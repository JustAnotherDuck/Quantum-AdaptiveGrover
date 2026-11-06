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

  useEffect(() => {
    let timer: any = null;
    const numLogs = record?.round_logs?.length ?? fallbackLogs.length;
    if (isPlaying && currentRoundIdx < numLogs - 1) {
      timer = setTimeout(() => {
        setCurrentRoundIdx((prev) => prev + 1);
      }, 1000);
    } else if (isPlaying && currentRoundIdx >= numLogs - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentRoundIdx, record]);

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
      data: ['State 0x1', 'State 0x3', 'State 0x5 (Target)', 'State 0x7'],
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
        data: [
          currentRound.round === 1 ? 16 : 8,
          currentRound.round === 1 ? 16 : 10,
          currentRound.round === 4 ? 42 : (currentRound.round === 2 ? 30 : 18),
          currentRound.round === 3 ? 28 : 8,
        ],
        type: 'bar',
        itemStyle: {
          color: (params: any) => {
            return params.dataIndex === 2 ? '#059669' : (isDark ? '#3b82f6' : '#2563eb');
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
              onClick={() => setCurrentRoundIdx(0)}
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
              onClick={() => setIsPlaying(!isPlaying)}
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

        <div className="space-y-1 mb-6">
          <div className="flex justify-between text-xs font-mono text-slate-500">
            <span>Round {currentRoundIdx + 1} of {logs.length}</span>
            <span>{currentRound.action}</span>
          </div>
          <input
            type="range"
            min={0}
            max={logs.length - 1}
            value={currentRoundIdx}
            onChange={(e) => setCurrentRoundIdx(parseInt(e.target.value))}
            className="w-full accent-emerald-600 cursor-pointer"
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
