import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { Link } from 'react-router-dom';
import { FileUp, Search, User, LogOut, Loader2, CheckCircle, TrendingUp } from 'lucide-react';

const CandidateDashboard = () => {
    const { user } = useAuth();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [recommendations, setRecommendations] = useState([]);

    useEffect(() => {
        const fetchProfile = async () => {
            if (!user) return;
            try {
                const res = await axios.get(`http://localhost:8000/api/candidates/me/${user.id}`);
                // Fetch recommendations
                const recRes = await axios.get(`http://localhost:8000/api/recommend/jobs/${user.id}`);
                setRecommendations(recRes.data);
            } catch (err) {
                console.error("Failed to fetch profile", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [user]);

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', user.id);

        try {
            await axios.post('http://localhost:8000/api/candidates/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Refresh profile data
            const profileRes = await axios.get(`http://localhost:8000/api/candidates/me/${user.id}`);
            setProfile(profileRes.data);

            // Refresh recommendations
            const recRes = await axios.get(`http://localhost:8000/api/recommend/jobs/${user.id}`);
            setRecommendations(recRes.data);

            alert("Resume analyzed successfully!");
        } catch (err) {
            console.error("Upload failed", err);
            alert("Failed to analyze resume.");
        } finally {
            setUploading(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-secondary" size={40} />
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in slide-in-from-bottom duration-500">
            {/* Upload Section */}
            <div className="card text-center py-12 mb-8 border-dashed border-2 bg-gradient-to-br from-secondary/5 to-transparent">
                <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                    {uploading ? <Loader2 className="animate-spin" size={32} /> : <FileUp size={32} />}
                </div>
                <h3 className="text-2xl font-bold mb-2">
                    {profile?.resume_path ? 'Update Your Resume' : 'Upload Your Resume'}
                </h3>
                <p className="text-gray-500 mb-6">Get AI-powered job matches by uploading your CV (PDF or DOCX)</p>
                <input type="file" className="hidden" id="cv-upload" onChange={handleUpload} disabled={uploading} />
                <label
                    htmlFor="cv-upload"
                    className={`btn-secondary cursor-pointer inline-block scale-105 hover:scale-110 transition-transform ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
                >
                    {uploading ? 'Analyzing...' : 'Select File'}
                </label>
                {profile?.resume_path && (
                    <p className="mt-4 text-xs text-green-600 flex items-center justify-center">
                        <CheckCircle size={14} className="mr-1" /> Resume parsed and skills updated
                    </p>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Profile Stats */}
                <div className="card hover:shadow-lg transition">
                    <h4 className="font-bold mb-4 flex items-center">
                        <User size={18} className="mr-2 text-secondary" />
                        Your Profile Details
                    </h4>
                    <div className="space-y-3 text-gray-600 dark:text-gray-400 text-sm">
                        <p><span className="font-semibold">Full Name:</span> {profile?.name}</p>
                        <p><span className="font-semibold">Preferred Role:</span> {profile?.preferred_role || 'Not Set'}</p>
                        <p><span className="font-semibold">Experience:</span> {profile?.experience_years} Years</p>
                        <p>
                            <span className="font-semibold text-secondary">Extracted Skills:</span>{' '}
                            {profile?.skills?.length > 0 ? profile.skills.join(', ') : 'None extracted'}
                        </p>
                    </div>
                </div>

                {/* AI Recommendations */}
                <div className="card hover:shadow-lg transition">
                    <h4 className="font-bold mb-4 flex items-center">
                        <TrendingUp size={18} className="mr-2 text-secondary" />
                        Top AI Recommendations
                    </h4>
                    {recommendations.length > 0 ? (
                        <div className="space-y-4">
                            {recommendations.slice(0, 3).map((rec, i) => (
                                <div key={i} className="flex flex-col bg-white dark:bg-gray-900 p-5 rounded-xl group shadow-sm hover:shadow-md transition-all border border-gray-100 dark:border-gray-800">
                                    <div className="flex justify-between items-center mb-4">
                                        <div className="flex flex-col">
                                            <span className="text-base font-black text-gray-900 dark:text-gray-100 group-hover:text-secondary transition-colors underline decoration-secondary/30 decoration-2 underline-offset-4">{rec.title}</span>
                                            <span className="text-[11px] text-gray-500 uppercase tracking-widest font-black mt-1">{rec.company}</span>
                                        </div>
                                        <div className="flex flex-col items-end bg-gray-50 dark:bg-gray-800 px-3 py-2 rounded-lg border border-gray-100 dark:border-gray-700">
                                            <div className="text-right">
                                                <div className="text-[9px] text-gray-400 font-black uppercase tracking-tighter">AI Match Probability</div>
                                                <div className="text-2xl font-black text-gray-900 dark:text-white leading-none mt-1">{Math.round(rec.score * 100)}%</div>
                                            </div>
                                        </div>
                                    </div>

                                    {rec.skill_gap && rec.skill_gap.length > 0 && (
                                        <div className="mt-2 mb-4">
                                            <span className="text-[10px] text-red-600 dark:text-red-400 font-black uppercase tracking-wider block mb-2">Missing Skills (Gap Analysis)</span>
                                            <div className="flex flex-wrap gap-1.5">
                                                {rec.skill_gap.map((skill, idx) => (
                                                    <span key={idx} className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 px-2 py-1 rounded text-[10px] font-black border border-red-100 dark:border-red-900/30 uppercase">
                                                        {skill}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {rec.suggestions && (
                                        <div className="mt-auto p-3 bg-blue-50/50 dark:bg-blue-900/10 rounded-lg border border-blue-100/50 dark:border-blue-900/20">
                                            <p className="text-[11px] text-gray-800 dark:text-gray-300 leading-relaxed">
                                                <strong className="text-secondary uppercase font-black mr-2 text-[10px]">AI Strategic Suggestion:</strong>
                                                <span className="font-medium">{rec.suggestions}</span>
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                            <Link to="/candidate/jobs" className="text-secondary text-xs font-bold hover:underline block text-center mt-2">
                                View all matches
                            </Link>
                        </div>
                    ) : (
                        <p className="text-gray-500 text-sm italic">
                            {profile?.resume_path
                                ? "Calculating recommendations..."
                                : "Upload your resume to see high-confidence job matches here."}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CandidateDashboard;
