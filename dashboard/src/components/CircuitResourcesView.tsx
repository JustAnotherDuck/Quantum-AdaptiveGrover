import React, { useState, useEffect } from 'react';
import { CircuitData } from '../types';
import { Cpu, BookOpen, Layers, Check, Copy } from 'lucide-react';

export const CircuitResourcesView: React.FC = () => {
  const [keySize, setKeySize] = useState<number>(4);
  const [circuitData, setCircuitData] = useState<CircuitData | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    fetch(`/api/circuits?key_size=${keySize}`)
      .then((res) => res.json())
      .then((data) => setCircuitData(data))
      .catch((err) => console.error("Failed to load circuit resources", err));
  }, [keySize]);

  const copyQASM = () => {
    if (circuitData?.mode_a.qasm_snippet) {
      navigator.clipboard.writeText(circuitData.mode_a.qasm_snippet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Quantum Circuit Resource Profiles (Mode A & Mode B)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Synthesis profiles for simulated marked-state phase oracles and reversible cryptographic block cipher circuits.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-500">Key Size:</span>
            <select
              value={keySize}
              onChange={(e) => setKeySize(parseInt(e.target.value))}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-1.5 text-slate-900 dark:text-slate-100"
            >
              <option value={4}>4-bit (SPN nibble)</option>
              <option value={6}>6-bit</option>
              <option value={8}>8-bit (2-nibble SPN)</option>
            </select>
          </div>
        </div>

        {/* Mode A & Mode B Resource Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Mode A */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 mb-3">
              <Layers className="w-4 h-4 text-emerald-600" />
              <span>Mode A: Synthesized Phase Oracle</span>
            </div>
            {circuitData ? (
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Total Qubits</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_a.stats.num_qubits} qubits
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Circuit Depth</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_a.stats.depth} layers
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Two-Qubit Gates (CX)</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_a.stats.two_qubit_gates}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Total Gate Count</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_a.stats.total_gates}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-400 py-4">Loading Mode A metrics...</div>
            )}
          </div>

          {/* Mode B */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 mb-3">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span>Mode B: Reversible Cryptographic SPN Oracle</span>
            </div>
            {circuitData?.mode_b ? (
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Total Qubits</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_b.stats.num_qubits} qubits
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Circuit Depth</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_b.stats.depth} layers
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Two-Qubit Gates (CX)</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_b.stats.two_qubit_gates}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Total Gate Count</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {circuitData.mode_b.stats.total_gates}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-400 py-4">
                Mode B reversible SPN is configured for 4-bit and 8-bit block structures.
              </div>
            )}
          </div>
        </div>

        {/* QASM Snippet Viewer */}
        {circuitData?.mode_a.qasm_snippet && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
                Generated OpenQASM 2.0 Representation (Mode A)
              </span>
              <button
                onClick={copyQASM}
                className="flex items-center text-[11px] text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              >
                {copied ? <Check className="w-3.5 h-3.5 mr-1 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                {copied ? "Copied" : "Copy QASM"}
              </button>
            </div>
            <pre className="p-3 rounded-lg bg-slate-900 text-slate-200 font-mono text-[11px] overflow-x-auto max-h-44 border border-slate-800">
              {circuitData.mode_a.qasm_snippet}
            </pre>
          </div>
        )}

        {/* Literature Benchmark External Comparison */}
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3">
            <BookOpen className="w-4 h-4 text-purple-600" />
            <span>Verified Peer-Reviewed Cryptographic Literature Benchmarks</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400">
                  <th className="py-2.5 px-3">Target Cipher</th>
                  <th className="py-2.5 px-3">Reference Citation</th>
                  <th className="py-2.5 px-3">Logical Qubits</th>
                  <th className="py-2.5 px-3">T-Depth per Oracle</th>
                  <th className="py-2.5 px-3">Total T-Gates per Oracle</th>
                  <th className="py-2.5 px-3">Oracle Invocations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px] text-slate-700 dark:text-slate-300">
                <tr>
                  <td className="py-2.5 px-3 font-sans font-bold">AES-128</td>
                  <td className="py-2.5 px-3 font-sans">Grassl et al. (PQCrypto 2016)</td>
                  <td className="py-2.5 px-3">2,953</td>
                  <td className="py-2.5 px-3">3,740</td>
                  <td className="py-2.5 px-3">1,190,400</td>
                  <td className="py-2.5 px-3">&approx; 1.18 &times; 10<sup>19</sup></td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-sans font-bold">AES-128</td>
                  <td className="py-2.5 px-3 font-sans">Jaques et al. (EUROCRYPT 2020)</td>
                  <td className="py-2.5 px-3">1,785</td>
                  <td className="py-2.5 px-3">120</td>
                  <td className="py-2.5 px-3">54,400</td>
                  <td className="py-2.5 px-3">&approx; 1.18 &times; 10<sup>19</sup></td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-sans font-bold">AES-192</td>
                  <td className="py-2.5 px-3 font-sans">Grassl et al. (PQCrypto 2016)</td>
                  <td className="py-2.5 px-3">4,449</td>
                  <td className="py-2.5 px-3">4,488</td>
                  <td className="py-2.5 px-3">1,428,480</td>
                  <td className="py-2.5 px-3">&approx; 1.89 &times; 10<sup>28</sup></td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-sans font-bold">AES-256</td>
                  <td className="py-2.5 px-3 font-sans">Grassl et al. (PQCrypto 2016)</td>
                  <td className="py-2.5 px-3">6,681</td>
                  <td className="py-2.5 px-3">5,236</td>
                  <td className="py-2.5 px-3">1,666,560</td>
                  <td className="py-2.5 px-3">&approx; 2.42 &times; 10<sup>38</sup></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
