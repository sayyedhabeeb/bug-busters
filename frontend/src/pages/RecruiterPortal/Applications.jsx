import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { ClipboardList, User, Calendar, ExternalLink, Loader2, Target, CheckCircle } from 'lucide-react';

const Applications = () => {
    const { user } = useAuth();
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchApplications = async () => {
            if (!user) return;
            try {
                const res = await axios.get(`http://localhost:8000/api/applications/recruiter/${user.id}`);
                setApplications(res.data);
            } catch (err) {
                console.error("Failed to fetch applications", err);
            } finally {
                setLoading(false);
            }
        };
        fetchApplications();
    }, [user]);

    if (loading) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-primary" size={40} />
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Manage Applications</h2>
                    <p className="text-gray-500 text-sm">Review candidate matches and process job applications</p>
                </div>
            </div>

            <div className="card overflow-hidden p-0 shadow-lg border-primary/10">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 dark:bg-gray-800/80 border-b dark:border-gray-700">
                        <tr>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Candidate</th>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest">Job Role</th>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Match %</th>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Applied On</th>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Status</th>
                            <th className="px-6 py-4 text-xs font-black text-gray-400 uppercase tracking-widest text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y dark:divide-gray-700">
                        {applications.length > 0 ? (
                            applications.map((app) => (
                                <tr key={app.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-10 h-10 bg-primary/10 text-primary flex items-center justify-center rounded-full">
                                                <User size={18} />
                                            </div>
                                            <div>
                                                <div className="font-bold text-gray-900 dark:text-gray-100">{app.candidate_name}</div>
                                                <div className="text-[10px] text-gray-400">ID: #{app.id}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="font-bold text-gray-700 dark:text-gray-300">{app.job_title}</div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="inline-flex items-center px-2.5 py-1 bg-primary/10 text-primary text-xs font-black rounded-md">
                                            {Math.round(app.match_score * 100)}%
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex items-center justify-center text-xs text-gray-500">
                                            <Calendar size={14} className="mr-1.5" />
                                            {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'N/A'}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <span className={`px-3 py-1 text-[10px] font-black uppercase rounded-full ${app.status === 'Auto-Matched' ? 'bg-indigo-100 text-indigo-600' :
                                            app.status === 'Applied' ? 'bg-blue-100 text-blue-600' :
                                                app.status === 'Accepted' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
                                            }`}>
                                            {app.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <a
                                            href={`http://localhost:8000/api/candidates/${app.candidate_id}/cv`}
                                            className="p-2 text-gray-400 hover:text-primary transition-colors inline-block"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            title="Download CV"
                                        >
                                            <ExternalLink size={18} />
                                        </a>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="6" className="px-6 py-12 text-center text-gray-500 italic">
                                    <div className="flex flex-col items-center opacity-30">
                                        <ClipboardList size={48} className="mb-3" />
                                        <p className="text-sm font-bold">No candidate matches found yet.</p>
                                        <p className="text-xs">Once candidates upload their CVs, AI will automatically match them to your jobs.</p>
                                    </div>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="bg-primary/5 border border-primary/20 p-4 rounded-xl flex items-start space-x-3 shadow-sm">
                <CheckCircle size={20} className="text-primary shrink-0 mt-0.5" />
                <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed font-medium">
                    <strong>Auto-Matching Engine:</strong> This system uses AI to automatically link candidates to your jobs.
                    You no longer need to wait for manual applications; the best talent is surfaced instantly upon resume upload.
                </p>
            </div>
        </div>
    );
};

export default Applications;
