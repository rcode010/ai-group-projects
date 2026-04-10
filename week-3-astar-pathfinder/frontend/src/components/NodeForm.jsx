import React from 'react';
import { MousePointer2, Plus, ArrowRight, Flag, Play, RotateCcw, AlertCircle, GitBranch } from 'lucide-react';
import { cn } from '../utils';

export default function NodeForm({
  mode, setMode, onSolve, onClear,
  solving, error,
  startNode, goalNode,
  nodeCount, edgeCount,
}) {
  return (
    <div className="w-16 md:w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col p-2 md:p-6 shadow-sm z-10 shrink-0 overflow-y-auto">

      {/* Logo */}
      <div className="hidden md:flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center font-black text-white text-base shadow-lg shadow-indigo-600/30 select-none">
          A*
        </div>
        <div>
          <h1 className="font-bold text-slate-800 dark:text-slate-100 leading-tight text-lg">Path Finder</h1>
          <p className="text-[11px] font-medium text-slate-400 leading-tight mt-0.5">Chebyshev Heuristic</p>
        </div>
      </div>

      {/* Start / Goal indicator */}
      <div className="hidden md:flex gap-3 mb-5">
        <div className="flex-1 rounded-xl bg-emerald-50 border border-emerald-200 p-2.5 text-center">
          <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-wider mb-0.5">Start</p>
          <p className="font-black text-emerald-700 text-xl">{startNode ?? '—'}</p>
        </div>
        <div className="flex-1 rounded-xl bg-rose-50 border border-rose-200 p-2.5 text-center">
          <p className="text-[10px] text-rose-500 font-bold uppercase tracking-wider mb-0.5">Goal</p>
          <p className="font-black text-rose-700 text-xl">{goalNode ?? '—'}</p>
        </div>
      </div>

      {/* Graph stats */}
      <div className="hidden md:flex gap-3 mb-8">
        <div className="flex-1 rounded-xl bg-slate-50 border border-slate-200 p-2.5 text-center">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Nodes</p>
          <p className="font-bold text-slate-700 text-lg">{nodeCount ?? 0}</p>
        </div>
        <div className="flex-1 rounded-xl bg-slate-50 border border-slate-200 p-2.5 text-center">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Edges</p>
          <p className="font-bold text-slate-700 text-lg">{edgeCount ?? 0}</p>
        </div>
      </div>

      {/* Section label */}
      <p className="hidden md:block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3 px-1">Tools</p>

      {/* Tool buttons */}
      <div className="flex flex-col gap-1.5 flex-grow">
        <ToolButton
          title="Click the grid to place a new node"
          icon={<Plus size={18} />}
          label="Add Node"
          active={mode === 'add_node'}
          onClick={() => setMode('add_node')}
        />
        <ToolButton
          title="Click two nodes to connect them"
          icon={<ArrowRight size={18} />}
          label="Add Edge"
          active={mode === 'add_edge'}
          onClick={() => setMode('add_edge')}
        />
        <ToolButton
          title="Drag to move nodes · Right-click to delete"
          icon={<MousePointer2 size={18} />}
          label="Select / Move"
          active={mode === 'select'}
          onClick={() => setMode('select')}
        />

        <div className="h-px bg-slate-200 dark:bg-slate-800 my-3" />

        <ToolButton
          title="Click a node to mark it as Start"
          icon={<Flag size={18} className="text-emerald-500" />}
          label="Set Start"
          active={mode === 'set_start'}
          onClick={() => setMode('set_start')}
        />
        <ToolButton
          title="Click a node to mark it as Goal"
          icon={<Flag size={18} className="text-rose-500" />}
          label="Set Goal"
          active={mode === 'set_goal'}
          onClick={() => setMode('set_goal')}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="hidden md:flex items-start gap-2 mt-4 p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-600 text-sm">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex flex-col gap-3 mt-auto pt-6">
        <button
          onClick={onClear}
          title="Reset to default graph"
          className="flex items-center justify-center gap-2.5 w-full py-2.5 px-4 rounded-xl border-2 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 hover:border-slate-300 dark:hover:bg-slate-800 transition-all text-sm font-bold"
        >
          <RotateCcw size={16} />
          <span className="hidden md:block">Reset Graph</span>
        </button>

        <button
          onClick={onSolve}
          disabled={solving || !startNode || !goalNode}
          title="Run A* algorithm"
          className="flex items-center justify-center gap-2.5 w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-bold shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-base"
        >
          {solving
            ? <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            : <Play size={18} fill="white" />
          }
          <span className="hidden md:block">{solving ? 'Solving…' : 'Solve Path'}</span>
        </button>
      </div>
    </div>
  );
}

function ToolButton({ icon, label, active, onClick, title }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={cn(
        'flex items-center gap-3 w-full px-3 py-2 rounded-lg transition-all text-sm font-medium relative',
        active
          ? 'bg-indigo-50 text-indigo-600 dark:bg-slate-800 dark:text-indigo-400'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800'
      )}
    >
      {active && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-600 rounded-r-full" />
      )}
      <span className="ml-1 shrink-0">{icon}</span>
      <span className="hidden md:block truncate">{label}</span>
    </button>
  );
}