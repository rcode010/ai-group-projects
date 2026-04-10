import { useState, useRef, useEffect, useCallback } from 'react';
import Grid from './components/Grid';
import NodeForm from './components/NodeForm';
import StepsViewer from './components/StepsViewer';
import { solvePath } from './api';
import './index.css';

const GRID_SIZE = 40;

const DEFAULT_NODES = [
  { id: 'S', x: 200, y: 160 },
  { id: 'A', x: 280, y: 320 },
  { id: 'B', x: 440, y: 240 },
  { id: 'C', x: 360, y: 400 },
  { id: 'G', x: 520, y: 480 },
];
const DEFAULT_EDGES = [
  { source: 'S', target: 'A', weight: 1 },
  { source: 'S', target: 'B', weight: 1 },
  { source: 'A', target: 'C', weight: 1 },
  { source: 'B', target: 'C', weight: 1 },
  { source: 'C', target: 'G', weight: 1 },
];

function getNextId(nodes) {
  const reserved = new Set(['S', 'G']);
  const used = new Set(nodes.map(n => n.id));
  for (let i = 65; i <= 90; i++) {
    const ch = String.fromCharCode(i);
    if (!reserved.has(ch) && !used.has(ch)) return ch;
  }
  return `N${nodes.length}`;
}

function snapToGrid(val) {
  return Math.round(val / GRID_SIZE) * GRID_SIZE;
}

export default function App() {
  const [nodes, setNodes] = useState(DEFAULT_NODES);
  const [edges, setEdges] = useState(DEFAULT_EDGES);

  const [mode, setMode] = useState('add_node');
  const [startNode, setStartNode] = useState('S');
  const [goalNode, setGoalNode] = useState('G');
  const [selectedEdgeNode, setSelectedEdgeNode] = useState(null);
  const [solveResult, setSolveResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [solving, setSolving] = useState(false);
  const [error, setError] = useState(null);

  // Drag state (for select mode)
  const dragRef = useRef(null); // { nodeId, startX, startY, origX, origY }
  const boardRef = useRef(null);

  // ── Board click: add node ──────────────────────────────────────────────
  const handleBoardClick = (e) => {
    if (!boardRef.current) return;
    if (mode !== 'add_node') return;

    const rect = boardRef.current.getBoundingClientRect();
    const x = snapToGrid(e.clientX - rect.left);
    const y = snapToGrid(e.clientY - rect.top);

    if (nodes.some(n => Math.abs(n.x - x) < 20 && Math.abs(n.y - y) < 20)) return;

    const newId = getNextId(nodes);
    setNodes(prev => [...prev, { id: newId, x, y }]);
  };

  // ── Node left-click ────────────────────────────────────────────────────
  const handleNodeClick = (e, id) => {
    e.stopPropagation();
    if (mode === 'add_edge') {
      if (!selectedEdgeNode) {
        setSelectedEdgeNode(id);
      } else {
        if (selectedEdgeNode !== id) {
          const alreadyExists = edges.some(
            ed => (ed.source === selectedEdgeNode && ed.target === id) ||
                  (ed.source === id && ed.target === selectedEdgeNode)
          );
          if (!alreadyExists) {
            setEdges(prev => [...prev, { source: selectedEdgeNode, target: id, weight: 1 }]);
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

  // ── Node right-click: delete (select mode only) ────────────────────────
  const handleNodeRightClick = (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    if (mode !== 'select') return;
    setNodes(prev => prev.filter(n => n.id !== id));
    setEdges(prev => prev.filter(ed => ed.source !== id && ed.target !== id));
    if (startNode === id) setStartNode(null);
    if (goalNode === id) setGoalNode(null);
    setSolveResult(null);
  };

  // ── Drag: start ────────────────────────────────────────────────────────
  const handleNodeMouseDown = useCallback((e, id) => {
    if (mode !== 'select') return;
    if (e.button !== 0) return; // left button only
    e.stopPropagation();
    e.preventDefault();

    const rect = boardRef.current.getBoundingClientRect();
    const node = nodes.find(n => n.id === id);
    if (!node) return;

    dragRef.current = {
      nodeId: id,
      startMouseX: e.clientX,
      startMouseY: e.clientY,
      origX: node.x,
      origY: node.y,
      rect,
    };
  }, [mode, nodes]);

  // ── Drag: move ─────────────────────────────────────────────────────────
  useEffect(() => {
    const onMouseMove = (e) => {
      if (!dragRef.current) return;
      const { nodeId, startMouseX, startMouseY, origX, origY, rect } = dragRef.current;
      const dx = e.clientX - startMouseX;
      const dy = e.clientY - startMouseY;
      const newX = Math.max(GRID_SIZE, Math.min(rect.width - GRID_SIZE, snapToGrid(origX + dx)));
      const newY = Math.max(GRID_SIZE, Math.min(rect.height - GRID_SIZE, snapToGrid(origY + dy)));
      setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, x: newX, y: newY } : n));
    };

    const onMouseUp = () => {
      dragRef.current = null;
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);

  // ── Solve ──────────────────────────────────────────────────────────────
  const handleSolve = async () => {
    if (!startNode || !goalNode) {
      setError('Please set a Start and Goal node first.');
      return;
    }
    if (nodes.length < 2) {
      setError('Please add at least 2 nodes.');
      return;
    }
    setError(null);
    setSolving(true);
    try {
      const data = await solvePath(nodes, edges, startNode, goalNode);
      setSolveResult(data);
      setShowModal(true);
    } catch (err) {
      setError(err.message || 'Error contacting the backend.');
    } finally {
      setSolving(false);
    }
  };

  // ── Clear ──────────────────────────────────────────────────────────────
  const handleClear = () => {
    setNodes(DEFAULT_NODES);
    setEdges(DEFAULT_EDGES);
    setStartNode('S');
    setGoalNode('G');
    setSolveResult(null);
    setShowModal(false);
    setError(null);
    setSelectedEdgeNode(null);
    setMode('add_node');
  };

  // ── Escape cancels edge selection ──────────────────────────────────────
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') setSelectedEdgeNode(null);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 font-sans overflow-hidden">
      <NodeForm
        mode={mode}
        setMode={setMode}
        onSolve={handleSolve}
        onClear={handleClear}
        solving={solving}
        error={error}
        startNode={startNode}
        goalNode={goalNode}
        nodeCount={nodes.length}
        edgeCount={edges.length}
      />

      <div className="flex-1 relative overflow-hidden">
        <Grid
          nodes={nodes}
          edges={edges}
          mode={mode}
          startNode={startNode}
          goalNode={goalNode}
          selectedEdgeNode={selectedEdgeNode}
          solveResult={solveResult}
          onBoardClick={handleBoardClick}
          onNodeClick={handleNodeClick}
          onNodeRightClick={handleNodeRightClick}
          onNodeMouseDown={handleNodeMouseDown}
          boardRef={boardRef}
        />
      </div>

      <StepsViewer
        show={showModal}
        solveResult={solveResult}
        onClose={() => setShowModal(false)}
      />
    </div>
  );
}