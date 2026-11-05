import React from 'react';
import { 
  BarChart3, 
  Cpu, 
  ShieldAlert, 
  Play, 
  RotateCcw, 
  TrendingDown, 
  Filter, 
  Layers, 
  BookOpen, 
  MessageSquare, 
  Sun, 
  Moon 
} from 'lucide-react';

export type ViewType = 
  | 'overview' 
  | 'explorer' 
  | 'replay' 
  | 'crossover' 
  | 'filtering' 
  | 'ablation' 
  | 'circuits' 
  | 'readiness' 
  | 'validity';

interface NavbarProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  isDark: boolean;
  onToggleTheme: () => void;
  isAssistantOpen: boolean;
  onToggleAssistant: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onSelectView,
  isDark,
  onToggleTheme,
  isAssistantOpen,
  onToggleAssistant,
}) => {
  const navItems: Array<{ id: ViewType; label: string; icon: React.ReactNode }> = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4 mr-1.5" /> },
    { id: 'explorer', label: 'Strategy Explorer', icon: <Play className="w-4 h-4 mr-1.5" /> },
    { id: 'replay', label: 'Controller Replay', icon: <RotateCcw className="w-4 h-4 mr-1.5" /> },
    { id: 'crossover', label: 'Noise Crossover', icon: <TrendingDown className="w-4 h-4 mr-1.5" /> },
    { id: 'filtering', label: 'Filtering Cost', icon: <Filter className="w-4 h-4 mr-1.5" /> },
    { id: 'ablation', label: 'Ablation Matrix', icon: <Layers className="w-4 h-4 mr-1.5" /> },
    { id: 'circuits', label: 'Circuit Resources', icon: <Cpu className="w-4 h-4 mr-1.5" /> },
    { id: 'readiness', label: 'AES Readiness', icon: <ShieldAlert className="w-4 h-4 mr-1.5" /> },
    { id: 'validity', label: 'Methods & Audit', icon: <BookOpen className="w-4 h-4 mr-1.5" /> },
  ];

  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <span className="font-bold text-lg tracking-tight text-emerald-700 dark:text-emerald-400">
              AdaptiveGrover-QCA
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 font-mono">
              Research Platform v1.0
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleTheme}
              title={isDark ? "Switch to light theme" : "Switch to dark theme"}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
            </button>

            <button
              onClick={onToggleAssistant}
              className={`flex items-center text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
                isAssistantOpen
                  ? "bg-emerald-50 dark:bg-emerald-950/50 border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300"
                  : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
              Research Assistant
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex space-x-1 overflow-x-auto py-2 scrollbar-none border-t border-slate-100 dark:border-slate-800">
          {navItems.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id)}
                className={`flex items-center whitespace-nowrap px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-emerald-600 text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
              >
                {item.icon}
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
