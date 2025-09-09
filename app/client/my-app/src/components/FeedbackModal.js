import { useEffect, useState } from 'react';
import { Modal, View, Text, StyleSheet, TextInput } from 'react-native';
import ButtonPrimary from './ButtonPrimary';
import ProbabilityList from './ProbabilityList';
import StarRating from './StarRating';
import colors from '../theme/colors';
import { postFeedback } from '../utils/api';

export default function FeedbackModal({ visible, onClose, onSubmitted, predictionId, scores }) {
  const [stars, setStars] = useState(0);
  const [comment, setComment] = useState('');
  const [sending, setSending] = useState(false);

  // Reset fields each time modal opens OR prediction changes
  useEffect(() => {
    if (visible) {
      setStars(0);
      setComment('');
    }
  }, [visible, predictionId]);

  // Auto-close after 60s
  useEffect(() => {
    if (!visible) return;
    const t = setTimeout(() => {
      onSubmitted?.();
      onClose?.();
    }, 60000);
    return () => clearTimeout(t);
  }, [visible, onSubmitted, onClose]);

  const send = async () => {
    try {
      setSending(true);
      await postFeedback(predictionId, stars, comment.trim());
      onSubmitted?.();
      onClose?.();
    } finally {
      setSending(false);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Emotion probabilities</Text>
          <ProbabilityList scores={scores} />

          <Text style={[styles.title, { marginTop: 16 }]}>Your feedback</Text>
          <StarRating value={stars} onChange={setStars} />

          <TextInput
            value={comment}
            onChangeText={setComment}
            placeholder="Any comments?"
            placeholderTextColor={colors.subtext}
            style={styles.input}
            multiline
          />
          <ButtonPrimary title="Send feedback" onPress={send} loading={sending} />
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.55)', justifyContent: 'center', padding: 16 },
  card: { backgroundColor: colors.card, padding: 16, borderRadius: 16, gap: 12, borderWidth: 1, borderColor: colors.border },
  title: { color: colors.text, fontSize: 16, fontWeight: '700' },
  input: { minHeight: 70, borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 10, color: colors.text }
});
