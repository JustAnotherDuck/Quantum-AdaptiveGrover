import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';

interface AblationMatrixViewProps {
  isDark: boolean;
}

export const AblationMatrixView: React.FC<AblationMatrixViewProps> = ({ isDark }) => {
  const [noiseSetting, setNoiseSetting] = useState<'moderate' | 'high'>('moderate');

  const ablationsModerate = [
    { name: "Full Adaptive Hybrid (Proposed)", success: 99.2, cost: 214, oracleCalls: 192 },
    { name: "Ablation: No Filtering", success: 96.5, cost: 482, oracleCalls: 448 },
    { name: "Ablation: No Adaptivity", success: 82.0, cost: 840, oracleCalls: 780 },
    { name: "Ablation: No Noise-Awareness", success: 88.5, cost: 650, oracleCalls: 610 },
    { name: "Ablation: No Shallow Restart", success: 74.0, cost: 1120, oracleCalls: 1080 },
    { name: "Null Control (Random Guess)", success: 1.5, cost: 15000, oracleCalls: 15000 },
  ];

  const ablationsHigh = [
    { name: "Full Adaptive Hybrid (Proposed)", success: 88.4, cost: 620, oracleCalls: 576 },
    { name: "Ablation: No Filtering", success: 71.0, cost: 1850, oracleCalls: 1780 },
    { name: "Ablation: No Adaptivity", success: 42.5, cost: 4200, oracleCalls: 4100 },
    { name: "Ablation: No Noise-Awareness", success: 58.0, cost: 2600, oracleCalls: 2480 },
    { name: "Ablation: No Shallow Restart", success: 22.0, cost: 8900, oracleCalls: 8700 },
    { name: "Null Control (Random Guess)", success: 1.5, cost: 15000, oracleCalls: 15000 },
  ];

  const activeData = noiseSetting === 'moderate' ? ablationsModerate : ablationsHigh;

  const chartOption = {
    backgroundColor: 'transparent',
    title: {
      text: `Effective Cost by Ablation Lever (${noiseSetting === 'moderate' ? 'Moderate Noise: 2% error' : 'High Noise: 8% error'})`,
      textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 13, fontWeight: 'bold' },
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 60, right: 30, bottom: 85, left: 65 },
    xAxis: {
      type: 'category',
      data: activeData.map((d) => d.name.replace("Ablation: ", "")),
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b',
        fontSize: 10,
        rotate: 20,
        interval: 0,
      },
      axisLine: { lineStyle: { color: isDark ? '#334155' : '#cbd5e1' } },
    },
    yAxis: {
      type: 'log',
      name: 'Total Effective Cost (Log Scale)',
      nameTextStyle: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 11 },
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      splitLine: { lineStyle: { color: isDark ? '#1e293b' : '#f1f5f9' } },
    },
    series: [
      {
        name: 'Effective Cost',
        type: 'bar',
        data: activeData.map((d) => d.cost),
        itemStyle: {
          color: (params: any) => {
            if (params.dataIndex === 0) return '#009E73';
            if (params.dataIndex === 5) return '#999999';
            return '#0072B2';
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
              Multi-Lever Ablation Analysis
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Isolates the marginal contribution of filtering, dynamic iteration selection, noise awareness, and restarts.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setNoiseSetting('moderate')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                noiseSetting === 'moderate'
                  ? 'bg-emerald-50 dark:bg-emerald-950 border-emerald-500 text-emerald-700 dark:text-emerald-300'
                  : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
              }`}
            >
              Moderate Noise (2%)
            </button>
            <button
              onClick={() => setNoiseSetting('high')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                noiseSetting === 'high'
                  ? 'bg-emerald-50 dark:bg-emerald-950 border-emerald-500 text-emerald-700 dark:text-emerald-300'
                  : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
              }`}
            >
              High Noise (8%)
            </button>
          </div>
        </div>

        <div className="h-80 w-full mb-6">
          <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400">
                <th className="py-2.5 px-3">Framework Configuration</th>
                <th className="py-2.5 px-3">Success Rate</th>
                <th className="py-2.5 px-3">Total Effective Cost</th>
                <th className="py-2.5 px-3">Oracle Calls</th>
                <th className="py-2.5 px-3">Ablation Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-700 dark:text-slate-300">
              {activeData.map((row, idx) => (
                <tr key={idx} className={idx === 0 ? "bg-emerald-50/40 dark:bg-emerald-950/20" : ""}>
                  <td className="py-2.5 px-3 font-sans font-medium">{row.name}</td>
                  <td className="py-2.5 px-3">
                    <span className={row.success >= 80 ? "text-emerald-600 font-bold" : "text-amber-600 font-medium"}>
                      {row.success.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-bold">{row.cost.toLocaleString()}</td>
                  <td className="py-2.5 px-3">{row.oracleCalls.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-sans">
                    {idx === 0 ? (
                      <span className="text-emerald-600 font-semibold">Reference Baseline</span>
                    ) : idx === 5 ? (
                      <span className="text-slate-400">Lower Bound Null Control</span>
                    ) : (
                      <span className="text-amber-700 dark:text-amber-400">
                        +{(row.cost - activeData[0].cost).toLocaleString()} calls (loss of efficiency)
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
