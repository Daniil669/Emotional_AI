// import React, { useEffect, useRef, useState } from 'react';
// import { View, Text, StyleSheet, Alert } from 'react-native';
// import { Audio } from 'expo-av';
// import colors from '../theme/colors';
// import ButtonPrimary from '../components/ButtonPrimary';
// import { postAudio } from '../utils/api';
// import FeedbackModal from '../components/FeedbackModal';
// import { AUDIO_MAX_SECONDS, AUDIO_MODEL_NAME } from '../config';

// export default function AudioScreen() {
//   const [permission, requestPermission] = Audio.usePermissions();
//   const recRef = useRef(null);
//   const autoStopRef = useRef(null);        // ← keep timeout id here

//   const [recording, setRecording] = useState(null);
//   const [isPaused, setPaused] = useState(false);
//   const [loading, setLoading] = useState(false);
//   const [lastUri, setLastUri] = useState(null);

//   const [feedbackVisible, setFeedbackVisible] = useState(false);
//   const [predictionId, setPredictionId] = useState(null);
//   const [scores, setScores] = useState(null);

//   const clearAutoStop = () => {
//     if (autoStopRef.current) {
//       clearTimeout(autoStopRef.current);
//       autoStopRef.current = null;
//     }
//   };

//   const hardResetRecorder = () => {
//     clearAutoStop();
//     recRef.current = null;
//     setRecording(null);
//     setPaused(false);
//   };

//   const resetAfterFeedback = () => {
//     setFeedbackVisible(false);
//     setPredictionId(null);
//     setScores(null);
//     hardResetRecorder();
//     setLastUri(null);
//   };

//   useEffect(() => {
//     if (!permission) requestPermission();
//   }, [permission]);

//   const startRecording = async () => {
//     try {
//       if (!permission?.granted) {
//         const p = await requestPermission();
//         if (!p?.granted) return;
//       }
//       // fresh session
//       hardResetRecorder();
//       setLastUri(null);

//       await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
//       const { recording } = await Audio.Recording.createAsync(
//         Audio.RecordingOptionsPresets.HIGH_QUALITY
//       );
//       recRef.current = recording;
//       setRecording(recording);
//       setPaused(false);

//       // set fresh 30s auto-stop
//       clearAutoStop();
//       autoStopRef.current = setTimeout(async () => {
//         if (recRef.current) {
//           try { await stopRecording(); } catch {}
//         }
//       }, AUDIO_MAX_SECONDS * 1000);
//     } catch (e) {
//       Alert.alert('Recording error', 'Could not start recording.');
//     }
//   };

//   const pauseRecording = async () => {
//     if (!recRef.current || isPaused) return;
//     try {
//       await recRef.current.pauseAsync();
//       setPaused(true);
//     } catch {}
//   };

//   const resumeRecording = async () => {
//     if (!recRef.current || !isPaused) return;
//     try {
//       await recRef.current.startAsync();
//       setPaused(false);
//     } catch {}
//   };

//   const stopRecording = async () => {
//     if (!recRef.current) return null;
//     try {
//       clearAutoStop();
//       await recRef.current.stopAndUnloadAsync();
//       const uri = recRef.current.getURI();
//       hardResetRecorder();
//       setLastUri(uri);
//       return uri;
//     } catch {
//       hardResetRecorder();
//       return null;
//     }
//   };

//   const send = async () => {
//     setLoading(true);
//     try {
//       const uri = recRef.current ? await stopRecording() : lastUri;
//       if (!uri) return;
//       const res = await postAudio(uri);
//       setPredictionId(res.prediction_id);
//       setScores(res.scores);
//       setFeedbackVisible(true);
//     } catch {
//       Alert.alert('Upload error', 'Failed to send audio to the server.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const canSend = !!recRef.current || !!lastUri;

//   return (
//     <View style={styles.wrap}>
//       <Text style={styles.info}>
//         Limit: {AUDIO_MAX_SECONDS}s • Model: {AUDIO_MODEL_NAME}
//       </Text>

//       <View style={styles.col}>
//         {!recording ? (
//           <ButtonPrimary title="Record" onPress={startRecording} />
//         ) : (
//           <>
//             <ButtonPrimary
//               title={isPaused ? 'Resume' : 'Pause'}
//               onPress={isPaused ? resumeRecording : pauseRecording}
//             />
//             <ButtonPrimary title="Stop and Reset" onPress={stopRecording} style={{ marginTop: 12 }} />
//           </>
//         )}
//         <ButtonPrimary
//           title="Send"
//           onPress={send}
//           loading={loading}
//           disabled={!canSend || loading}
//           style={{ marginTop: 12, opacity: (!canSend || loading) ? 0.6 : 1 }}
//         />
//       </View>

//       <FeedbackModal
//         visible={feedbackVisible}
//         onClose={resetAfterFeedback}
//         onSubmitted={resetAfterFeedback}
//         predictionId={predictionId}
//         scores={scores}
//       />
//     </View>
//   );
// }

