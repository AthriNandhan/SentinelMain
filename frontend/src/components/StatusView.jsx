import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getStatus } from '../services/api';
import { Shield, ShieldAlert, ShieldCheck, Activity, Terminal } from 'lucide-react';

const StatusView = ({ workflowId }) => {
    const { data, error, isLoading } = useQuery({
        queryKey: ['workflow', workflowId],
        queryFn: () => getStatus(workflowId),
        // keep polling only while workflow is in progress
        refetchInterval: (query) => {
            const currentData = query.state.data;
            return (currentData && currentData.state && currentData.state.verification_status === 'PENDING') ? 1000 : false;
        },
        enabled: !!workflowId,
    });
    const [applying, setApplying] = React.useState(false);
    const [applyMsg, setApplyMsg] = React.useState('');

    if (isLoading || !data) return <div className="text-center text-green-500 animate-pulse">Establishing uplink...</div>;
    if (error) return <div className="text-red-500">Connection Lost with Sentinel Operations.</div>;

    const { state, logs } = data;
    
    if (!state) return <div className="text-center text-yellow-500">Initializing state...</div>;


    // improved status logic
    let remediationStatus = 'UNKNOWN';
    let statusColor = 'text-yellow-500';

    if (state.verification_status === 'PASS') {
        remediationStatus = 'REMEDIATED';
        statusColor = 'text-green-500'; // Green
    } else if (state.exploit_success) {
        remediationStatus = 'VULNERABLE';
        statusColor = 'text-red-500'; // Red
    } else if (state.verification_status === 'PENDING') {
        remediationStatus = 'ANALYZING';
        statusColor = 'text-yellow-500';
    } else {
        remediationStatus = 'SECURE';
        statusColor = 'text-green-500';
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'PASS': return 'text-green-500';
            case 'FAIL': return 'text-red-500';
            default: return 'text-yellow-500';
        }
    };

    const handleApply = async () => {
        setApplying(true);
        try {
            // dynamic import to avoid circular dependency if placed in api.js (though it's fine there)
            // assuming applyPatch is exported from api.js
            const { applyPatch } = await import('../services/api');
            await applyPatch(workflowId);
            setApplyMsg('Patch Applied Successfully!');
        } catch (err) {
            console.error(err);
            setApplyMsg('Failed to apply patch.');
        } finally {
            setApplying(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 p-4 rounded border border-gray-700">
                    <h3 className="text-gray-400 text-sm font-bold uppercase">Iteration</h3>
                    <p className="text-2xl font-mono">{state.iteration_count} / {state.max_iterations}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded border border-gray-700">
                    <h3 className="text-gray-400 text-sm font-bold uppercase">Network Status</h3>
                    <p className={`text-2xl font-mono ${statusColor}`}>
                        {remediationStatus}
                    </p>
                </div>
                <div className="bg-gray-800 p-4 rounded border border-gray-700">
                    <h3 className="text-gray-400 text-sm font-bold uppercase">Verification</h3>
                    <p className={`text-2xl font-mono ${getStatusColor(state.verification_status)}`}>
                        {state.verification_status}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-[300px]">
                {/* Left Column: Verification Analysis */}
                <div className="bg-gray-800 p-4 rounded border border-gray-700 flex flex-col">
                    <h3 className="text-yellow-400 mb-2 font-bold flex items-center gap-2">
                        <ShieldCheck size={16} /> Verification Analysis
                    </h3>
                    <div className="bg-gray-900 p-3 rounded text-gray-300 text-sm font-mono whitespace-pre-wrap border-l-4 border-yellow-500 flex-grow overflow-y-auto max-h-[400px]">
                        {state.verification_reasoning || "Waiting for verification analysis..."}
                    </div>
                </div>

                {/* Right Column: Patch Proposal */}
                <div className="bg-gray-800 p-4 rounded border border-gray-700 flex flex-col">
                    <div className="flex justify-between items-center mb-2">
                        <h3 className="text-blue-400 font-bold flex items-center gap-2">
                            <Activity size={16} /> Latest Patch
                        </h3>
                        {state.patch_diff && state.verification_status === 'PASS' && (
                            <button
                                onClick={handleApply}
                                disabled={applying || applyMsg.includes('Successfully')}
                                className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm disabled:opacity-50"
                            >
                                {applying ? 'Deploying...' : (applyMsg || 'Apply Patch to File')}
                            </button>
                        )}
                    </div>
                    <pre className="bg-black p-4 rounded text-green-300 font-mono text-xs overflow-auto flex-grow max-h-[400px]">
                        {state.patch_diff || (state.verification_status === 'PASS' ? "No patch required." : "Waiting for patch generation...")}
                    </pre>
                </div>
            </div>

            {/* Bottom: Live Logs */}
            <div className="bg-gray-900 p-4 rounded border border-gray-700 font-mono text-sm h-64 overflow-y-auto">
                <h3 className="text-green-400 mb-2 flex items-center gap-2"><Terminal size={16} /> Live Operations Log</h3>
                <div className="space-y-1">
                    {logs && logs.events.map((log, idx) => (
                        <div key={idx} className="border-b border-gray-800 pb-1 mb-1">
                            <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                            <span className="text-blue-400 font-bold">{log.agent}</span>:{' '}
                            <span className="text-gray-300">{log.action}</span>
                            {log.details && (
                                <pre className="text-xs text-gray-500 mt-1 pl-4 overflow-x-auto">
                                    {JSON.stringify(log.details, null, 2)}
                                </pre>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StatusView;
