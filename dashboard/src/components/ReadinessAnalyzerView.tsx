import React, { useState, useEffect } from 'react';
import { ReadinessData } from '../types';
import { ShieldAlert, AlertTriangle, BookOpen } from 'lucide-react';

export const ReadinessAnalyzerView: React.FC = () => {
  const [cipher, setCipher] = useState<string>("AES-128");
  const [errorRate, setErrorRate] = useState<number>(0.001);
  const [threshold, setThreshold] = useState<number>(0.01);
  const [data, setData] = useState<ReadinessData | null>(null);

  const fetchReadiness = () => {
    fetch("/api/readiness", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cipher,
        physical_error_rate: errorRate,
        code_threshold: threshold,
      }),
    })
      .then((res) => res.json())
      .then((resData) => setData(resData))
      .catch((err) => console.error("Readiness evaluation failed", err));
  };

  useEffect(() => {
    fetchReadiness();
  }, [cipher, errorRate, threshold]);

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-xl border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200">
        <div className="flex items-start space-x-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="text-xs leading-relaxed">
            <span className="font-semibold uppercase tracking-wider block mb-0.5">
              Experimental Estimate Only | Cryptographic Safety Notice
            </span>
            {data?.safety_disclaimer ||
              "EXPERIMENTAL ESTIMATE ONLY: Not a formal cryptographic certification. This research framework evaluates reduced-scale instances in simulation. No claim is made that current quantum hardware can break AES-128 or AES-256."}
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4">
          Cipher Security & Hardware Parameter Configuration
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Cryptographic Cipher Target
            </label>
            <select
              value={cipher}
              onChange={(e) => setCipher(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 text-slate-900 dark:text-slate-100"
            >
              <option value="AES-128">AES-128 (NIST Standard)</option>
              <option value="AES-192">AES-192 (NIST Standard)</option>
              <option value="AES-256">AES-256 (NIST Standard)</option>
              <option value="S-AES">S-AES (16-bit Educational SPN)</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Physical Gate Error Rate: {(errorRate * 100).toFixed(2)}%</span>
            </div>
            <input
              type="range"
              min={0.0001}
              max={0.02}
              step={0.0005}
              value={errorRate}
              onChange={(e) => setErrorRate(parseFloat(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.01% (Target FTQC)</span>
              <span>0.1%</span>
              <span>1.0%</span>
              <span>2.0% (Current NISQ)</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              <span>Surface Code Threshold: {(threshold * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min={0.001}
              max={0.05}
              step={0.002}
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.1%</span>
              <span>1.0% (Standard)</span>
              <span>5.0%</span>
            </div>
          </div>
        </div>
      </div>

      {data && (
        <div className="space-y-6">
          <div
            className={`p-5 rounded-xl border ${
              data.circuit_survival_probability > 0.05
                ? "bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200"
                : "bg-red-50 dark:bg-red-950/40 border-red-300 dark:border-red-800 text-red-900 dark:text-red-200"
            }`}
          >
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
              <div>
                <span className="font-bold text-sm block mb-1">
                  NISQ Feasibility Assessment Verdict
                </span>
                <p className="text-xs leading-relaxed">{data.nisq_feasibility_verdict}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Ideal Grover Iterations</span>
              <span className="text-lg font-bold font-mono text-slate-900 dark:text-slate-100">
                {data.ideal_grover_iterations}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Logical Qubits Needed</span>
              <span className="text-lg font-bold font-mono text-slate-900 dark:text-slate-100">
                {data.logical_qubits_required.toLocaleString()}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">NISQ Circuit Survival</span>
              <span className="text-lg font-bold font-mono text-red-600 dark:text-red-400">
                {data.circuit_survival_probability === 0 ? "0.00e+00" : data.circuit_survival_probability.toExponential(2)}
              </span>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-[11px] text-slate-500 block mb-1">Reference Citation</span>
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block truncate">
                {data.literature_source}
              </span>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs text-xs space-y-3">
            <div className="flex items-center space-x-2 font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              <BookOpen className="w-4 h-4 text-purple-600" />
              <span>Grounded Peer-Reviewed Literature Evidence</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
              Comprehensive quantum resource estimates published by Grassl et al. (PQCrypto 2016) and Jaques et al. (EUROCRYPT 2020)
              establish that full AES exhaustive key search requires sequential quantum circuits with T-depth exceeding 120 layers per round
              over 2<sup>64</sup> iterations.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 font-mono text-[11px] text-slate-700 dark:text-slate-300">
              Total Circuit Operations = ~1.18 &times; 10<sup>19</sup> iterations &times; 54,400 T-gates &asymp; 6.4 &times; 10<sup>23</sup> gates.
              At physical gate error &epsilon; = 0.1%, fidelity collapses to (1 - 10<sup>-3</sup>)<sup>10<sup>23</sup></sup> &equiv; 0.00.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
