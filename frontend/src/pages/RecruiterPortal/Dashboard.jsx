import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { Link } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Users, BarChart3, Settings, LogOut, MapPin, Loader2 } from 'lucide-react';

const RecruiterDashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        total_jobs: 0,
        total_candidates: 0,
        total_applications: 0,
        avg_match_score: 0,
        recent_vacancies: []
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/recruiter/stats');
                setStats(res.data);
            } catch (err) {
                console.error("Failed to fetch recruiter stats", err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-primary" size={40} />
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header with real-time stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card flex items-center justify-between border-l-4 border-blue-500 shadow-sm">
                    <div>
                        <p className="text-gray-500 mb-1 font-medium text-sm">Total Jobs</p>
                        <h3 className="text-3xl font-black">{stats.total_jobs}</h3>
                    </div>
                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-lg">
                        <Briefcase />
                    </div>
                </div>
                <div className="card flex items-center justify-between border-l-4 border-green-500 shadow-sm">
                    <div>
                        <p className="text-gray-500 mb-1 font-medium text-sm">Available Candidates</p>
                        <h3 className="text-3xl font-black">{stats.total_candidates}</h3>
                    </div>
                    <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 rounded-lg">
                        <Users />
                    </div>
                </div>
                <div className="card flex items-center justify-between border-l-4 border-amber-500 shadow-sm">
                    <div>
                        <p className="text-gray-500 mb-1 font-medium text-sm">Avg. Match Score</p>
                        <h3 className="text-3xl font-black">{stats.avg_match_score}%</h3>
                    </div>
                    <div className="p-3 bg-amber-100 dark:bg-amber-900/30 text-amber-600 rounded-lg">
                        <BarChart3 />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="card h-full">
                    <h3 className="text-lg font-bold mb-6 flex items-center">
                        <LayoutDashboard className="mr-2 text-primary" size={20} />
                        Quick Actions
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Link to="/recruiter/job-roles" className="p-4 border dark:border-gray-700 rounded-xl hover:bg-primary/5 hover:border-primary transition group text-left">
                            <p className="font-bold group-hover:text-primary transition-colors">Create Role</p>
                            <p className="text-xs text-gray-500 mt-1">Add a new job vacancy</p>
                        </Link>
                        <Link to="/recruiter/candidates" className="p-4 border dark:border-gray-700 rounded-xl hover:bg-secondary/5 hover:border-secondary transition group text-left">
                            <p className="font-bold group-hover:text-secondary transition-colors">View Matches</p>
                            <p className="text-xs text-gray-500 mt-1">Check top candidates</p>
                        </Link>
                    </div>
                </div>

                <div className="card h-full">
                    <h3 className="text-lg font-bold mb-6 flex items-center">
                        <Briefcase className="mr-2 text-primary" size={20} />
                        Recent Vacancies
                    </h3>
                    {stats.recent_vacancies.length > 0 ? (
                        <div className="space-y-4">
                            {stats.recent_vacancies.map((job) => (
                                <div key={job.id} className="p-3 border dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition flex justify-between items-center group">
                                    <div>
                                        <p className="font-bold text-sm group-hover:text-primary">{job.title}</p>
                                        <div className="flex items-center text-xs text-gray-400 mt-1">
                                            <MapPin size={12} className="mr-1" /> {job.location} • {job.type}
                                        </div>
                                    </div>
                                    <Link to="/recruiter/candidates" className="text-xs font-bold text-secondary hover:underline">
                                        View Matches →
                                    </Link>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <Briefcase size={32} className="mx-auto mb-2 text-gray-300 opacity-50" />
                            <p className="text-gray-500 italic text-sm">No job roles created yet.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RecruiterDashboard;
