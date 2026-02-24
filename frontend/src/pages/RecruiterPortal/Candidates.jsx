import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Users, Search, Filter, ArrowUpRight, Loader2, Target, X } from 'lucide-react';

const Candidates = () => {
    const [jobs, setJobs] = useState([]);
    const [selectedJob, setSelectedJob] = useState(null);
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(false);

    // Filtering states
    const [searchTerm, setSearchTerm] = useState('');
    const [minScore, setMinScore] = useState(0);
    const [minExp, setMinExp] = useState(0);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/jobs');
                setJobs(res.data);
                if (res.data.length > 0) {
                    setSelectedJob(res.data[0]);
                }
            } catch (err) {
                console.error("Failed to fetch jobs", err);
            }
        };
        fetchJobs();
    }, []);

    useEffect(() => {
        if (selectedJob) {
            fetchRankedCandidates(selectedJob.id);
        }
    }, [selectedJob]);

    const fetchRankedCandidates = async (jobId) => {
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/api/recommend', {
                job_id: jobId,
                top_k: 50 // Fetch more for local filtering
            });
            setCandidates(res.data.matches);
        } catch (err) {
            console.error("Failed to fetch matches", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredCandidates = useMemo(() => {
        return candidates.filter(c => {
            const matchesSearch = c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                c.skills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
            const matchesScore = (c.score * 100) >= minScore;
            const matchesExp = c.experience_years >= minExp;
            return matchesSearch && matchesScore && matchesExp;
        });
    }, [candidates, searchTerm, minScore, minExp]);

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold">Smart Candidate Matching</h2>
                    <p className="text-gray-500 text-sm">Ranked by trained XGBoost model probability</p>
                </div>

                <div className="flex flex-wrap gap-3 w-full md:w-auto">
                    <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 p-2 rounded-lg border dark:border-gray-700 shadow-sm grow md:grow-0">
                        <Target size={18} className="text-primary" />
                        <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Target Role:</span>
                        <select
                            className="bg-transparent border-none focus:ring-0 text-sm font-black text-gray-900 dark:text-white cursor-pointer"
                            value={selectedJob?.id || ''}
                            onChange={(e) => {
                                const job = jobs.find(j => j.id === e.target.value);
                                setSelectedJob(job);
                            }}
                        >
                            {jobs.map(job => (
                                <option key={job.id} value={job.id}>{job.title}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white dark:bg-gray-800 p-4 rounded-xl border dark:border-gray-700 shadow-sm">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                    <input
                        type="text"
                        placeholder="Search name or skill..."
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border rounded-lg text-sm"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="flex flex-col">
                    <label className="text-[10px] font-bold uppercase text-gray-400 mb-1 ml-1">Min Match Score: {minScore}%</label>
                    <input
                        type="range"
                        min="0" max="100"
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
                        value={minScore}
                        onChange={(e) => setMinScore(parseInt(e.target.value))}
                    />
                </div>

                <div className="flex flex-col">
                    <label className="text-[10px] font-bold uppercase text-gray-400 mb-1 ml-1">Min Experience: {minExp}y</label>
                    <input
                        type="range"
                        min="0" max="15"
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-secondary"
                        value={minExp}
                        onChange={(e) => setMinExp(parseInt(e.target.value))}
                    />
                </div>

                <button
                    onClick={() => { setSearchTerm(''); setMinScore(0); setMinExp(0); }}
                    className="flex items-center justify-center space-x-2 text-xs font-bold text-gray-400 hover:text-red-500 transition-colors"
                >
                    <X size={14} />
                    <span>RESET FILTERS</span>
                </button>
            </div>

            <div className="card overflow-hidden p-0 shadow-lg border-primary/10">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 dark:bg-gray-800/80 border-b dark:border-gray-700">
                            <tr>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Rank</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Candidate</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Core Skills</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Exp</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Match Score</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">CV / Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y dark:divide-gray-700">
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-20 text-center">
                                        <div className="flex flex-col items-center">
                                            <Loader2 className="animate-spin text-primary mb-2" size={32} />
                                            <p className="text-gray-500 font-medium">Running XGBoost Inference...</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : filteredCandidates.length > 0 ? (
                                filteredCandidates.map((c, i) => (
                                    <tr key={c.id} className="hover:bg-primary/5 dark:hover:bg-primary/10 transition-colors group">
                                        <td className="px-6 py-4">
                                            <span className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-sm ${i < 3 ? 'bg-primary text-white shadow-md' : 'bg-gray-100 dark:bg-gray-700 text-gray-500'}`}>
                                                {i + 1}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div>
                                                <div className="font-black text-gray-900 dark:text-gray-100 group-hover:text-primary transition-colors">{c.name}</div>
                                                <div className="text-[10px] text-gray-400 font-mono">ID: {c.id}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {c.skills.slice(0, 3).map(s => (
                                                    <span key={s} className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 text-[10px] font-bold rounded uppercase tracking-wider">
                                                        {s}
                                                    </span>
                                                ))}
                                                {c.skills.length > 3 && <span className="text-[10px] font-bold text-gray-400">+{c.skills.length - 3}</span>}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm font-black text-center">{c.experience_years}y</td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center space-x-3">
                                                <div className="flex-1 w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden shadow-inner">
                                                    <div
                                                        className={`h-full transition-all duration-1000 ${c.score > 0.8 ? 'bg-green-500' : c.score > 0.5 ? 'bg-primary' : 'bg-amber-500'}`}
                                                        style={{ width: `${Math.round(c.score * 100)}%` }}
                                                    ></div>
                                                </div>
                                                <span className="text-sm font-black text-gray-900 dark:text-gray-100 min-w-[40px]">
                                                    {Math.round(c.score * 100)}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <a
                                                href={`http://localhost:8000/api/candidates/${c.id}/cv`}
                                                className="btn-primary px-3 py-1.5 text-[10px] font-black uppercase rounded-md inline-flex items-center"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                Download CV
                                            </a>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-gray-500 italic">
                                        <div className="flex flex-col items-center opacity-40">
                                            <Target size={40} className="mb-2" />
                                            <p>No candidates match your current filters.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="bg-primary/5 border border-primary/20 p-4 rounded-xl flex items-start space-x-3 shadow-sm">
                <Target size={20} className="text-primary shrink-0 mt-0.5" />
                <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                    <strong className="text-primary font-black uppercase text-[10px] tracking-widest block mb-1 border-b border-primary/20 pb-1">Model-Driven Enforcement</strong>
                    These match scores are strictly dictated by the trained XGBoost model probability.
                    The ranking is automatic and based on the statistical contribution of 10 distinct features including Semantic SBERT, TF-IDF frequency, and Skill Density.
                </p>
            </div>
        </div>
    );
};

export default Candidates;
