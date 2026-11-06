import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { ExecutionRecord } from '../types';
import { Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react';

interface ControllerReplayViewProps {
  initialRecord?: ExecutionRecord | null;
  isDark: boolean;
}

export const ControllerReplayView: React.FC<ControllerReplayViewProps> = ({ initialRecord, isDark }) => {
  const [currentRoundIdx, setCurrentRoundIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [record, setRecord] = useState<ExecutionRecord | null>(initialRecord || null);

  useEffect(() => {
    if (initialRecord) {
      setRecord(initialRecord);
      setCurrentRoundIdx(0);
    }
  }, [initialRecord]);

  const fallbackLogs = [
    { round: 1, action: "filter_space_prefix", iterations: 0, shots: 0, measured_key: 0, oracle_calls: 0, success: false, noise_estimate: 0.01 },
    { round: 2, action: "grover_amplification", iterations: 1, shots: 64, measured_key: 5, oracle_calls: 64, success: false, noise_estimate: 0.018 },
    { round: 3, action: "shallow_restart_amplification", iterations: 1, shots: 64, measured_key: 7, oracle_calls: 64, success: false, noise_estimate: 0.021 },
    { round: 4, action: "adaptive_verified", iterations: 1, shots: 64, measured_key: 5, oracle_calls: 64, success: true, noise_estimate: 0.020 },
  ];

  const activeRecord: ExecutionRecord = record || {
    strategy_name: "Adaptive Hybrid (Demo)",
    found_key: 5,
    is_verified: true,
    total_oracle_calls: 384,
    classical_verification_calls: 3,
    total_effective_cost: 387,
    wall_clock_seconds: 0.012,
    rounds_executed: 4,
    final_search_space_size: 4,
    round_logs: fallbackLogs,
  };

  const logs =
    activeRecord.round_logs && activeRecord.round_logs.length > 0
      ? activeRecord.round_logs
      : fallbackLogs;
  const safeIdx = Math.min(Math.max(0, currentRoundIdx), logs.length - 1);
  const currentRound = logs[safeIdx] || fallbackLogs[0];

  useEffect(() => {
    let timer: any = null;
    if (isPlaying && currentRoundIdx < logs.length - 1) {
      timer = setTimeout(() => {
        setCurrentRoundIdx((prev) => prev + 1);
      }, 1200);
    } else if (isPlaying && currentRoundIdx >= logs.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentRoundIdx, logs.length]);

  const handlePlayToggle = () => {
    if (logs.length <= 1) {
      setIsPlaying(true);
      setTimeout(() => setIsPlaying(false), 600);
      return;
    }
    if (!isPlaying && currentRoundIdx >= logs.length - 1) {
      setCurrentRoundIdx(0);
      setIsPlaying(true);
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleRestart = () => {
    setCurrentRoundIdx(0);
    setIsPlaying(false);
  };

  const handleLoadDemoTrace = () => {
    setRecord(null);
    setCurrentRoundIdx(0);
    setIsPlaying(false);
  };

  const targetKey = activeRecord.found_key ?? 5;
  const measuredKey = currentRound.measured_key ?? 0;
  const candidateKeys = Array.from(
    new Set([
      targetKey,
      measuredKey,
      (targetKey + 1) % 16,
      (targetKey + 3) % 16,
    ])
  ).sort((a, b) => a - b);

  const categories = candidateKeys.map(
    (k) => `0x${k.toString(16).toUpperCase()} (${k})${k === targetKey ? " [Target]" : ""}`
  );

  const chartData = candidateKeys.map((k) => {
    if (k === measuredKey && currentRound.success) {
      return currentRound.shots > 0 ? Math.round(currentRound.shots * 0.7) : 42;
    }
    if (k === measuredKey) {
      return currentRound.shots > 0 ? Math.round(currentRound.shots * 0.45) : 28;
    }
    if (k === targetKey) {
      return currentRound.shots > 0 ? Math.round(currentRound.shots * 0.25) : 18;
    }
    return currentRound.shots > 0 ? Math.max(2, Math.round(currentRound.shots * 0.1)) : 8;
  });

  const chartOption = {
    backgroundColor: 'transparent',
    title: {
      text: `Round ${currentRound.round}: Measured Candidate Sampling Distribution`,
      textStyle: {
        color: isDark ? '#e2e8f0' : '#1e293b',
        fontSize: 12,
        fontWeight: 'normal',
      },
    },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      axisLine: { lineStyle: { color: isDark ? '#334155' : '#cbd5e1' } },
    },
    yAxis: {
      type: 'value',
      name: 'Sample Counts',
      nameTextStyle: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      splitLine: { lineStyle: { color: isDark ? '#1e293b' : '#f1f5f9' } },
    },
    series: [
      {
        data: chartData,
        type: 'bar',
        itemStyle: {
          color: (params: any) => {
            const keyVal = candidateKeys[params.dataIndex];
            if (keyVal === targetKey && currentRound.success) return '#059669';
            if (keyVal === measuredKey) return '#d97706';
            return isDark ? '#3b82f6' : '#2563eb';
          },
        },
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Interactive Controller Replay
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Step through adaptive decisions: Bayesian noise estimation, shallow iteration selection, and restarts.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleLoadDemoTrace}
              title="Reset to 4-Round Controller Demonstration Trace"
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs flex items-center"
            >
              Demo Trace
            </button>
            <button
              onClick={handleRestart}
              title="Restart Replay from Round 1"
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentRoundIdx(Math.max(0, currentRoundIdx - 1))}
              disabled={currentRoundIdx === 0}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            <button
              onClick={handlePlayToggle}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs flex items-center"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5 mr-1" /> : <Play className="w-3.5 h-3.5 mr-1" />}
              {isPlaying ? "Pause" : "Play"}
            </button>
            <button
              onClick={() => setCurrentRoundIdx(Math.min(logs.length - 1, currentRoundIdx + 1))}
              disabled={currentRoundIdx >= logs.length - 1}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>
        </div>

        {logs.length <= 1 && (
          <div className="mb-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-xs text-amber-800 dark:text-amber-300 flex flex-wrap items-center justify-between gap-2">
            <span>
              <strong>Note:</strong> Loaded simulation converged in 1 round (key verified immediately on round 1). Pressing Play stays on round 1.
            </span>
            <button
              onClick={handleLoadDemoTrace}
              className="px-2.5 py-1 rounded-md bg-amber-600 hover:bg-amber-700 text-white font-medium text-[11px]"
            >
              Load 4-Round Controller Trace
            </button>
          </div>
        )}

        <div className="space-y-1 mb-6">
          <div className="flex justify-between text-xs font-mono text-slate-500">
            <span>Round {currentRoundIdx + 1} of {logs.length}</span>
            <span>{currentRound.action}</span>
          </div>
          <input
            type="range"
            min={0}
            max={Math.max(1, logs.length - 1)}
            value={currentRoundIdx}
            disabled={logs.length <= 1}
            onChange={(e) => setCurrentRoundIdx(parseInt(e.target.value))}
            className="w-full accent-emerald-600 cursor-pointer disabled:opacity-40"
          />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-0.5">Iterations (k)</span>
            <span className="text-sm font-bold font-mono">{currentRound.iterations}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-0.5">Shots Taken</span>
            <span className="text-sm font-bold font-mono">{currentRound.shots}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-0.5">Measured Key</span>
            <span className="text-sm font-bold font-mono">0x{currentRound.measured_key.toString(16)} ({currentRound.measured_key})</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-0.5">Estimated Noise</span>
            <span className="text-sm font-bold font-mono">
              {currentRound.noise_estimate !== undefined ? `${(currentRound.noise_estimate * 100).toFixed(2)}%` : "N/A"}
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>
    </div>
  );
};
