import { useState, useRef, MouseEvent, useEffect } from 'react';
import { MousePointer2, Plus, ArrowRight, Flag, Play, X, RotateCcw } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type Node = { id: string; x: number; y: number };
type Edge = { source: string; target: string; weight: number };

type Mode = 'select' | 'add_node' | 'add_edge' | 'set_start' | 'set_goal';

const GRID_SIZE = 40;

export default function App() {
  const [nodes, setNodes] = useState<{ id: string; x: number; y: number }[]>([]);
  const [edges, setEdges] = useState<{ source: string; target: string; weight: number }[]>([]);
  
  const [mode, setMode] = useState<Mode>('add_node');
  const [startNode, setStartNode] = useState<string | null>(null);
  const [goalNode, setGoalNode] = useState<string | null>(null);

  const [selectedEdgeNode, setSelectedEdgeNode] = useState<string | null>(null);
  const boardRef = useRef<HTMLDivElement>(null);

  const [solveResult, setSolveResult] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [solving, setSolving] = useState(false);
  
  const nextNodeId = String.fromCharCode(65 + nodes.length); // A, B, C...

  const handleBoardClick = (e: MouseEvent<HTMLDivElement>) => {
    if (!boardRef.current) return;
    const rect = boardRef.current.getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) / GRID_SIZE) * GRID_SIZE;
    const y = Math.round((e.clientY - rect.top) / GRID_SIZE) * GRID_SIZE;

    if (mode === 'add_node') {
      // Check if node exists closely
      if (nodes.some(n => Math.abs(n.x - x) < 20 && Math.abs(n.y - y) < 20)) return;
      
      const newNodeId = nodes.length === 0 ? 'S' : (nodes.length === 1 && !goalNode ? 'G' : nextNodeId);
      setNodes([...nodes, { id: newNodeId, x, y }]);
      if (newNodeId === 'S') setStartNode('S');
      if (newNodeId === 'G') setGoalNode('G');
    }
  };

  const handleNodeClick = (e: MouseEvent, id: string) => {
    e.stopPropagation();
    if (mode === 'add_edge') {
      if (!selectedEdgeNode) {
        setSelectedEdgeNode(id);
      } else {
        if (selectedEdgeNode !== id) {
          // Add edge
          const n1 = nodes.find(n => n.id === selectedEdgeNode)!;
          const n2 = nodes.find(n => n.id === id)!;
          const dist = Math.sqrt(Math.pow(n1.x - n2.x, 2) + Math.pow(n1.y - n2.y, 2));
          // Check if edge exists
          if (!edges.some(e => (e.source === n1.id && e.target === n2.id) || (e.source === n2.id && e.target === n1.id))) {
             setEdges([...edges, { source: n1.id, target: n2.id, weight: Math.round(dist) }]);
          }
        }
        setSelectedEdgeNode(null);
      }
    } else if (mode === 'set_start') {
      setStartNode(id);
    } else if (mode === 'set_goal') {
      setGoalNode(id);
    } else if (mode === 'select') {
       // do nothing
    }
  };

  const handleSolve = async () => {
    if (!startNode || !goalNode) {
      alert("Please set a Start and Goal node.");
      return;
    }
    setSolving(true);
    try {
      const resp = await fetch('http://localhost:8000/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, edges, start_node: startNode, goal_node: goalNode })
      });
      const data = await resp.json();
      if (!resp.ok) {
        setSolveResult({ error: data.detail || "An unexpected error occurred." });
      } else {
        setSolveResult(data);
      }
      setShowModal(true);
    } catch (err) {
      alert("Error contacting the backend.");
    } finally {
      setSolving(false);
    }
  };

  const handleClear = () => {
     setNodes([]);
     setEdges([]);
     setStartNode(null);
     setGoalNode(null);
     setSolveResult(null);
     setShowModal(false);
  };

  // Keyboard accessibility
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
       if (e.key === 'Escape') setSelectedEdgeNode(null);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 font-sans overflow-hidden">
      {/* Sidebar Toolbar */}
      <div className="w-16 md:w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col p-2 md:p-4 shadow-sm z-10 transition-all">
        <div className="hidden md:flex items-center gap-2 mb-8">
           <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-600/20">A*</div>
           <h1 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Path Finder</h1>
        </div>
        
        <div className="flex flex-col gap-2 flex-grow">
          <ToolButton icon={<MousePointer2 size={18} />} label="Select" active={mode === 'select'} onClick={() => setMode('select')} />
          <ToolButton icon={<Plus size={18} />} label="Add Node" active={mode === 'add_node'} onClick={() => setMode('add_node')} />
          <ToolButton icon={<ArrowRight size={18} />} label="Add Edge" active={mode === 'add_edge'} onClick={() => setMode('add_edge')} />
          <div className="h-px bg-slate-200 dark:bg-slate-800 my-2" />
          <ToolButton icon={<Flag size={18} className="text-emerald-500" />} label="Set Start" active={mode === 'set_start'} onClick={() => setMode('set_start')} />
          <ToolButton icon={<Flag size={18} className="text-rose-500" />} label="Set Goal" active={mode === 'set_goal'} onClick={() => setMode('set_goal')} />
        </div>

        <div className="flex flex-col gap-2 mt-auto">
          <button 
             onClick={handleClear}
             className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
          >
             <RotateCcw size={18} />
             <span className="hidden md:block font-medium">Clear Graph</span>
          </button>
          <button 
             onClick={handleSolve}
             disabled={solving}
             className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium shadow-md transition disabled:opacity-50"
          >
             {solving ? <span className="animate-spin text-xl">◌</span> : <Play size={18} />}
             <span className="hidden md:block">Solve Path</span>
          </button>
        </div>
      </div>

      {/* Main Board */}
      <div className="flex-1 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
         {/* Grid Background Pattern */}
         <div 
           ref={boardRef}
           onClick={handleBoardClick}
           className="absolute inset-0 cursor-crosshair overflow-hidden" 
           style={{
             backgroundImage: `radial-gradient(circle at 1px 1px, #cbd5e1 1px, transparent 0)`,
             backgroundSize: `${GRID_SIZE}px ${GRID_SIZE}px`
           }}
         >
            {/* Edges Layer */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {edges.map((edge, i) => {
                 const n1 = nodes.find(n => n.id === edge.source);
                 const n2 = nodes.find(n => n.id === edge.target);
                 if (!n1 || !n2) return null;
                 const isSolution = solveResult?.path && solveResult.path.includes(edge.source) && solveResult.path.includes(edge.target) && Math.abs(solveResult.path.indexOf(edge.source) - solveResult.path.indexOf(edge.target)) === 1;

                 return (
                    <g key={i}>
                      <line 
                        x1={n1.x} y1={n1.y} 
                        x2={n2.x} y2={n2.y} 
                        stroke={isSolution ? "#4f46e5" : "#94a3b8"} 
                        strokeWidth={isSolution ? 4 : 2} 
                        className={isSolution ? "transition-all duration-500 ease-in-out drop-shadow-[0_0_8px_rgba(79,70,229,0.5)]" : "transition-all"}
                      />
                      <rect 
                         x={(n1.x + n2.x)/2 - 16} y={(n1.y + n2.y)/2 - 10} 
                         width={32} height={20} rx={4}
                         fill="white" className="dark:fill-slate-800 pointer-events-auto shadow-sm"
                      />
                      <text 
                         x={(n1.x + n2.x)/2} y={(n1.y + n2.y)/2 + 4} 
                         textAnchor="middle" fill="#64748b" fontSize="10" className="dark:fill-slate-400 font-medium"
                      >
                         {edge.weight}
                      </text>
                    </g>
                 )
              })}
            </svg>

            {/* Nodes Layer */}
            {nodes.map(n => {
              const isStart = n.id === startNode;
              const isGoal = n.id === goalNode;
              const isSelected = n.id === selectedEdgeNode;
              const isPath = solveResult?.path && solveResult.path.includes(n.id);

              return (
                <div 
                  key={n.id}
                  onClick={(e) => handleNodeClick(e, n.id)}
                  className={cn(
                    "absolute w-12 h-12 -ml-6 -mt-6 rounded-full flex flex-col items-center justify-center transition-all cursor-pointer select-none group shadow-sm z-10 border-2",
                    isStart ? "bg-emerald-100 border-emerald-500 text-emerald-700" :
                    isGoal ? "bg-rose-100 border-rose-500 text-rose-700" :
                    isPath ? "bg-indigo-100 border-indigo-500 text-indigo-700" :
                    isSelected ? "bg-amber-100 border-amber-500 text-amber-700 scale-110" :
                    "bg-white border-slate-300 text-slate-700 hover:border-slate-400 hover:shadow-md dark:bg-slate-800 dark:border-slate-600 dark:text-slate-200"
                  )}
                  style={{ left: n.x, top: n.y }}
                >
                  <span className="font-bold">{n.id}</span>
                  {/* Tooltip on hover showing Chebyshev h-score if calculated */}
                  <div className="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-slate-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap pointer-events-none transition-opacity">
                     {isStart ? "Start" : isGoal ? "Goal" : `Node ${n.id}`}
                     {solveResult && solveResult.steps && solveResult.steps.length > 0 && solveResult.steps[solveResult.steps.length-1].f_scores[n.id] !== undefined && (
                        ` | f=${solveResult.steps[solveResult.steps.length-1].f_scores[n.id]}`
                     )}
                  </div>
                </div>
              );
            })}
         </div>
      </div>

      {/* Results Modal */}
      <AnimatePresence>
        {showModal && solveResult && (
           <motion.div 
             initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
             className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
           >
             <motion.div 
                initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
                className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl overflow-hidden w-full max-w-2xl border border-slate-200 dark:border-slate-800"
             >
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
                   <h2 className="text-xl font-bold text-slate-800 dark:text-white">A* Solution Path</h2>
                   <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition">
                      <X size={20} />
                   </button>
                </div>
                <div className="p-6 max-h-[70vh] overflow-y-auto">
                   {solveResult.error && (
                      <div className="p-4 bg-rose-50 text-rose-600 rounded-lg border border-rose-100 dark:bg-rose-900/20 dark:border-rose-900">
                         {solveResult.error}
                      </div>
                   )}
                   {!solveResult.error && (
                      <div>
                         <div className="flex items-center gap-4 mb-8">
                            <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-center border border-slate-100 dark:border-slate-800">
                               <p className="text-sm text-slate-500 mb-1">Total Cost</p>
                               <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{solveResult.total_cost}</p>
                            </div>
                            <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-center border border-slate-100 dark:border-slate-800">
                               <p className="text-sm text-slate-500 mb-1">Steps Explored</p>
                               <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">{solveResult.steps.length}</p>
                            </div>
                         </div>

                         <h3 className="font-semibold text-slate-800 dark:text-slate-200 mb-4 text-lg">Exploration Steps</h3>
                         <div className="space-y-4">
                            {solveResult.steps.map((step: any, idx: number) => (
                               <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm relative pl-12">
                                  <div className="absolute left-4 top-5 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs ring-4 ring-white dark:ring-slate-800">
                                     {idx + 1}
                                  </div>
                                  <p className="font-medium text-slate-800 dark:text-slate-200 mb-2">Visiting Node <span className="text-indigo-600">{step.current_node}</span></p>
                                  <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                                     <div>
                                        <p className="text-slate-500 dark:text-slate-400 mb-1">Open Set</p>
                                        <div className="flex flex-wrap gap-1">
                                           {step.open_set.length > 0 ? step.open_set.map((n: string) => (
                                              <span key={n} className="px-2 py-0.5 rounded bg-amber-100 text-amber-700 text-xs font-mono">{n} (f:{step.f_scores[n]})</span>
                                           )) : <span className="text-slate-400 italic">empty</span>}
                                        </div>
                                     </div>
                                     <div>
                                        <p className="text-slate-500 dark:text-slate-400 mb-1">Closed Set</p>
                                        <div className="flex flex-wrap gap-1">
                                           {step.closed_set.length > 0 ? step.closed_set.map((n: string) => (
                                              <span key={n} className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 text-xs font-mono">{n}</span>
                                           )) : <span className="text-slate-400 italic">empty</span>}
                                        </div>
                                     </div>
                                  </div>
                               </div>
                            ))}
                         </div>
                         
                         <div className="mt-8 p-5 bg-indigo-50 border border-indigo-100 dark:bg-indigo-900/20 dark:border-indigo-800/30 rounded-xl">
                            <h3 className="font-semibold text-indigo-900 dark:text-indigo-300 mb-3 text-lg">Final Path</h3>
                            <div className="flex flex-wrap items-center gap-2">
                               {solveResult.path.map((n: string, i: number) => (
                                  <div key={i} className="flex items-center gap-2">
                                     <div className="w-10 h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-lg shadow-indigo-600/20">
                                        {n}
                                     </div>
                                     {i < solveResult.path.length - 1 && <ArrowRight className="text-indigo-400" size={20} />}
                                  </div>
                               ))}
                            </div>
                         </div>
                      </div>
                   )}
                </div>
             </motion.div>
           </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ToolButton({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 w-full p-2.5 rounded-lg transition-all text-sm font-medium",
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
