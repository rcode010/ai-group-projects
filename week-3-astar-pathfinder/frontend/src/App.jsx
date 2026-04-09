import { useState, useRef, useEffect } from 'react';
import Grid from './components/Grid';
import NodeForm from './components/NodeForm';
import StepsViewer from './components/StepsViewer';
import { solvePath } from './api';

const GRID_SIZE = 40;

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  
  const [mode, setMode] = useState('add_node');
  const [startNode, setStartNode] = useState(null);
  const [goalNode, setGoalNode] = useState(null);

  const [selectedEdgeNode, setSelectedEdgeNode] = useState(null);
  const boardRef = useRef(null);

  const [solveResult, setSolveResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [solving, setSolving] = useState(false);
  
  const nextNodeId = String.fromCharCode(65 + nodes.length);

  const handleBoardClick = (e) => {
    if (!boardRef.current) return;
    const rect = boardRef.current.getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) / GRID_SIZE) * GRID_SIZE;
    const y = Math.round((e.clientY - rect.top) / GRID_SIZE) * GRID_SIZE;

    if (mode === 'add_node') {
      if (nodes.some(n => Math.abs(n.x - x) < 20 && Math.abs(n.y - y) < 20)) return;
      
      const newNodeId = nodes.length === 0 ? 'S' : (nodes.length === 1 && !goalNode ? 'G' : nextNodeId);
      setNodes([...nodes, { id: newNodeId, x, y }]);
      if (newNodeId === 'S') setStartNode('S');
      if (newNodeId === 'G') setGoalNode('G');
    }
  };

  const handleNodeClick = (e, id) => {
    e.stopPropagation();
    if (mode === 'add_edge') {
      if (!selectedEdgeNode) {
        setSelectedEdgeNode(id);
      } else {
        if (selectedEdgeNode !== id) {
          const n1 = nodes.find(n => n.id === selectedEdgeNode);
          const n2 = nodes.find(n => n.id === id);
          if (n1 && n2) {
            const dist = Math.sqrt(Math.pow(n1.x - n2.x, 2) + Math.pow(n1.y - n2.y, 2));
            if (!edges.some(e => (e.source === n1.id && e.target === n2.id) || (e.source === n2.id && e.target === n1.id))) {
              setEdges([...edges, { source: n1.id, target: n2.id, weight: Math.round(dist) }]);
            }
          }
        }
        setSelectedEdgeNode(null);
      }
    } else if (mode === 'set_start') {
      setStartNode(id);
    } else if (mode === 'set_goal') {
      setGoalNode(id);
    }
  };

  const handleSolve = async () => {
    if (!startNode || !goalNode) {
      alert("Please set a Start and Goal node.");
      return;
    }
    setSolving(true);
    try {
      const data = await solvePath(nodes, edges, startNode, goalNode);
      setSolveResult(data);
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
      />

      <div className="flex-1 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
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
