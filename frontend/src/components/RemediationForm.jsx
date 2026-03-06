import React, { useState, useEffect } from 'react';
import { startRemediation } from '../services/api';
import { Play, Loader2 } from 'lucide-react';

const RemediationForm = ({ onStart }) => {
    const [codePath, setCodePath] = useState('');
    const [vulnType, setVulnType] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [vulnerabilities, setVulnerabilities] = useState([]);
    const [loadingVulns, setLoadingVulns] = useState(true);

    useEffect(() => {
        // Fetch available vulnerabilities from backend
        const fetchVulnerabilities = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/vulnerabilities');
                const data = await response.json();
                setVulnerabilities(data.vulnerabilities || []);
            } catch (err) {
                console.error('Failed to fetch vulnerabilities:', err);
                // Fallback to hardcoded options
                setVulnerabilities([
                    { code: 'SQL', name: 'SQL Injection' },
                    { code: 'XSS', name: 'Cross-Site Scripting (XSS)' },
                    { code: 'PATH_TRAVERSAL', name: 'Path Traversal' },
                    { code: 'BUFFER_OVERFLOW', name: 'Buffer Overflow' }
                ]);
            } finally {
                setLoadingVulns(false);
            }
        };
        fetchVulnerabilities();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const data = await startRemediation(codePath, vulnType);
            onStart(data.workflow_id);
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'Failed to start remediation. Check console for details.';
            setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
            console.error("Remediation Error:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-green-400 flex items-center gap-2">
                <Play size={20} /> Start New Mission
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-400">Target File Path</label>
                    <input
                        type="text"
                        value={codePath}
                        onChange={(e) => setCodePath(e.target.value)}
                        className="mt-1 block w-full bg-gray-900 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-green-500 focus:border-green-500"
                        placeholder="C:/Projects/vulnerable.py"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-400">Vulnerability Type</label>
                    <select
                        value={vulnType}
                        onChange={(e) => setVulnType(e.target.value)}
                        className="mt-1 block w-full bg-gray-900 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-green-500 focus:border-green-500"
                        required
                        disabled={loadingVulns}
                    >
                        <option value="" disabled>
                            {loadingVulns ? 'Loading...' : 'Select Vulnerability Type'}
                        </option>
                        {vulnerabilities.map((vuln) => (
                            <option key={vuln.code} value={vuln.code}>
                                {vuln.name}
                            </option>
                        ))}
                    </select>
                </div>
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <button
                    type="submit"
                    disabled={loading || loadingVulns}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-green-500 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                >
                    {loading ? <Loader2 className="animate-spin" /> : 'Launch Sentinel'}
                </button>
            </form>
        </div>
    );
};

export default RemediationForm;
