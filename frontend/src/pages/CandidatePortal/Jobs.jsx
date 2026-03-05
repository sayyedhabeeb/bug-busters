import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { Search, MapPin, DollarSign, Clock, Filter, Bookmark, Loader2, Target } from 'lucide-react';

const Jobs = () => {
    const { user } = useAuth();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [applying, setApplying] = useState(null);
    const [analyzing, setAnalyzing] = useState(null);
    const [matchResults, setMatchResults] = useState({});
    const [appliedJobs, setAppliedJobs] = useState(new Set());

    useEffect(() => {
        const fetchAllJobs = async () => {
            try {
                const res = await axios.get(`http://localhost:8000/api/jobs`);
                setJobs(res.data);
            } catch (err) {
                console.error("Failed to fetch jobs", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAllJobs();
    }, []);

    const checkMatch = async (jobId) => {
        setAnalyzing(jobId);
        try {
            const res = await axios.post('http://localhost:8000/api/recommend/analyze', {
                user_id: user.id,
                job_id: jobId
            });
            setMatchResults(prev => ({ ...prev, [jobId]: res.data }));
        } catch (err) {
            console.error("Match analysis failed", err);
            alert("Failed to analyze match. Have you uploaded your resume?");
        } finally {
            setAnalyzing(null);
        }
    };

    const handleApply = async (job) => {
        setApplying(job.id);
        const matchData = matchResults[job.id] || {};
        try {
            await axios.post('http://localhost:8000/api/applications', {
                user_id: user.id,
                job_id: job.id,
                score: matchData.final_score || job.score || 0.0,
                xgboost_score: matchData.xgboost_score || 0.0,
                match_drivers: matchData.match_drivers || []
            });
            setAppliedJobs(prev => new Set([...prev, job.id]));
            alert(`Successfully applied for ${job.title}!`);
        } catch (err) {
            console.error("Application failed", err);
            alert("Failed to submit application. Did you upload your resume?");
        } finally {
            setApplying(null);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-secondary" size={40} />
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">All Available Jobs</h2>
                    <p className="text-gray-500 text-sm">Explore all current vacancies across our network</p>
                </div>
                <div className="flex w-full md:w-auto space-x-2">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                        <input className="pl-10 pr-4 py-2 w-full rounded-lg border dark:bg-gray-700 dark:border-gray-600 outline-none focus:ring-2 focus:ring-secondary/20" placeholder="Search jobs..." />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {jobs.length > 0 ? jobs.map((job, i) => (
                    <div key={job.id || i} className="card border-l-4 border-l-transparent hover:border-l-secondary transition-all group hover:shadow-lg animate-in slide-in-from-bottom duration-300" style={{ animationDelay: `${i * 100}ms` }}>
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <div className="flex-1">
                                <div className="flex flex-wrap items-center gap-3 mb-2">
                                    <h3 className="text-lg font-black group-hover:text-secondary transition-colors">{job.title}</h3>
                                    {appliedJobs.has(job.id) && (
                                        <span className="px-2 py-0.5 bg-green-100 text-green-600 text-[10px] font-black uppercase rounded-md">
                                            Applied
                                        </span>
                                    )}
                                </div>
                                <p className="text-gray-600 dark:text-gray-300 font-bold text-sm mb-4">
                                    {job.company_name || 'Hiring Company'}
                                </p>

                                <div className="flex flex-wrap gap-4 text-xs text-gray-400 font-medium">
                                    <span className="flex items-center"><Clock size={14} className="mr-1 text-blue-500" /> {job.job_type || 'Full-time'}</span>
                                </div>
                            </div>

                            <div className="flex flex-col gap-3 w-full md:w-auto">
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={() => checkMatch(job.id)}
                                        disabled={analyzing === job.id}
                                        className="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-black text-xs transition-all border-2 border-primary text-primary hover:bg-primary/5 active:scale-95 disabled:opacity-50"
                                    >
                                        {analyzing === job.id ? (
                                            <span className="flex items-center justify-center">
                                                <Loader2 size={14} className="animate-spin mr-2" />
                                                Analyzing...
                                            </span>
                                        ) : (
                                            'Check AI Match'
                                        )}
                                    </button>
                                    <button
                                        onClick={() => handleApply(job)}
                                        disabled={applying === job.id || appliedJobs.has(job.id)}
                                        className={`flex-1 md:flex-none px-6 py-2.5 rounded-lg font-black text-sm transition-all shadow-md ${appliedJobs.has(job.id)
                                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none'
                                            : 'bg-secondary text-white hover:bg-secondary-dark active:scale-95 shadow-secondary/20'
                                            }`}
                                    >
                                        {applying === job.id ? (
                                            <span className="flex items-center justify-center">
                                                <Loader2 size={16} className="animate-spin mr-2" />
                                                Applying...
                                            </span>
                                        ) : appliedJobs.has(job.id) ? (
                                            'Applied'
                                        ) : (
                                            'Apply Now'
                                        )}
                                    </button>
                                </div>

                                {matchResults[job.id] && (
                                    <div className="mt-4 p-5 bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 animate-in zoom-in duration-300">
                                        <div className="flex justify-between items-center mb-5 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                                            <div>
                                                <div className="text-gray-400 font-black uppercase tracking-widest text-[9px] mb-1">Combined AI Match Score</div>
                                                <div className="text-4xl font-black text-gray-900 dark:text-white leading-none">{Math.round(matchResults[job.id].final_score * 100)}%</div>
                                            </div>
                                            <div className="w-12 h-12 rounded-full border-4 border-secondary/20 border-t-secondary flex items-center justify-center text-secondary font-black text-xs">
                                                AI
                                            </div>
                                        </div>

                                        {matchResults[job.id].skill_gap?.length > 0 && (
                                            <div className="mb-5">
                                                <div className="text-red-600 dark:text-red-400 font-black uppercase tracking-wider text-[10px] mb-2 px-1">Critical Skill Gaps</div>
                                                <div className="flex flex-wrap gap-1.5">
                                                    {matchResults[job.id].skill_gap.map(s => (
                                                        <span key={s} className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 px-2 py-1 rounded border border-red-100 dark:border-red-900/30 font-black text-[10px] uppercase">{s}</span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        <div className="bg-blue-50/50 dark:bg-blue-900/10 p-4 rounded-xl border border-blue-100/50 dark:border-blue-900/20">
                                            <div className="flex items-start gap-3">
                                                <div className="mt-0.5 text-secondary">
                                                    <Target size={16} />
                                                </div>
                                                <div>
                                                    <strong className="text-secondary uppercase font-black text-[10px] block mb-1">Strategic AI Suggestion</strong>
                                                    <p className="text-[11px] text-gray-800 dark:text-gray-300 leading-relaxed font-medium">
                                                        {matchResults[job.id].suggestions}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )) : (
                    <div className="card text-center py-20 text-gray-500">
                        <div className="max-w-xs mx-auto">
                            <Search size={48} className="mx-auto mb-4 opacity-10" />
                            <h3 className="text-lg font-bold text-gray-400 mb-2">No Matches Yet</h3>
                            <p className="text-sm">Please upload your resume in the dashboard to enable AI-powered matching.</p>
                        </div>
                    </div>
                )}
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 p-4 rounded-xl flex items-center space-x-3 mb-8">
                <Target size={20} className="text-blue-600" />
                <p className="text-xs text-blue-700 dark:text-blue-300 font-medium leading-relaxed">
                    <strong>Refinement Tip:</strong> Our XGBoost model uses semantic analysis. If match scores are low, try mentioning specific technologies from the job descriptions in your resume.
                </p>
            </div>
        </div>
    );
};

export default Jobs;
