import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RemediationForm from './components/RemediationForm';
import StatusView from './components/StatusView';
import { Shield } from 'lucide-react';

const queryClient = new QueryClient();

function App() {
    const [workflowId, setWorkflowId] = useState(null);

    return (
        <QueryClientProvider client={queryClient}>
            <div className="min-h-screen text-slate-200 p-8 font-sans selection:bg-indigo-500/30">
                <header className="max-w-4xl mx-auto mb-12 flex items-center justify-between border-b border-white/5 pb-6">
                    <div className="flex items-center gap-4">
                        <div className="p-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
                            <Shield className="text-indigo-400 w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                                Sentinel_Code
                                <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-2 py-0.5 rounded-full border border-indigo-500/30 font-medium">BETA</span>
                            </h1>
                            <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-mono">Automated Vulnerability Remediation</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 text-xs rounded-full border border-emerald-500/20 backdrop-blur-md font-medium shadow-[0_0_10px_rgba(16,185,129,0.1)]">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            SYSTEM ONLINE
                        </div>
                    </div>
                </header>

                <main className="max-w-4xl mx-auto space-y-8 relative z-10">
                    {!workflowId ? (
                        <RemediationForm onStart={setWorkflowId} />
                    ) : (
                        <div className="space-y-6">
                            <button
                                onClick={() => setWorkflowId(null)}
                                className="inline-flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors hover:bg-white/5 px-3 py-1.5 rounded-lg -ml-3"
                            >
                                ← Return to Mission Control
                            </button>
                            <StatusView workflowId={workflowId} />
                        </div>
                    )}
                </main>
            </div>
        </QueryClientProvider>
    );
}

export default App;
