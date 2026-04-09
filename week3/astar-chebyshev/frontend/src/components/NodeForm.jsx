import React from 'react';
import { MousePointer2, Plus, ArrowRight, Flag, Play, RotateCcw } from 'lucide-react';
import { cn } from '../utils';

export default function NodeForm({ mode, setMode, onSolve, onClear, solving }) {
  return (
    <div className="w-16 md:w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col p-2 md:p-4 shadow-sm z-10 transition-all">
      <div className="hidden md:flex items-center gap-2 mb-8">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-600/20">A*</div>
        <h1 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Path Finder</h1>
      </div>
      
      <div className="flex flex-col gap-2 flex-grow">
        <ToolButton title="Select nodes or edges" icon={<MousePointer2 size={18} />} label="Select" active={mode === 'select'} onClick={() => setMode('select')} />
        <ToolButton title="Click on grid to add a node" icon={<Plus size={18} />} label="Add Node" active={mode === 'add_node'} onClick={() => setMode('add_node')} />
        <ToolButton title="Connect two nodes with an edge" icon={<ArrowRight size={18} />} label="Add Edge" active={mode === 'add_edge'} onClick={() => setMode('add_edge')} />
        <div className="h-px bg-slate-200 dark:bg-slate-800 my-2" />
        <ToolButton title="Select start node" icon={<Flag size={18} className="text-emerald-500" />} label="Set Start" active={mode === 'set_start'} onClick={() => setMode('set_start')} />
        <ToolButton title="Select goal node" icon={<Flag size={18} className="text-rose-500" />} label="Set Goal" active={mode === 'set_goal'} onClick={() => setMode('set_goal')} />
      </div>

      <div className="flex flex-col gap-2 mt-auto">
        <button 
          onClick={onClear}
          title="Clear all nodes and edges"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
        >
          <RotateCcw size={18} />
          <span className="hidden md:block font-medium">Clear Graph</span>
        </button>
        <button 
          onClick={onSolve}
          disabled={solving}
          title="Run A* algorithm"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium shadow-md transition disabled:opacity-50"
        >
          {solving ? <span className="animate-spin text-xl">◌</span> : <Play size={18} />}
          <span className="hidden md:block">Solve Path</span>
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
        "flex items-center gap-3 w-full p-2.5 rounded-lg transition-all text-sm font-medium relative",
        active 
           ? "bg-slate-100 text-indigo-600 dark:bg-slate-800 dark:text-indigo-400 shadow-inner" 
           : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200"
      )}
    >
      {icon}
      <span className="hidden md:block">{label}</span>
      {active && <div className="absolute left-0 w-1 h-8 bg-indigo-600 rounded-r-full" />}
    </button>
  );
}