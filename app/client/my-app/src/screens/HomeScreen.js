import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import ButtonPrimary from '../components/ButtonPrimary';
import colors from '../theme/colors';

export default function HomeScreen({ navigation }) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Emotional AI</Text>
      <Text style={styles.subtitle}>Choose the AI model to test emotions</Text>

      <View style={styles.btnCol}>
        <ButtonPrimary title="Text model" onPress={() => navigation.navigate('Text')} />
        <ButtonPrimary title="Audio model" onPress={() => navigation.navigate('Audio')} style={{ marginTop: 14 }} />
        <ButtonPrimary title="Analytics"  onPress={() => navigation.navigate('Analytics')} style={{ marginTop: 14 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20, backgroundColor: colors.bg },
  title: { color: colors.text, fontSize: 28, fontWeight: '800', marginBottom: 8 },
  subtitle: { color: colors.subtext, fontSize: 14, marginBottom: 28 },
  btnCol: { width: '80%', alignItems: 'center' },
});
