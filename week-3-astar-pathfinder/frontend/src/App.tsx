import { useState, useRef, useCallback, type MouseEvent, useEffect } from 'react';
import { MousePointer2, Plus, ArrowRight, Flag, Play, X, RotateCcw, Trash2 } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type Mode = 'select' | 'add_node' | 'add_edge' | 'set_start' | 'set_goal';

const GRID_SIZE = 40;

// Chebyshev distance (same formula as backend)
function chebyshev(x1: number, y1: number, x2: number, y2: number): number {
  return Math.max(Math.abs(x1 - x2), Math.abs(y1 - y2));
}

export default function App() {
  const [nodes, setNodes] = useState<{ id: string; x: number; y: number; weight: number }[]>([]);
  const [edges, setEdges] = useState<{ source: string; target: string; weight: number }[]>([]);

  const [mode, setMode] = useState<Mode>('add_node');
  const [startNode, setStartNode] = useState<string | null>(null);
  const [goalNode, setGoalNode] = useState<string | null>(null);

  const [selectedEdgeNode, setSelectedEdgeNode] = useState<string | null>(null);
  const boardRef = useRef<HTMLDivElement>(null);

  const [solveResult, setSolveResult] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [solving, setSolving] = useState(false);

  // Drag state for select mode
  const dragRef = useRef<{
    nodeId: string;
    startMouseX: number;
    startMouseY: number;
    origX: number;
    origY: number;
    hasMoved: boolean;
  } | null>(null);

  // ── Helper: next node ID ─────────────────────────────────────────────
  function getNextId(): string {
    const reserved = new Set(['S', 'G']);
    const used = new Set(nodes.map(n => n.id));
    for (let i = 65; i <= 90; i++) {
      const ch = String.fromCharCode(i);
      if (!reserved.has(ch) && !used.has(ch)) return ch;
    }
    return `N${nodes.length}`;
  }

  function snapToGrid(val: number): number {
    return Math.round(val / GRID_SIZE) * GRID_SIZE;
  }

  // ── Board click: add node ────────────────────────────────────────────
  const handleBoardClick = (e: MouseEvent<HTMLDivElement>) => {
    if (!boardRef.current) return;
    if (mode !== 'add_node') return;

    const rect = boardRef.current.getBoundingClientRect();
    const x = snapToGrid(e.clientX - rect.left);
    const y = snapToGrid(e.clientY - rect.top);

    if (nodes.some(n => Math.abs(n.x - x) < 20 && Math.abs(n.y - y) < 20)) return;

    const newNodeId = nodes.length === 0 ? 'S' : (nodes.length === 1 && !goalNode ? 'G' : getNextId());

    const weightInput = window.prompt(`Enter weight for node ${newNodeId}:`, '1');
    if (weightInput === null) return; // user cancelled
    const parsedWeight = parseInt(weightInput);
    const nodeWeight = isNaN(parsedWeight) ? 1 : parsedWeight;

    setNodes(prev => [...prev, { id: newNodeId, x, y, weight: nodeWeight }]);
    if (newNodeId === 'S') setStartNode('S');
    if (newNodeId === 'G') setGoalNode('G');
  };

  // ── Node left-click ──────────────────────────────────────────────────
  const handleNodeClick = (e: MouseEvent, id: string) => {
    e.stopPropagation();

    // If we're dragging and moved, don't trigger click actions
    if (dragRef.current && dragRef.current.hasMoved) return;

    if (mode === 'add_edge') {
      if (!selectedEdgeNode) {
        setSelectedEdgeNode(id);
      } else {
        if (selectedEdgeNode !== id) {
          const n1 = nodes.find(n => n.id === selectedEdgeNode)!;
          const n2 = nodes.find(n => n.id === id)!;
          const dist = Math.sqrt(Math.pow(n1.x - n2.x, 2) + Math.pow(n1.y - n2.y, 2));
          if (!edges.some(e => (e.source === n1.id && e.target === n2.id) || (e.source === n2.id && e.target === n1.id))) {
            const defaultWeight = Math.round(dist);
            const inputWeight = window.prompt(`Enter weight for edge ${n1.id} → ${n2.id}:`, defaultWeight.toString());
            if (inputWeight === null) {
              setSelectedEdgeNode(null);
              return;
            }
            const finalWeight = parseInt(inputWeight);
            setEdges(prev => [...prev, { source: n1.id, target: n2.id, weight: isNaN(finalWeight) ? defaultWeight : finalWeight }]);
          }
        }
        setSelectedEdgeNode(null);
      }
    } else if (mode === 'set_start') {
      setStartNode(id);
      setMode('add_node');
    } else if (mode === 'set_goal') {
      setGoalNode(id);
      setMode('add_node');
    }
  };

  // ── Node right-click: delete (select mode) ───────────────────────────
  const handleNodeRightClick = (e: MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (mode !== 'select') return;
    setNodes(prev => prev.filter(n => n.id !== id));
    setEdges(prev => prev.filter(ed => ed.source !== id && ed.target !== id));
    if (startNode === id) setStartNode(null);
    if (goalNode === id) setGoalNode(null);
    setSolveResult(null);
  };

  // ── Drag: start ──────────────────────────────────────────────────────
  const handleNodeMouseDown = useCallback((e: MouseEvent, id: string) => {
    if (mode !== 'select') return;
    if (e.button !== 0) return; // left button only
    e.stopPropagation();
    e.preventDefault();

    const node = nodes.find(n => n.id === id);
    if (!node) return;

    dragRef.current = {
      nodeId: id,
      startMouseX: e.clientX,
      startMouseY: e.clientY,
      origX: node.x,
      origY: node.y,
      hasMoved: false,
    };
  }, [mode, nodes]);

  // ── Drag: move + release ─────────────────────────────────────────────
  useEffect(() => {
    const onMouseMove = (e: globalThis.MouseEvent) => {
      if (!dragRef.current || !boardRef.current) return;
      const { nodeId, startMouseX, startMouseY, origX, origY } = dragRef.current;
      const dx = e.clientX - startMouseX;
      const dy = e.clientY - startMouseY;

      // Only start "moving" after a small threshold to avoid accidental drags
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        dragRef.current.hasMoved = true;
      }

      const rect = boardRef.current.getBoundingClientRect();
      const newX = Math.max(GRID_SIZE, Math.min(rect.width - GRID_SIZE, snapToGrid(origX + dx)));
      const newY = Math.max(GRID_SIZE, Math.min(rect.height - GRID_SIZE, snapToGrid(origY + dy)));
      setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, x: newX, y: newY } : n));
    };

    const onMouseUp = () => {
      if (dragRef.current) {
        dragRef.current = null;
      }
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);

  // ── Solve ─────────────────────────────────────────────────────────────
  const handleSolve = async () => {
    if (!startNode || !goalNode) {
      alert("Please set a Start and Goal node.");
      return;
    }
    if (nodes.length < 2) {
      alert("Please add at least 2 nodes.");
      return;
    }
    setSolving(true);
    try {
      const resp = await fetch('http://localhost:8000/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nodes: nodes.map(n => ({ ...n, weight: n.weight ?? 1 })),
          edges,
          start_node: startNode,
          goal_node: goalNode,
        })
      });
      const data = await resp.json();
      if (!resp.ok) {
        setSolveResult({ error: data.detail || "An unexpected error occurred." });
      } else {
        setSolveResult(data);
      }
      setShowModal(true);
    } catch {
      alert("Error contacting the backend. Make sure it is running on port 8000.");
    } finally {
      setSolving(false);
    }
  };

  // ── Clear ─────────────────────────────────────────────────────────────
  const handleClear = () => {
    setNodes([]);
    setEdges([]);
    setStartNode(null);
    setGoalNode(null);
    setSolveResult(null);
    setShowModal(false);
    setSelectedEdgeNode(null);
    setMode('add_node');
  };

  // ── Escape cancels edge selection ─────────────────────────────────────
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedEdgeNode(null);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  // ── Compute Chebyshev h-cost for each node (shown on board) ──────────
  const goalNodeData = nodes.find(n => n.id === goalNode);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 font-sans overflow-hidden">
      {/* ─── Sidebar Toolbar ─── */}
      <div className="w-16 md:w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col p-2 md:p-4 shadow-sm z-10 transition-all">
        <div className="hidden md:flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-600/20">A*</div>
          <h1 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Path Finder</h1>
        </div>

        <div className="flex flex-col gap-2 flex-grow">
          <ToolButton icon={<MousePointer2 size={18} />} label="Select / Move" active={mode === 'select'} onClick={() => setMode('select')} />
          <ToolButton icon={<Plus size={18} />} label="Add Node" active={mode === 'add_node'} onClick={() => setMode('add_node')} />
          <ToolButton icon={<ArrowRight size={18} />} label="Add Edge" active={mode === 'add_edge'} onClick={() => setMode('add_edge')} />
          <div className="h-px bg-slate-200 dark:bg-slate-800 my-2" />
          <ToolButton icon={<Flag size={18} className="text-emerald-500" />} label="Set Start" active={mode === 'set_start'} onClick={() => setMode('set_start')} />
          <ToolButton icon={<Flag size={18} className="text-rose-500" />} label="Set Goal" active={mode === 'set_goal'} onClick={() => setMode('set_goal')} />
        </div>

        {/* Node & Edge Counts */}
        <div className="hidden md:flex flex-col gap-1 mb-4 text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800 pt-3">
          <span>Nodes: <b className="text-slate-700 dark:text-slate-200">{nodes.length}</b></span>
          <span>Edges: <b className="text-slate-700 dark:text-slate-200">{edges.length}</b></span>
          {startNode && <span>Start: <b className="text-emerald-600">{startNode}</b></span>}
          {goalNode && <span>Goal: <b className="text-rose-600">{goalNode}</b></span>}
        </div>

        {/* Mode Tip */}
        {mode === 'select' && (
          <div className="hidden md:block text-xs text-slate-400 mb-3 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <b>Drag</b> to move nodes<br />
            <b>Right-click</b> to delete
          </div>
        )}
        {mode === 'add_edge' && selectedEdgeNode && (
          <div className="hidden md:block text-xs text-amber-600 mb-3 p-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
            Click another node to create edge from <b>{selectedEdgeNode}</b>
          </div>
        )}

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

      {/* ─── Main Board ─── */}
      <div className="flex-1 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
        <div
          ref={boardRef}
          onClick={handleBoardClick}
          className={cn(
            "absolute inset-0 overflow-hidden",
            mode === 'select' ? "cursor-default" : "cursor-crosshair"
          )}
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
                    x={(n1.x + n2.x) / 2 - 16} y={(n1.y + n2.y) / 2 - 10}
                    width={32} height={20} rx={4}
                    fill="white" className="dark:fill-slate-800 pointer-events-auto shadow-sm"
                  />
                  <text
                    x={(n1.x + n2.x) / 2} y={(n1.y + n2.y) / 2 + 4}
                    textAnchor="middle" fill="#64748b" fontSize="10" className="dark:fill-slate-400 font-medium"
                  >
                    {edge.weight}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Nodes Layer */}
          {nodes.map(n => {
            const isStart = n.id === startNode;
            const isGoal = n.id === goalNode;
            const isSelected = n.id === selectedEdgeNode;
            const isPath = solveResult?.path && solveResult.path.includes(n.id);

            // Chebyshev h-cost from this node to goal
            const hCost = goalNodeData && n.id !== goalNode
              ? chebyshev(n.x, n.y, goalNodeData.x, goalNodeData.y)
              : null;

            return (
              <div
                key={n.id}
                onClick={(e) => handleNodeClick(e, n.id)}
                onContextMenu={(e) => handleNodeRightClick(e, n.id)}
                onMouseDown={(e) => handleNodeMouseDown(e, n.id)}
                className={cn(
                  "absolute w-14 h-14 -ml-7 -mt-7 rounded-full flex flex-col items-center justify-center cursor-pointer select-none group z-10 border-2 transition-shadow",
                  mode === 'select' && "cursor-grab active:cursor-grabbing",
                  isStart ? "bg-emerald-100 border-emerald-500 text-emerald-700 shadow-md shadow-emerald-200" :
                  isGoal ? "bg-rose-100 border-rose-500 text-rose-700 shadow-md shadow-rose-200" :
                  isPath ? "bg-indigo-100 border-indigo-500 text-indigo-700 shadow-md shadow-indigo-200" :
                  isSelected ? "bg-amber-100 border-amber-500 text-amber-700 scale-110 shadow-lg" :
                  "bg-white border-slate-300 text-slate-700 hover:border-slate-400 hover:shadow-md dark:bg-slate-800 dark:border-slate-600 dark:text-slate-200"
                )}
                style={{ left: n.x, top: n.y }}
              >
                <span className="font-bold text-sm">{n.id}</span>
                <span className="text-[9px] font-mono opacity-75 leading-none">w={n.weight ?? 1}</span>
                {/* Show Chebyshev h(n) below the node label */}
                {hCost !== null && (
                  <span className="text-[9px] font-mono opacity-70 leading-none">h={hCost}</span>
                )}

                {/* Tooltip on hover */}
                <div className="absolute -top-14 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-slate-900 text-white text-xs px-2.5 py-1.5 rounded-lg whitespace-nowrap pointer-events-none transition-opacity shadow-lg z-50">
                  {isStart ? "Start (S)" : isGoal ? "Goal (G)" : `Node ${n.id}`}
                  {` • weight=${n.weight ?? 1}`}
                  {hCost !== null && ` • h=${hCost}`}
                  <span className="block text-slate-400 text-[10px]">({n.x}, {n.y})</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ─── Results Modal (Solution Window) ─── */}
      <AnimatePresence>
        {showModal && solveResult && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
              className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl overflow-hidden w-full max-w-3xl border border-slate-200 dark:border-slate-800"
            >
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
                <h2 className="text-xl font-bold text-slate-800 dark:text-white">A* Solution — Chebyshev Distance</h2>
                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition">
                  <X size={20} />
                </button>
              </div>
              <div className="p-6 max-h-[75vh] overflow-y-auto">
                {solveResult.error && (
                  <div className="p-4 bg-rose-50 text-rose-600 rounded-lg border border-rose-100 dark:bg-rose-900/20 dark:border-rose-900">
                    {solveResult.error}
                  </div>
                )}
                {!solveResult.error && (
                  <div>
                    {/* Summary Stats */}
                    <div className="flex items-center gap-4 mb-8">
                      <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-center border border-slate-100 dark:border-slate-800">
                        <p className="text-sm text-slate-500 mb-1">Total Cost</p>
                        <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{solveResult.total_cost}</p>
                      </div>
                      <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-center border border-slate-100 dark:border-slate-800">
                        <p className="text-sm text-slate-500 mb-1">Steps Explored</p>
                        <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">{solveResult.steps.length}</p>
                      </div>
                      <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-center border border-slate-100 dark:border-slate-800">
                        <p className="text-sm text-slate-500 mb-1">Path Length</p>
                        <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">{solveResult.path.length} nodes</p>
                      </div>
                    </div>

                    {/* Step-by-step Exploration (as shown in lectures) */}
                    <h3 className="font-semibold text-slate-800 dark:text-slate-200 mb-4 text-lg">Step-by-Step Exploration</h3>
                    <div className="space-y-4">
                      {solveResult.steps.map((step: any, idx: number) => (
                        <div key={idx} className={cn(
                          "p-4 rounded-xl border shadow-sm relative pl-14",
                          step.goal_reached
                            ? "border-emerald-300 bg-emerald-50 dark:bg-emerald-900/20 dark:border-emerald-700"
                            : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                        )}>
                          <div className={cn(
                            "absolute left-4 top-5 w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ring-4",
                            step.goal_reached
                              ? "bg-emerald-500 text-white ring-emerald-50 dark:ring-emerald-900/20"
                              : "bg-indigo-100 text-indigo-600 ring-white dark:ring-slate-800"
                          )}>
                            {idx + 1}
                          </div>

                          <p className="font-medium text-slate-800 dark:text-slate-200 mb-1">
                            Visiting Node <span className="text-indigo-600 font-bold">{step.current_node}</span>
                            {step.goal_reached && <span className="ml-2 text-emerald-600 font-semibold">✓ Goal Reached!</span>}
                          </p>

                          {/* g, h, f breakdown */}
                          <div className="flex gap-3 mb-3 flex-wrap">
                            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-xs font-mono dark:bg-slate-700 dark:text-slate-300">
                              node_weight={step.node_weight ?? 0}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-mono dark:bg-blue-900/30 dark:text-blue-300">
                              g={step.g}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-purple-100 text-purple-700 text-xs font-mono dark:bg-purple-900/30 dark:text-purple-300">
                              h={step.h}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 text-xs font-mono font-bold dark:bg-indigo-900/30 dark:text-indigo-300">
                              f={step.f}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-slate-500 dark:text-slate-400 mb-1 font-medium">Open Set</p>
                              <div className="flex flex-wrap gap-1">
                                {step.open_set.length > 0 ? step.open_set.map((n: string) => (
                                  <span key={n} className="px-2 py-0.5 rounded bg-amber-100 text-amber-700 text-xs font-mono dark:bg-amber-900/30 dark:text-amber-300">
                                    {n} (f={step.f_scores?.[n] ?? '?'})
                                  </span>
                                )) : <span className="text-slate-400 italic text-xs">empty</span>}
                              </div>
                            </div>
                            <div>
                              <p className="text-slate-500 dark:text-slate-400 mb-1 font-medium">Closed Set</p>
                              <div className="flex flex-wrap gap-1">
                                {step.closed_set.length > 0 ? step.closed_set.map((n: string) => (
                                  <span key={n} className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 text-xs font-mono dark:bg-emerald-900/30 dark:text-emerald-300">
                                    {n}
                                  </span>
                                )) : <span className="text-slate-400 italic text-xs">empty</span>}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Final Path */}
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
                      <p className="mt-3 text-sm text-indigo-700 dark:text-indigo-400 font-mono">
                        Path: {solveResult.path.join(' → ')} | Total Cost: {solveResult.total_cost}
                      </p>
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

function ToolButton({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
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
