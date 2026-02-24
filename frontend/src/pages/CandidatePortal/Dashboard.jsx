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
                                <div key={i} className="flex justify-between items-center bg-gray-50 dark:bg-gray-800 p-3 rounded-lg group">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold group-hover:text-secondary transition-colors">{rec.title}</span>
                                        <span className="text-[10px] text-gray-400 uppercase tracking-wider">{rec.company}</span>
                                    </div>
                                    <div className="flex items-center space-x-3">
                                        <div className="flex flex-col items-end">
                                            <span className="text-xs font-black text-secondary">{Math.round(rec.score * 100)}% Match</span>
                                            <span className="text-[8px] text-green-500 font-bold uppercase tracking-tighter">Auto-Matched</span>
                                        </div>
                                    </div>
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
