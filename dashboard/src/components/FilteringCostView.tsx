import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { Info } from 'lucide-react';

interface FilteringCostViewProps {
  isDark: boolean;
}

export const FilteringCostView: React.FC<FilteringCostViewProps> = ({ isDark }) => {
  const [prefixBits, setPrefixBits] = useState<number>(2);

  const keySizes = [4, 6, 8, 12, 16];

  const rows = keySizes.map((n) => {
    const N = 1 << n;
    const effPrefix = Math.min(prefixBits, n - 1);
    const N_prime = N >> effPrefix;
    const filterCost = 2 * effPrefix;

    const unfilteredClassical = N / 2.0;
    const filteredClassical = N_prime / 2.0 + filterCost;
    const filteredGrover = (Math.PI / 4.0) * Math.sqrt(N_prime) * 1.5 + filterCost;

    const filteringReduction = unfilteredClassical / (N_prime / 2.0);
    const quantumSpeedup = filteredClassical / filteredGrover;

    return {
      n,
      N,
      N_prime,
      unfilteredClassical,
      filteredClassical,
      filteredGrover: Math.round(filteredGrover),
      filteringReduction: filteringReduction.toFixed(1),
      quantumSpeedup: quantumSpeedup.toFixed(2),
    };
  });

  const chartOption = {
    backgroundColor: 'transparent',
    title: {
      text: `Search Cost Comparison (Prefix Constraint = ${prefixBits} bits)`,
      textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 13, fontWeight: 'bold' },
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      data: ['Unfiltered Classical', 'Filtered Classical', 'Filtered Grover'],
      textStyle: { color: isDark ? '#cbd5e1' : '#475569', fontSize: 11 },
      top: 28,
    },
    grid: { top: 75, right: 30, bottom: 45, left: 65 },
    xAxis: {
      type: 'category',
      data: keySizes.map((n) => `${n}-bit (N'=${1 << (n - Math.min(prefixBits, n - 1))})`),
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      axisLine: { lineStyle: { color: isDark ? '#334155' : '#cbd5e1' } },
    },
    yAxis: {
      type: 'log',
      name: 'Operations (Log Scale)',
      nameTextStyle: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 11 },
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 10 },
      splitLine: { lineStyle: { color: isDark ? '#1e293b' : '#f1f5f9' } },
    },
    series: [
      {
        name: 'Unfiltered Classical',
        type: 'bar',
        data: rows.map((r) => r.unfilteredClassical),
        itemStyle: { color: '#94a3b8' },
      },
      {
        name: 'Filtered Classical',
        type: 'bar',
        data: rows.map((r) => r.filteredClassical),
        itemStyle: { color: '#0072B2' },
      },
      {
        name: 'Filtered Grover',
        type: 'bar',
        data: rows.map((r) => r.filteredGrover),
        itemStyle: { color: '#009E73' },
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Fair Filtering Baseline & Quantum Speedup Decomposition
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Separates the classical search space reduction factor (N / N') from genuine quantum-specific algorithmic speedup.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-500">Constraint Bits:</span>
            <select
              value={prefixBits}
              onChange={(e) => setPrefixBits(parseInt(e.target.value))}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-1.5 text-slate-900 dark:text-slate-100"
            >
              <option value={1}>1 bit (2x pruning)</option>
              <option value={2}>2 bits (4x pruning)</option>
              <option value={3}>3 bits (8x pruning)</option>
              <option value={4}>4 bits (16x pruning)</option>
            </select>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/30 text-blue-900 dark:text-blue-200 mb-6 text-xs leading-relaxed">
          <div className="font-semibold uppercase tracking-wider mb-1 flex items-center">
            <Info className="w-4 h-4 mr-1.5 text-blue-600" />
            Audit Finding A1: Fair Baseline Accounting & Asymptotic Threshold
          </div>
          Filtered Grover must be benchmarked strictly against <em>Filtered Classical Brute Force</em>, not unfiltered classical search.
          On small keys (n &le; 8), constant-factor quantum overheads (gate synthesis and classical candidate verification)
          result in a quantum speedup S<sub>quantum</sub> &lt; 1.0x. True quantum speedup only emerges when the filtered space N' &gt;&gt; 2<sup>16</sup>.
        </div>

        <div className="h-80 w-full mb-6">
          <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400">
                <th className="py-2.5 px-3">Key Size (n)</th>
                <th className="py-2.5 px-3">Total Space (N)</th>
                <th className="py-2.5 px-3">Filtered Space (N')</th>
                <th className="py-2.5 px-3">Unfiltered Classical</th>
                <th className="py-2.5 px-3">Filtered Classical</th>
                <th className="py-2.5 px-3">Filtered Grover</th>
                <th className="py-2.5 px-3">Classical Pruning</th>
                <th className="py-2.5 px-3">Quantum Speedup (S_quantum)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-700 dark:text-slate-300">
              {rows.map((r) => (
                <tr key={r.n}>
                  <td className="py-2.5 px-3 font-sans font-medium">{r.n} bits</td>
                  <td className="py-2.5 px-3">{r.N.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-semibold text-emerald-600 dark:text-emerald-400">{r.N_prime.toLocaleString()}</td>
                  <td className="py-2.5 px-3">{r.unfilteredClassical.toLocaleString()}</td>
                  <td className="py-2.5 px-3">{r.filteredClassical.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-bold">{r.filteredGrover.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-sans">{r.filteringReduction}x</td>
                  <td className="py-2.5 px-3 font-sans">
                    <span
                      className={`px-2 py-0.5 rounded-full font-semibold ${
                        parseFloat(r.quantumSpeedup) >= 1.0
                          ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                          : "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300"
                      }`}
                    >
                      {r.quantumSpeedup}x
                    </span>
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
