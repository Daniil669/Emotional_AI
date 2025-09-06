import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { Audio } from 'expo-av';
import colors from '../theme/colors';
import ButtonPrimary from '../components/ButtonPrimary';
import { postAudio } from '../utils/api';
import FeedbackModal from '../components/FeedbackModal';
import { AUDIO_MAX_SECONDS, AUDIO_MODEL_NAME } from '../config';

export default function AudioScreen() {
  const [permission, requestPermission] = Audio.usePermissions();
  const recRef = useRef(null);
  const autoStopRef = useRef(null);        // ← keep timeout id here

  const [recording, setRecording] = useState(null);
  const [isPaused, setPaused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lastUri, setLastUri] = useState(null);

  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [predictionId, setPredictionId] = useState(null);
  const [scores, setScores] = useState(null);

  const clearAutoStop = () => {
    if (autoStopRef.current) {
      clearTimeout(autoStopRef.current);
      autoStopRef.current = null;
    }
  };

  const hardResetRecorder = () => {
    clearAutoStop();
    recRef.current = null;
    setRecording(null);
    setPaused(false);
  };

  const resetAfterFeedback = () => {
    setFeedbackVisible(false);
    setPredictionId(null);
    setScores(null);
    hardResetRecorder();
    setLastUri(null);
  };

  useEffect(() => {
    if (!permission) requestPermission();
  }, [permission]);

  const startRecording = async () => {
    try {
      if (!permission?.granted) {
        const p = await requestPermission();
        if (!p?.granted) return;
      }
      // fresh session
      hardResetRecorder();
      setLastUri(null);

      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      recRef.current = recording;
      setRecording(recording);
      setPaused(false);

      // set fresh 30s auto-stop
      clearAutoStop();
      autoStopRef.current = setTimeout(async () => {
        if (recRef.current) {
          try { await stopRecording(); } catch {}
        }
      }, AUDIO_MAX_SECONDS * 1000);
    } catch (e) {
      Alert.alert('Recording error', 'Could not start recording.');
    }
  };

  const pauseRecording = async () => {
    if (!recRef.current || isPaused) return;
    try {
      await recRef.current.pauseAsync();
      setPaused(true);
    } catch {}
  };

  const resumeRecording = async () => {
    if (!recRef.current || !isPaused) return;
    try {
      await recRef.current.startAsync();
      setPaused(false);
    } catch {}
  };

  const stopRecording = async () => {
    if (!recRef.current) return null;
    try {
      clearAutoStop();
      await recRef.current.stopAndUnloadAsync();
      const uri = recRef.current.getURI();
      hardResetRecorder();
      setLastUri(uri);
      return uri;
    } catch {
      hardResetRecorder();
      return null;
    }
  };

  const send = async () => {
    setLoading(true);
    try {
      const uri = recRef.current ? await stopRecording() : lastUri;
      if (!uri) return;
      const res = await postAudio(uri);
      setPredictionId(res.prediction_id);
      setScores(res.scores);
      setFeedbackVisible(true);
    } catch {
      Alert.alert('Upload error', 'Failed to send audio to the server.');
    } finally {
      setLoading(false);
    }
  };

  const canSend = !!recRef.current || !!lastUri;

  return (
    <View style={styles.wrap}>
      <Text style={styles.info}>
        Limit: {AUDIO_MAX_SECONDS}s • Model: {AUDIO_MODEL_NAME}
      </Text>

      <View style={styles.col}>
        {!recording ? (
          <ButtonPrimary title="Record" onPress={startRecording} />
        ) : (
          <>
            <ButtonPrimary
              title={isPaused ? 'Resume' : 'Pause'}
              onPress={isPaused ? resumeRecording : pauseRecording}
            />
            <ButtonPrimary title="Stop and Reset" onPress={stopRecording} style={{ marginTop: 12 }} />
          </>
        )}
        <ButtonPrimary
          title="Send"
          onPress={send}
          loading={loading}
          disabled={!canSend || loading}
          style={{ marginTop: 12, opacity: (!canSend || loading) ? 0.6 : 1 }}
        />
      </View>

      <FeedbackModal
        visible={feedbackVisible}
        onClose={resetAfterFeedback}
        onSubmitted={resetAfterFeedback}
        predictionId={predictionId}
        scores={scores}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, alignItems: 'center', padding: 20, backgroundColor: colors.bg },
  info: { color: colors.subtext, fontSize: 13, marginTop: 8, marginBottom: 24, textAlign: 'center' },
  col: { width: '80%', alignItems: 'center' }
});
