import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import TextScreen from '../screens/TextScreen';
import AudioScreen from '../screens/AudioScreen';
import AnalyticsScreen from '../screens/AnalyticsScreen';
import colors from '../theme/colors';

const Stack = createNativeStackNavigator();

const navTheme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, background: colors.bg, text: colors.text },
};

export default function Navigation() {
  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Emotional AI' }} />
        <Stack.Screen name="Text" component={TextScreen} options={{ title: 'Text Model' }} />
        <Stack.Screen name="Audio" component={AudioScreen} options={{ title: 'Audio Model' }} />
        <Stack.Screen name="Analytics" component={AnalyticsScreen} options={{ title: 'Analytics' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
