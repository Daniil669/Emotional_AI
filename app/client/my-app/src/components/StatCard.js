import { View, Text, StyleSheet } from 'react-native';
import colors from '../theme/colors';

export default function StatCard({ title, value, subtitle, style }) {
  return (
    <View style={[styles.card, style]}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.value}>{value ?? '—'}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 14,
    padding: 14,
    minWidth: '46%',
  },
  title: { color: colors.subtext, fontSize: 12, marginBottom: 6 },
  value: { color: colors.text, fontSize: 18, fontWeight: '700' },
  subtitle: { color: colors.subtext, fontSize: 12, marginTop: 6 },
});
