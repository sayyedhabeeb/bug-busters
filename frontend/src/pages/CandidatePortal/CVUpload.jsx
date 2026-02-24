import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { FileUp, CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';

const CVUpload = () => {
    const { user } = useAuth();
    const [file, setFile] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [results, setResults] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setAnalyzing(true);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', user.id);

        try {
            const res = await axios.post('http://localhost:8000/api/candidates/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Now get recommendations based on the uploaded CV
            // For simplicity, we can just fetch jobs and match them here or have a recommendation endpoint
            const recRes = await axios.post('http://localhost:8000/api/recommend', {
                job_id: 'default',
                job_description: 'Software Engineer', // This would normally be dynamic
                required_skills: res.data.skills_extracted
            });

            const processedResults = {
                skills: res.data.skills_extracted,
                recommendations: recRes.data.matches.map(m => ({
                    role: m.candidate_id, // This should be job title in a better API
                    score: Math.round(m.final_score * 100),
                    missing: []
                })),
                suggestions: ['Resume uploaded successfully!'],
                strengths: ['Profile updated']
            };

            setResults(processedResults);
        } catch (err) {
            console.error(err);
            alert("Analysis failed. Ensure the Python API is running on port 8000.");
        } finally {
            setAnalyzing(false);
        }
    };

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <h2 className="text-2xl font-bold mb-8">Resume AI Analysis</h2>

            {!results ? (
                <div className="card text-center py-16 border-dashed border-2 flex flex-col items-center">
                    <div className="w-20 h-20 bg-blue-100 text-primary rounded-full flex items-center justify-center mb-6">
                        <FileUp size={40} />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Upload Your CV</h3>
                    <p className="text-gray-500 mb-8 max-w-md">Our AI will scan your resume to extract skills and match you with the best available job roles.</p>

                    <input type="file" onChange={handleFileChange} className="hidden" id="resume-input" />
                    <label htmlFor="resume-input" className="cursor-pointer bg-white dark:bg-gray-700 border-2 border-primary text-primary px-8 py-3 rounded-xl font-bold hover:bg-primary hover:text-white transition-all mb-4">
                        {file ? file.name : 'Choose File (PDF/DOCX)'}
                    </label>

                    {file && (
                        <button
                            onClick={handleAnalyze}
                            disabled={analyzing}
                            className="btn-primary w-48 flex items-center justify-center space-x-2"
                        >
                            {analyzing ? <Loader2 className="animate-spin" /> : null}
                            <span>{analyzing ? 'Analyzing...' : 'Analyze Now'}</span>
                        </button>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
                    {/* Left: Extracted Skills & Strengths */}
                    <div className="space-y-6">
                        <div className="card">
                            <h3 className="font-bold mb-4 flex items-center space-x-2">
                                <CheckCircle2 className="text-green-500" size={20} />
                                <span>Extracted Skills</span>
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {results.skills.map(skill => (
                                    <span key={skill} className="px-3 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full text-sm font-medium">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div className="card bg-blue-50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900/30">
                            <h3 className="font-bold mb-4 text-blue-800 dark:text-blue-300">AI Suggestions</h3>
                            <ul className="space-y-3">
                                {results.suggestions.map((s, i) => (
                                    <li key={i} className="text-sm flex items-start space-x-2">
                                        <AlertCircle size={16} className="mt-0.5" />
                                        <span>{s}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Middle & Right: Match Scores */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="card">
                            <h3 className="text-xl font-bold mb-6">Job Role Recommended Matches</h3>
                            <div className="space-y-8">
                                {results.recommendations.map((rec) => (
                                    <div key={rec.role} className="space-y-2">
                                        <div className="flex justify-between items-center text-sm font-bold">
                                            <span>{rec.role}</span>
                                            <span className={rec.score > 70 ? 'text-green-600' : rec.score > 40 ? 'text-amber-600' : 'text-red-500'}>
                                                {rec.score}% Match
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 dark:bg-gray-700 h-3 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-1000 ${rec.score > 70 ? 'bg-green-500' : rec.score > 40 ? 'bg-amber-500' : 'bg-red-500'
                                                    }`}
                                                style={{ width: `${rec.score}%` }}
                                            ></div>
                                        </div>
                                        {rec.missing.length > 0 && (
                                            <p className="text-xs text-gray-500 mt-1">
                                                <span className="font-semibold">Missing:</span> {rec.missing.join(', ')}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex space-x-4">
                            <button onClick={() => setResults(null)} className="flex-1 border-2 border-gray-200 dark:border-gray-700 py-3 rounded-xl font-bold">Re-upload</button>
                            <button className="flex-[2] btn-primary">Browse Matched Jobs</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CVUpload;
