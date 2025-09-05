import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import colors from '../theme/colors';
import ButtonPrimary from '../components/ButtonPrimary';
import { postText } from '../utils/api';
import FeedbackModal from '../components/FeedbackModal';
import { TEXT_MAX, TEXT_MODEL_NAME } from '../config';

export default function TextScreen() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [predictionId, setPredictionId] = useState(null);
  const [scores, setScores] = useState(null);

  const resetAfterFeedback = () => {
   setFeedbackVisible(false);
   setPredictionId(null);
   setScores(null);
   setText('');              // clear input so user can send a new message
   };

  const send = async () => {
    if (!text.trim()) return;
    if (text.length > TEXT_MAX) return;
    setLoading(true);
    try {
      const res = await postText(text.trim(), 'en');
      setPredictionId(res.prediction_id);
      setScores(res.scores);
      setFeedbackVisible(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.select({ ios: 'padding', android: undefined })} style={{ flex: 1 }}>
      <View style={styles.wrap}>
        <Text style={styles.info}>
          Limit: {TEXT_MAX} characters • Model: {TEXT_MODEL_NAME}
        </Text>

        <View style={styles.inputRow}>
          <TextInput
            value={text}
            onChangeText={setText}
            placeholder="Type your message…"
            placeholderTextColor={colors.subtext}
            style={styles.input}
            maxLength={TEXT_MAX}
            multiline
          />
          <ButtonPrimary title="Send" onPress={send} loading={loading} />
        </View>

        <FeedbackModal
          visible={feedbackVisible}
          onClose={resetAfterFeedback}
          onSubmitted={resetAfterFeedback}
          predictionId={predictionId}
          scores={scores}
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, padding: 16, gap: 16, backgroundColor: colors.bg },
  info: { color: colors.subtext, fontSize: 13, textAlign: 'center', marginTop: 8 },
  inputRow: { gap: 10 },
  input: {
    minHeight: 120,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 12,
    color: colors.text,
    backgroundColor: colors.card
  },
});
