import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import colors from '../theme/colors';

export default function ButtonPrimary({ title, onPress, disabled, loading, style }) {
  return (
    <TouchableOpacity
      style={[styles.btn, disabled ? styles.disabled : null, style]}
      onPress={onPress}
      activeOpacity={0.85}
      disabled={disabled || loading}
    >
      {loading ? <ActivityIndicator /> : <Text style={styles.text}>{title}</Text>}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: colors.primary,
    paddingVertical: 14,
    paddingHorizontal: 18,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    minWidth: 140,
  },
  text: { color: colors.accent, fontSize: 16, fontWeight: '700' },
  disabled: { opacity: 0.6 }
});
