import React, { useState, useEffect } from 'react';
import { Navbar, ViewType } from './components/Navbar';
import { OverviewView } from './components/OverviewView';
import { StrategyExplorerView } from './components/StrategyExplorerView';
import { ControllerReplayView } from './components/ControllerReplayView';
import { NoiseCrossoverView } from './components/NoiseCrossoverView';
import { FilteringCostView } from './components/FilteringCostView';
import { AblationMatrixView } from './components/AblationMatrixView';
import { CircuitResourcesView } from './components/CircuitResourcesView';
import { ReadinessAnalyzerView } from './components/ReadinessAnalyzerView';
import { MethodsValidityView } from './components/MethodsValidityView';
import { AssistantDrawer } from './components/AssistantDrawer';
import { ExecutionRecord } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('overview');
  const [isDark, setIsDark] = useState<boolean>(true);
  const [isAssistantOpen, setIsAssistantOpen] = useState<boolean>(false);
  const [replayRecord, setReplayRecord] = useState<ExecutionRecord | null>(null);

  // Apply dark mode class to html element
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleLoadReplayData = (record: ExecutionRecord) => {
    setReplayRecord(record);
  };

  const handleAssistantSimulationTrigger = (_config: any) => {
    setCurrentView('explorer');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Navigation Bar */}
      <Navbar
        currentView={currentView}
        onSelectView={setCurrentView}
        isDark={isDark}
        onToggleTheme={() => setIsDark(!isDark)}
        isAssistantOpen={isAssistantOpen}
        onToggleAssistant={() => setIsAssistantOpen(!isAssistantOpen)}
      />

      {/* Main View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'overview' && <OverviewView onNavigate={setCurrentView} />}
        {currentView === 'explorer' && (
          <StrategyExplorerView onLoadReplayData={handleLoadReplayData} />
        )}
        {currentView === 'replay' && (
          <ControllerReplayView initialRecord={replayRecord} isDark={isDark} />
        )}
        {currentView === 'crossover' && <NoiseCrossoverView isDark={isDark} />}
        {currentView === 'filtering' && <FilteringCostView isDark={isDark} />}
        {currentView === 'ablation' && <AblationMatrixView isDark={isDark} />}
        {currentView === 'circuits' && <CircuitResourcesView />}
        {currentView === 'readiness' && <ReadinessAnalyzerView />}
        {currentView === 'validity' && <MethodsValidityView />}
      </main>

      {/* Research Assistant Drawer */}
      <AssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        onTriggerSimulation={handleAssistantSimulationTrigger}
      />

      {/* Research Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="font-medium text-slate-700 dark:text-slate-300">
            AdaptiveGrover-QCA: Adaptive and Noise-Aware Key Search for Practical Quantum Cryptanalysis
          </p>
          <p>
            Reproducible Experimental Research Platform &bull; Strictly Zero Speculative Extrapolations
          </p>
        </div>
      </footer>
    </div>
  );
};
export default App;
