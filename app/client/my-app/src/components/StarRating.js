import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import colors from '../theme/colors';

export default function StarRating({ value, onChange }) {
  return (
    <View style={styles.row}>
      {[1,2,3,4,5].map((n) => (
        <TouchableOpacity key={n} onPress={() => onChange(n)} style={styles.starBtn}>
          <Text style={[styles.star, value >= n ? styles.on : styles.off]}>★</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 },
  starBtn: { padding: 2 },
  star: { fontSize: 28 },
  on: { color: colors.primary },
  off: { color: '#555' },
});
