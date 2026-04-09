import React from 'react';
import { cn } from '../utils';

const GRID_SIZE = 40;

export default function Grid({ nodes, edges, mode, startNode, goalNode, selectedEdgeNode, solveResult, onBoardClick, onNodeClick, boardRef }) {
  return (
    <div 
      ref={boardRef}
      onClick={onBoardClick}
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

        let chebyshevCost = "";
        if (goalNode) {
          const gNode = nodes.find(gn => gn.id === goalNode);
          if (gNode) {
            const dx = Math.abs(n.x - gNode.x) / GRID_SIZE;
            const dy = Math.abs(n.y - gNode.y) / GRID_SIZE;
            chebyshevCost = Math.max(dx, dy);
          }
        }

        return (
          <div 
            key={n.id}
            onClick={(e) => onNodeClick(e, n.id)}
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
            {chebyshevCost !== "" && <span className="text-[10px] -mt-1 font-mono opacity-80">h={chebyshevCost}</span>}
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-slate-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap pointer-events-none transition-opacity">
              {isStart ? "Start" : isGoal ? "Goal" : `Node ${n.id}`}
              {solveResult && solveResult.steps?.length > 0 && solveResult.steps[solveResult.steps.length-1].h_scores?.[n.id] !== undefined && (
                ` | h=${solveResult.steps[solveResult.steps.length-1].h_scores[n.id]}`
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
