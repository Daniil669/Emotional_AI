import axios from 'axios';
import { API_BASE } from '../config';
import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';

const api = axios.create({ baseURL: API_BASE, timeout: 20000 });

// Text
export async function postText(text, lang = 'en') {
  const { data } = await api.post('/text', { text, lang });
  return data; // { prediction_id, top_label, confidence, scores, ... }
}


// Audio
export async function postAudio(fileUri) {
  const info = await FileSystem.getInfoAsync(fileUri, { size: true });
  if (!info.exists) throw new Error(`Audio file not found at ${fileUri}`);

  const rawName = (fileUri.split('/').pop() || '').split('?')[0];
  const ext = (rawName.split('.').pop() || '').toLowerCase();

  let name = rawName || `recording.${ext || 'm4a'}`;
  let type = 'application/octet-stream';
  if (ext === 'wav') type = 'audio/wav';
  else if (ext === 'caf') type = 'audio/x-caf';
  else if (ext === '3gp' || ext === '3gpp') type = 'audio/3gpp';
  else if (ext === 'aac') type = 'audio/aac';
  else if (ext === 'mp4' || ext === 'm4a') type = Platform.OS === 'ios' ? 'audio/m4a' : 'audio/mp4';
  else { name = 'recording.m4a'; type = Platform.OS === 'ios' ? 'audio/m4a' : 'audio/mp4'; }

  const form = new FormData();
  form.append('file', { uri: fileUri, name, type });

  const resp = await fetch(`${API_BASE}/audio`, {
    method: 'POST',
    headers: { Accept: 'application/json' }, // let fetch set boundary
    body: form,
  });

  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(`Server ${resp.status}: ${msg}`);
  }
  try { return await resp.json(); } catch { return {}; }
}




// Feedback
export async function postFeedback(predictionId, stars, comment) {
  const { data } = await api.post('/feedback', {
    prediction_id: predictionId,
    stars,
    comment,
  });
  return data; // { ok: true, feedback_id }
}


// Analytics
export async function getAnalytics({
  days = 30,
  modality = null,// text audio null
  correct_gte = 4,
  incorrect_lte = 2,
  high_conf_thr = 0.8,
} = {}) {
  const params = new URLSearchParams();
  params.append('days', String(days));
  if (modality) params.append('modality', modality);
  params.append('correct_gte', String(correct_gte));
  params.append('incorrect_lte', String(incorrect_lte));
  params.append('high_conf_thr', String(high_conf_thr));

  const { data } = await api.get(`/analytics?${params.toString()}`);
  return data;
}

