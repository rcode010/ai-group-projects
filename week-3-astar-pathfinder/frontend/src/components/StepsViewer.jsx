import React, { useState, useEffect } from 'react';
import { X, ArrowRight, ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react';
import { cn } from '../utils';

export default function StepsViewer({ show, solveResult, onClose }) {
  const [activeStep, setActiveStep] = useState(0);

  // Reset step index whenever a new result arrives
  useEffect(() => {
    setActiveStep(0);
  }, [solveResult]);

  if (!show || !solveResult) return null;

  const steps = solveResult.steps ?? [];
  const path = solveResult.path ?? [];
  const totalCost = solveResult.total_cost ?? solveResult.cost ?? 0;
  const step = steps[activeStep] ?? null;

  const prev = () => setActiveStep(s => Math.max(0, s - 1));
  const next = () => setActiveStep(s => Math.min(steps.length - 1, s + 1));

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in slide-in-from-bottom-4 duration-300">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-indigo-700 bg-indigo-600">
          <div>
            <h2 className="text-lg font-bold text-white">A* Solution</h2>
            <p className="text-indigo-200 text-xs mt-0.5">Chebyshev Distance Heuristic</p>
          </div>
          <button
            onClick={onClose}
            className="text-indigo-200 hover:text-white transition p-1.5 rounded-lg hover:bg-indigo-700"
          >
            <X size={20} />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-6 space-y-5">

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-indigo-50 border border-indigo-100 p-4 text-center">
              <p className="text-xs text-indigo-400 font-semibold uppercase tracking-wide mb-1">Total Cost</p>
              <p className="text-3xl font-black text-indigo-600">{totalCost}</p>
            </div>
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-4 text-center">
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide mb-1">Steps Explored</p>
              <p className="text-3xl font-black text-slate-700">{steps.length}</p>
            </div>
          </div>

          {/* Final path */}
          <div className="rounded-xl bg-indigo-600 p-4">
            <p className="text-indigo-200 text-xs font-semibold uppercase tracking-wide mb-3">Final Path</p>
            <div className="flex flex-wrap items-center gap-2">
              {path.map((node, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className={cn(
                    "w-9 h-9 rounded-full font-bold text-sm flex items-center justify-center shadow",
                    i === 0 ? "bg-emerald-400 text-emerald-900" :
                    i === path.length - 1 ? "bg-rose-400 text-rose-900" :
                    "bg-white text-indigo-700"
                  )}>
                    {node}
                  </div>
                  {i < path.length - 1 && (
                    <ArrowRight size={16} className="text-indigo-300" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step-by-step explorer */}
          {steps.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold text-slate-800 dark:text-slate-200 text-sm">
                  Exploration Steps
                </h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={prev}
                    disabled={activeStep === 0}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 transition"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span className="text-sm font-mono text-slate-600 min-w-[60px] text-center">
                    {activeStep + 1} / {steps.length}
                  </span>
                  <button
                    onClick={next}
                    disabled={activeStep === steps.length - 1}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 transition"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>

              {step && (
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 bg-white dark:bg-slate-800 shadow-sm space-y-4">

                  {/* Current node */}
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-12 h-12 rounded-full font-black text-lg flex items-center justify-center shadow-md flex-shrink-0",
                      step.goal_reached
                        ? "bg-rose-500 text-white"
                        : "bg-indigo-600 text-white"
                    )}>
                      {step.current_node}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-slate-800 dark:text-slate-200">
                        {step.goal_reached ? '🎯 Goal Reached!' : `Visiting Node ${step.current_node}`}
                      </p>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        <span className="text-xs font-mono bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded text-slate-600 dark:text-slate-300">
                          g = {step.g}
                        </span>
                        <span className="text-xs font-mono bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded text-slate-600 dark:text-slate-300">
                          h = {step.h}
                        </span>
                        <span className="text-xs font-mono bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded font-bold">
                          f = {step.f}
                        </span>
                      </div>
                    </div>
                    {step.goal_reached && (
                      <CheckCircle2 className="text-emerald-500 flex-shrink-0" size={24} />
                    )}
                  </div>

                  {/* Open / Closed sets */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-amber-50 border border-amber-100 p-3">
                      <p className="text-[10px] font-bold text-amber-500 uppercase tracking-wider mb-2">Open Set</p>
                      <div className="flex flex-wrap gap-1">
                        {step.open_set?.length > 0
                          ? step.open_set.map(n => (
                            <span key={n} className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 text-xs font-mono">
                              {n}
                              {step.f_scores?.[n] !== undefined && (
                                <span className="opacity-60 ml-1">f:{step.f_scores[n]}</span>
                              )}
                            </span>
                          ))
                          : <span className="text-slate-400 text-xs italic">empty</span>
                        }
                      </div>
                    </div>

                    <div className="rounded-lg bg-emerald-50 border border-emerald-100 p-3">
                      <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider mb-2">Closed Set</p>
                      <div className="flex flex-wrap gap-1">
                        {step.closed_set?.length > 0
                          ? step.closed_set.map(n => (
                            <span key={n} className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-xs font-mono">
                              {n}
                            </span>
                          ))
                          : <span className="text-slate-400 text-xs italic">empty</span>
                        }
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step dots */}
              <div className="flex justify-center gap-1.5 mt-3 flex-wrap">
                {steps.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveStep(i)}
                    title={`Step ${i + 1}`}
                    className={cn(
                      "rounded-full transition-all",
                      i === activeStep
                        ? "w-5 h-2 bg-indigo-600"
                        : "w-2 h-2 bg-slate-300 hover:bg-slate-400"
                    )}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}