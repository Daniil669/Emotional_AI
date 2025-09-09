import { View, Text, StyleSheet } from 'react-native';
import colors from '../theme/colors';

export default function ProbabilityList({ scores }) {
  if (!scores) return null;
  const items = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7);
  return (
    <View style={styles.wrap}>
      {items.map(([label, p]) => (
        <View style={styles.row} key={label}>
          <Text style={styles.label}>{label}</Text>
          <Text style={styles.value}>{(p * 100).toFixed(1)}%</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 6, padding: 12, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  label: { color: colors.text, fontSize: 14 },
  value: { color: colors.subtext, fontSize: 14 }
});