// const styles = StyleSheet.create({
//   wrap: { flex: 1, alignItems: 'center', padding: 20, backgroundColor: colors.bg },
//   info: { color: colors.subtext, fontSize: 13, marginTop: 8, marginBottom: 24, textAlign: 'center' },
//   col: { width: '80%', alignItems: 'center' }
// });
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Alert, Platform } from 'react-native';
import { useAudioRecorder, AudioModule, RecordingPresets } from 'expo-audio';
import colors from '../theme/colors';
import ButtonPrimary from '../components/ButtonPrimary';
import { postAudio } from '../utils/api';
import FeedbackModal from '../components/FeedbackModal';
import { AUDIO_MAX_SECONDS, AUDIO_MODEL_NAME } from '../config';

export default function AudioScreen() {
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  
  const autoStopRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [lastUri, setLastUri] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

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
    setLastUri(null);
    setIsRecording(false);
    setIsPaused(false);
  };

  const resetAfterFeedback = () => {
    setFeedbackVisible(false);
    setPredictionId(null);
    setScores(null);
    hardResetRecorder();
  };

  useEffect(() => {
    // Request permissions on mount
    (async () => {
      const result = await AudioModule.requestRecordingPermissionsAsync();
      console.log('Permission result:', result);
    })();
  }, []);

  const startRecording = async () => {
    try {
      console.log('Starting recording...');
      const { granted } = await AudioModule.requestRecordingPermissionsAsync();
      console.log('Permission granted:', granted);
      
      if (!granted) {
        Alert.alert('Permission denied', 'Recording permission is required.');
        return;
      }

      hardResetRecorder();
      
      // Prepare the recording
      console.log('Preparing recording...');
      await audioRecorder.prepareToRecordAsync();
      console.log('Recording prepared');
      
      // Start recording
      console.log('Calling audioRecorder.record()...');
      audioRecorder.record();
      console.log('Record called');
      
      setIsRecording(true);

      // Set 30s auto-stop
      clearAutoStop();
      autoStopRef.current = setTimeout(async () => {
        console.log('Auto-stop triggered');
        if (isRecording) {
          try { 
            await stopRecording(); 
          } catch (e) {
            console.error('Auto-stop error:', e);
          }
        }
      }, AUDIO_MAX_SECONDS * 1000);
      
      console.log('Recording setup complete');
    } catch (e) {
      console.error('Recording error:', e);
      Alert.alert('Recording error', `Could not start recording: ${e.message}`);
      setIsRecording(false);
    }
  };

  const pauseRecording = async () => {
    if (!isRecording || isPaused) return;
    try {
      console.log('Pausing recording...');
      await audioRecorder.pause();
      setIsPaused(true);
      console.log('Recording paused');
    } catch (e) {
      console.error('Pause error:', e);
    }
  };

  const resumeRecording = async () => {
    if (!isPaused) return;
    try {
      console.log('Resuming recording...');
      audioRecorder.record();
      setIsPaused(false);
      console.log('Recording resumed');
    } catch (e) {
      console.error('Resume error:', e);
    }
  };

  const stopRecording = async () => {
  if (!isRecording) return null;
  try {
    console.log('Stopping recording...');
    clearAutoStop();
    const result = await audioRecorder.stop();
    console.log('Recording stopped, result:', result);
    
    // Extract the URI from the result object
    const uri = result?.url || result;
    console.log('URI:', uri);
    
    setLastUri(uri);
    setIsRecording(false);
    setIsPaused(false);
    return uri;
  } catch (e) {
    console.error('Stop error:', e);
    setIsRecording(false);
    setIsPaused(false);
    return null;
  }
};

  const send = async () => {
    setLoading(true);
    try {
      let uri = lastUri;
      if (isRecording) {
        uri = await stopRecording();
      }
      if (!uri) {
        Alert.alert('No recording', 'Please record audio first.');
        setLoading(false);
        return;
      }
      
      console.log('Sending audio:', uri);
      const res = await postAudio(uri);
      setPredictionId(res.prediction_id);
      setScores(res.scores);
      setFeedbackVisible(true);
    } catch (e) {
      console.error('Upload error:', e);
      Alert.alert('Upload error', `Failed to send audio: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const canSend = isRecording || !!lastUri;

  return (
    <View style={styles.wrap}>
      <Text style={styles.info}>
        Limit: {AUDIO_MAX_SECONDS}s • Model: {AUDIO_MODEL_NAME}
      </Text>
      
      {/* Debug info */}
      <Text style={styles.debug}>
        Recording: {isRecording ? 'YES' : 'NO'} | 
        Paused: {isPaused ? 'YES' : 'NO'} | 
        Has URI: {lastUri ? 'YES' : 'NO'}
      </Text>

      <View style={styles.col}>
        {!isRecording ? (
          <ButtonPrimary title="Record" onPress={startRecording} />
        ) : (
          <>
            <ButtonPrimary
              title={isPaused ? 'Resume' : 'Pause'}
              onPress={isPaused ? resumeRecording : pauseRecording}
            />
            <ButtonPrimary 
              title="Stop and Reset" 
              onPress={stopRecording} 
              style={{ marginTop: 12 }} 
            />
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
  debug: { color: colors.subtext, fontSize: 11, marginBottom: 12, textAlign: 'center' },
  col: { width: '80%', alignItems: 'center' }
});