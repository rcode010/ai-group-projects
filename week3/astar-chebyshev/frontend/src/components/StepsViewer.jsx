import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight } from 'lucide-react';

export default function StepsViewer({ show, solveResult, onClose }) {
  if (!show || !solveResult) return null;

  return (
    <AnimatePresence>
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
              <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition">
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
                          <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">{solveResult.steps?.length}</p>
                       </div>
                    </div>

                    <h3 className="font-semibold text-slate-800 dark:text-slate-200 mb-4 text-lg">Exploration Steps</h3>
                    <div className="space-y-4">
                       {solveResult.steps?.map((step, idx) => (
                          <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm relative pl-12">
                             <div className="absolute left-4 top-5 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs ring-4 ring-white dark:ring-slate-800">
                                {idx + 1}
                             </div>
                             <p className="font-medium text-slate-800 dark:text-slate-200 mb-2">Visiting Node <span className="text-indigo-600">{step.current_node}</span></p>
                             <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                                <div>
                                   <p className="text-slate-500 dark:text-slate-400 mb-1">Open Set</p>
                                   <div className="flex flex-wrap gap-1">
                                      {step.open_set?.length > 0 ? step.open_set.map((n) => (
                                         <span key={n} className="px-2 py-0.5 rounded bg-amber-100 text-amber-700 text-xs font-mono">{n} (f:{step.f_scores[n]})</span>
                                      )) : <span className="text-slate-400 italic">empty</span>}
                                   </div>
                                </div>
                                <div>
                                   <p className="text-slate-500 dark:text-slate-400 mb-1">Closed Set</p>
                                   <div className="flex flex-wrap gap-1">
                                      {step.closed_set?.length > 0 ? step.closed_set.map((n) => (
                                         <span key={n} className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 text-xs font-mono">{n}</span>
                                      )) : <span className="text-slate-400 italic">empty</span>}
                                   </div>
                                </div>
                             </div>
                          </div>
                       ))}
                    </div>
                    
                    {solveResult.path && (
                      <div className="mt-8 p-5 bg-indigo-50 border border-indigo-100 dark:bg-indigo-900/20 dark:border-indigo-800/30 rounded-xl">
                          <h3 className="font-semibold text-indigo-900 dark:text-indigo-300 mb-3 text-lg">Final Path</h3>
                          <div className="flex flex-wrap items-center gap-2">
                            {solveResult.path.map((n, i) => (
                                <div key={i} className="flex items-center gap-2">
                                  <div className="w-10 h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-lg shadow-indigo-600/20">
                                      {n}
                                  </div>
                                  {i < solveResult.path.length - 1 && <ArrowRight className="text-indigo-400" size={20} />}
                                </div>
                            ))}
                          </div>
                      </div>
                    )}
                 </div>
              )}
           </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
