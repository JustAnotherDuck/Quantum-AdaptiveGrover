import React, { useState } from 'react';
import { ExecutionRecord } from '../types';
import { Play, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

interface StrategyExplorerViewProps {
  onLoadReplayData?: (record: ExecutionRecord) => void;
}

export const StrategyExplorerView: React.FC<StrategyExplorerViewProps> = ({ onLoadReplayData }) => {
  const [strategy, setStrategy] = useState<string>("Adaptive Hybrid (Proposed)");
  const [keySize, setKeySize] = useState<number>(4);
  const [noiseLevel, setNoiseLevel] = useState<number>(0.02);
  const [prefixBits, setPrefixBits] = useState<number>(1);
  const [shotsPerRound, setShotsPerRound] = useState<number>(64);
  const maxCalls = 15000;
  const [targetKey, setTargetKey] = useState<number>(7);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ExecutionRecord | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const strategies = [
    "Adaptive Hybrid (Proposed)",
    "Standard Grover",
    "Shallow + Restart",
    "Noise-Aware Grover",
    "Classical Brute Force",
    "Random Guess (Null Control)",
  ];

  const handleSimulate = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const payload = {
        strategy_name: strategy,
        key_size: keySize,
        target_key: targetKey % (1 << keySize),
        noise_level: noiseLevel,
        prefix_bits: prefixBits >= keySize ? keySize - 1 : prefixBits,
        shots_per_round: shotsPerRound,
        max_total_oracle_calls: maxCalls,
        seed: 42,
      };

      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Simulation request failed: status ${res.status}`);
      }
      const data = await res.json();
      const normalizedRecord: ExecutionRecord = {
        strategy_name: data.strategy_name || strategy,
        target_key: data.target_key,
        found_key: data.found_key !== undefined ? data.found_key : null,
        is_verified: Boolean(data.is_verified),
        total_oracle_calls: data.total_oracle_calls ?? data.oracle_calls ?? 0,
        classical_verification_calls:
          data.classical_verification_calls ?? data.classical_verify_cost ?? 0,
        total_effective_cost: data.total_effective_cost ?? 0,
        wall_clock_seconds: data.wall_clock_seconds ?? data.wall_clock_time ?? 0,
        rounds_executed: data.rounds_executed ?? data.extra_metadata?.rounds ?? 1,
        final_search_space_size:
          data.final_search_space_size ?? data.extra_metadata?.candidates_remaining ?? (1 << keySize),
        round_logs:
          Array.isArray(data.round_logs) && data.round_logs.length > 0
            ? data.round_logs
            : [
                {
                  round: 1,
                  action: data.strategy_name || strategy,
                  iterations: data.iterations ?? 0,
                  shots: data.shots ?? 0,
                  measured_key: data.found_key ?? 0,
                  oracle_calls: data.total_oracle_calls ?? data.oracle_calls ?? 0,
                  success: Boolean(data.is_verified),
                  noise_estimate: data.noise_level ?? noiseLevel,
                },
              ],
        per_attempt_success: data.per_attempt_success,
        ...data,
      };
      setResult(normalizedRecord);
      if (onLoadReplayData) {
        onLoadReplayData(normalizedRecord);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Execution error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4">
          Simulation Controls & Parameters
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Search Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-slate-900 dark:text-slate-100"
            >
              {strategies.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-slate-500 mt-1">
              Evaluates under identical maximum call budget B<sub>max</sub>.
            </p>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Key Length (n): {keySize} bits</span>
              <span className="text-slate-400">N = {1 << keySize} candidates</span>
            </div>
            <input
              type="range"
              min={2}
              max={8}
              value={keySize}
              onChange={(e) => {
                const n = parseInt(e.target.value);
                setKeySize(n);
                if (prefixBits >= n) setPrefixBits(Math.max(0, n - 1));
              }}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>2 bits</span>
              <span>4 bits</span>
              <span>6 bits</span>
              <span>8 bits</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Two-Qubit Error (&epsilon;<sub>2q</sub>): {(noiseLevel * 100).toFixed(1)}%</span>
              <span className="text-slate-400">{noiseLevel <= 0.01 ? "NISQ realistic" : "Stress regime"}</span>
            </div>
            <input
              type="range"
              min={0}
              max={0.20}
              step={0.005}
              value={noiseLevel}
              onChange={(e) => setNoiseLevel(parseFloat(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0% (Ideal)</span>
              <span>5%</span>
              <span>10%</span>
              <span>20%</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Classical Prefix Bits: {prefixBits} bits</span>
              <span className="text-slate-400">Pruning: {1 << prefixBits}x</span>
            </div>
            <input
              type="range"
              min={0}
              max={Math.max(0, keySize - 1)}
              value={prefixBits}
              onChange={(e) => setPrefixBits(parseInt(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Simulates classical cryptanalytic side-channel or differential filter.
            </p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Measurement Shots per Round: {shotsPerRound}
            </label>
            <select
              value={shotsPerRound}
              onChange={(e) => setShotsPerRound(parseInt(e.target.value))}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-slate-900 dark:text-slate-100"
            >
              <option value={16}>16 shots</option>
              <option value={32}>32 shots</option>
              <option value={64}>64 shots</option>
              <option value={128}>128 shots</option>
              <option value={256}>256 shots</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Target Key Value: {targetKey % (1 << keySize)}</span>
              <span className="font-mono text-[11px]">0x{(targetKey % (1 << keySize)).toString(16).toUpperCase()}</span>
            </div>
            <input
              type="number"
              min={0}
              max={(1 << keySize) - 1}
              value={targetKey % (1 << keySize)}
              onChange={(e) => setTargetKey(parseInt(e.target.value) || 0)}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-slate-900 dark:text-slate-100"
            />
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
          <div className="text-xs text-slate-500">
            Equalized budget cap: <span className="font-mono">{maxCalls.toLocaleString()}</span> maximum oracle calls.
          </div>
          <button
            onClick={handleSimulate}
            disabled={isLoading}
            className="flex items-center px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs shadow-xs transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 mr-2 animate-spin" />
                Executing Simulation...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 mr-2" />
                Run Simulation
              </>
            )}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-300 text-xs">
          Error: {errorMsg}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Key Recovery</span>
              <div className="flex items-center space-x-1.5">
                {result.is_verified ? (
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-600" />
                )}
                <span className="text-sm font-bold font-mono">
                  {result.found_key !== null ? result.found_key : "None"}
                </span>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Oracle Calls</span>
              <span className="text-sm font-bold font-mono">
                {(result.total_oracle_calls ?? result.oracle_calls ?? 0).toLocaleString()}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Verification Checks</span>
              <span className="text-sm font-bold font-mono">
                {(result.classical_verification_calls ?? result.classical_verify_cost ?? 0).toLocaleString()}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Total Effective Cost</span>
              <span className="text-sm font-bold font-mono text-emerald-600 dark:text-emerald-400">
                {Math.round(result.total_effective_cost ?? 0).toLocaleString()}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Rounds Executed</span>
              <span className="text-sm font-bold font-mono">
                {result.rounds_executed ?? 1}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Elapsed Time</span>
              <span className="text-sm font-bold font-mono">
                {(((result.wall_clock_seconds ?? result.wall_clock_time ?? 0)) * 1000).toFixed(1)} ms
              </span>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3">
              Round Execution Trace ({(result.round_logs ?? []).length} rounds)
            </h3>
            <div className="overflow-x-auto max-h-60 overflow-y-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead className="sticky top-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                  <tr className="text-slate-500 dark:text-slate-400">
                    <th className="py-2 px-3">Round</th>
                    <th className="py-2 px-3">Action</th>
                    <th className="py-2 px-3">Iterations (k)</th>
                    <th className="py-2 px-3">Shots</th>
                    <th className="py-2 px-3">Measured Key</th>
                    <th className="py-2 px-3">Oracle Calls</th>
                    <th className="py-2 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
                  {(result.round_logs ?? []).map((r, i) => (
                    <tr key={i} className={r.success ? "bg-emerald-50/50 dark:bg-emerald-950/20" : ""}>
                      <td className="py-2 px-3">{r.round}</td>
                      <td className="py-2 px-3 font-sans font-medium">{r.action}</td>
                      <td className="py-2 px-3">{r.iterations ?? 0}</td>
                      <td className="py-2 px-3">{r.shots ?? 0}</td>
                      <td className="py-2 px-3">
                        {r.measured_key !== null && r.measured_key !== undefined
                          ? `${r.measured_key} (0x${r.measured_key.toString(16)})`
                          : "None"}
                      </td>
                      <td className="py-2 px-3">{(r.oracle_calls ?? 0).toLocaleString()}</td>
                      <td className="py-2 px-3 font-sans">
                        {r.success ? (
                          <span className="text-emerald-600 font-medium">Verified Correct</span>
                        ) : (
                          <span className="text-slate-400">Verification Failed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
