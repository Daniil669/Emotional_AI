import { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, Pressable,
ActivityIndicator } from 'react-native';
import colors from '../theme/colors';
import { getAnalytics } from '../utils/api';
import StatCard from '../components/StatCard';

function fmtPct(v) {
  if (v === null || v === undefined) return '—';
  return `${(v * 100).toFixed(1)}%`;
}
function fmtNum(v) {
  if (v === null || v === undefined) return '—';
  return Number(v).toLocaleString();
}
function fmtMs(v) {
  if (v === null || v === undefined) return '—';
  return `${Math.round(v)} ms`;
}
function Pill({ label, active, onPress, style }) {
  return (
    <Pressable onPress={onPress} style={[styles.pill, active && styles.pillActive, style]}>
      <Text style={[styles.pillText, active && styles.pillTextActive]}>{label}</Text>
    </Pressable>
  );
}

export default function AnalyticsScreen() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // simple filter state
  const [days, setDays] = useState(30);
  const [modality, setModality] = useState(null); // null  text  audio
  const [correctGte, setCorrectGte] = useState(4);
  const [incorrectLte, setIncorrectLte] = useState(2);
  const [highConf, setHighConf] = useState(0.8);

  const load = useCallback(async () => {
    setErr(null);
    try {
      const res = await getAnalytics({
        days,
        modality,
        correct_gte: correctGte,
        incorrect_lte: incorrectLte,
        high_conf_thr: highConf,
      });
      setData(res);
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }, [days, modality, correctGte, incorrectLte, highConf]);

  useEffect(() => { load(); }, [load]);
  const onRefresh = useCallback(async () => { setRefreshing(true); await load(); setRefreshing(false); }, [load]);

  if (!data && !err) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text style={{ color: colors.subtext, marginTop: 8 }}>Loading analytics…</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.wrap}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      contentContainerStyle={{ paddingBottom: 28 }}
    >
      {/* Filters */}
      <Text style={styles.h1}>Analytics</Text>
      <View style={styles.row}>
        <Pill label="7d"   active={days===7}  onPress={() => setDays(7)} />
        <Pill label="30d"  active={days===30} onPress={() => setDays(30)} style={{ marginLeft: 8 }} />
        <Pill label="All"  active={days===0}  onPress={() => setDays(0)} style={{ marginLeft: 8 }} />
      </View>
      <View style={[styles.row, { marginTop: 8 }]}>
        <Pill label="All"    active={modality===null}   onPress={() => setModality(null)} />
        <Pill label="Text"   active={modality==='text'} onPress={() => setModality('text')} style={{ marginLeft: 8 }} />
        <Pill label="Audio"  active={modality==='audio'} onPress={() => setModality('audio')} style={{ marginLeft: 8 }} />
      </View>
      <View style={[styles.row, { marginTop: 8 }]}>
        <Pill label="Strict (5⭐=Correct)" active={correctGte===5 && incorrectLte===2}
              onPress={() => { setCorrectGte(5); setIncorrectLte(2); }} />
        <Pill label="Default (≥4 ok)" active={correctGte===4 && incorrectLte===2}
              onPress={() => { setCorrectGte(4); setIncorrectLte(2); }} style={{ marginLeft: 8 }} />
        <Pill label="Moderate (≥3 ok)" active={correctGte===3 && incorrectLte===1}
              onPress={() => { setCorrectGte(3); setIncorrectLte(1); }} style={{ marginLeft: 8 }} />
      </View>
      <View style={[styles.row, { marginTop: 8 }]}>
        <Pill label="HighConf 0.8" active={highConf===0.8} onPress={() => setHighConf(0.8)} />
        <Pill label="0.9" active={highConf===0.9} onPress={() => setHighConf(0.9)} style={{ marginLeft: 8 }} />
        <Pill label="0.7" active={highConf===0.7} onPress={() => setHighConf(0.7)} style={{ marginLeft: 8 }} />
      </View>

      {err ? (
        <Text style={styles.error}>Error: {err}</Text>
      ) : (
        <>
          {/* Overview */}
          <Text style={styles.h2}>Overview</Text>
          <View style={styles.grid2}>
            <StatCard title="Total Predictions" value={fmtNum(data.overall.total_predictions)} />
            <StatCard title="Feedback Coverage" value={fmtPct(data.overall.feedback_rate)} subtitle={`${fmtNum(data.overall.total_with_feedback)} with feedback`} />
          </View>

          {/* Modality totals */}
          <View style={[styles.grid2, { marginTop: 12 }]}>
            <StatCard title="Text total"  value={fmtNum(data.totals_by_modality.text)} />
            <StatCard title="Audio total" value={fmtNum(data.totals_by_modality.audio)} />
          </View>

          {/* Comparison (audio - text) */}
          {data.comparison && (
            <>
              <Text style={styles.h2}>Audio vs Text (Δ = audio − text)</Text>
              <View style={styles.grid2}>
                <StatCard title="Accuracy Δ" value={fmtPct(data.comparison.accuracy_delta)} />
                <StatCard title="Avg Confidence Δ" value={data.comparison.avg_confidence_delta?.toFixed(3) ?? '—'} />
              </View>
              <View style={[styles.grid2, { marginTop: 12 }]}>
                <StatCard title="Feedback Rate Δ" value={fmtPct(data.comparison.feedback_rate_delta)} />
                <StatCard title="Avg Proc Time Δ" value={fmtMs(data.comparison.avg_processing_ms_delta)} />
              </View>
              <View style={[styles.grid2, { marginTop: 12 }]}>
                <StatCard title="High-Conf Share Δ" value={fmtPct(data.comparison.high_conf_share_delta)} />
                <StatCard title="Avg Stars Δ" value={data.comparison.avg_stars_delta?.toFixed(2) ?? '—'} />
              </View>
            </>
          )}

          {/* Per-modality summaries */}
          <Text style={styles.h2}>Per Modality</Text>
          {['text', 'audio'].map((m) => {
            const s = data.modality_summaries?.[m];
            if (!s) return null;
            return (
              <View key={m} style={styles.block}>
                <Text style={styles.h3}>{m.toUpperCase()}</Text>
                <View style={styles.grid2}>
                  <StatCard title="Accuracy (by feedback)" value={fmtPct(s.accuracy_by_feedback.accuracy)} subtitle={`${s.accuracy_by_feedback.correct}/${s.accuracy_by_feedback.denominator} marked correct`} />
                  <StatCard title="Feedback Rate" value={fmtPct(s.feedback_rate)} subtitle={`${fmtNum(s.with_feedback)}/${fmtNum(s.total)}`} />
                </View>
                <View style={[styles.grid2, { marginTop: 12 }]}>
                  <StatCard title="Avg Confidence" value={s.avg_confidence?.toFixed(3) ?? '—'} />
                  <StatCard title="High-Conf Share" value={fmtPct(s.high_conf_share)} />
                </View>
                <View style={[styles.grid2, { marginTop: 12 }]}>
                  <StatCard title="Avg Stars" value={s.avg_stars?.toFixed(2) ?? '—'} />
                  <StatCard title="Avg Processing" value={fmtMs(s.avg_processing_ms)} />
                </View>
              </View>
            );
          })}

          {/* Per-emotion table */}
          <Text style={styles.h2}>Per Emotion</Text>
          <View style={styles.table}>
            <View style={[styles.tr, styles.trHead]}>
              <Text style={[styles.th, {flex: 1.2}]}>Label</Text>
              <Text style={[styles.th, {flex: 0.7, textAlign: 'right'}]}>Count</Text>
              <Text style={[styles.th, {flex: 1, textAlign: 'right'}]}>Acc.</Text>
              <Text style={[styles.th, {flex: 1, textAlign: 'right'}]}>Avg★</Text>
              <Text style={[styles.th, {flex: 1, textAlign: 'right'}]}>AvgConf</Text>
            </View>
             {data.by_emotion?.map((item) => (
                <View key={item.label} style={styles.tr}>
                <Text style={[styles.td, {flex: 1.2}]}>{item.label}</Text>
                <Text style={[styles.td, {flex: 0.7, textAlign: 'right'}]}>{fmtNum(item.count)}</Text>
                <Text style={[styles.td, {flex: 1, textAlign: 'right'}]}>
                {fmtPct(item.accuracy_by_feedback.accuracy)}
                </Text>
                <Text style={[styles.td, {flex: 1, textAlign: 'right'}]}>
                    {item.avg_stars?.toFixed(2) ?? '—'}
                </Text>
                <Text style={[styles.td, {flex: 1, textAlign: 'right'}]}>
                    {item.avg_confidence?.toFixed(3) ?? '—'}
                </Text>
                </View>
            ))}
          </View>

          {/* Extras */}
          <Text style={styles.h2}>Stability / Misc</Text>
          <View style={styles.grid2}>
            <StatCard title="Duplicate Inputs" value={fmtNum(data.duplicates.groups)} subtitle="groups" />
            <StatCard title="Label Disagreement" value={fmtPct(data.duplicates.disagreement_rate)} />
          </View>
          <View style={[styles.grid2, { marginTop: 12 }]}>
            <StatCard title="Text Languages" value={fmtNum(data.language_stats?.reduce((s,x)=>s+x.count,0) || 0)} subtitle={`${data.language_stats?.slice(0,3).map(x=>x.lang).join(', ') || '—'}`} />
            <StatCard title="Avg Audio Dur." value={`${data.audio_stats?.avg_duration_sec ? data.audio_stats.avg_duration_sec.toFixed(2) : '—'} s`} subtitle={`SR ${data.audio_stats?.avg_sample_rate ? Math.round(data.audio_stats.avg_sample_rate) : '—'}`} />
          </View>

          {/* Timeseries (simple textual summary) */}
          <Text style={styles.h2}>Activity (Daily)</Text>
          <Text style={styles.smallNote}>
            Showing {data.timeseries?.length || 0} days. Recent:{' '}
            {data.timeseries?.slice(-5).map(t => `${t.day}:${t.count}`).join('  ·  ') || '—'}
          </Text>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg, paddingHorizontal: 16, paddingTop: 10 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 26, fontWeight: '800', marginBottom: 8 },
  h2: { color: colors.text, fontSize: 18, fontWeight: '700', marginTop: 18, marginBottom: 8 },
  h3: { color: colors.text, fontSize: 16, fontWeight: '700', marginBottom: 10 },
  row: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center'},
  grid2: { flexDirection: 'row', justifyContent: 'space-between' },
  block: { marginTop: 8 },
  error: { color: colors.danger, marginTop: 10 },
  pill: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 999, paddingVertical: 6, paddingHorizontal: 12,
    backgroundColor: colors.card,
  },
  pillActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  pillText: { color: colors.subtext, fontSize: 12 },
  pillTextActive: { color: '#fff' },
  table: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 12, overflow: 'hidden', backgroundColor: colors.card,
  },
  tr: { flexDirection: 'row', paddingVertical: 10, paddingHorizontal: 12, borderTopWidth: 1, borderTopColor: colors.border },
  trHead: { backgroundColor: '#15151f', borderTopWidth: 0 },
  th: { color: colors.subtext, fontSize: 12, fontWeight: '700' },
  td: { color: colors.text, fontSize: 13 },
  smallNote: { color: colors.subtext, fontSize: 12, marginBottom: 8 },
});
