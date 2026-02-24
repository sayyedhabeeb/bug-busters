import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { Plus, Trash2, Edit3, Briefcase } from 'lucide-react';

const JobRoles = () => {
    const { user } = useAuth();
    const [jobs, setJobs] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        required_skills: '',
        experience_required: 0,
        location: 'Remote',
        salary_range: '',
        job_type: 'Full-time'
    });

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/jobs');
            setJobs(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleEdit = (job) => {
        setEditingId(job.id);
        setIsEditing(true);
        setFormData({
            title: job.title,
            description: job.description,
            required_skills: Array.isArray(job.skills) ? job.skills.join(', ') : (job.skills || ''),
            experience_required: job.experience_required,
            location: job.location || 'Remote',
            salary_range: job.salary_range || '',
            job_type: job.job_type || 'Full-time'
        });
        setShowModal(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                required_skills: formData.required_skills.split(',').map(s => s.trim()),
                recruiter_id: user.id
            };

            if (isEditing) {
                await axios.put(`http://localhost:8000/api/jobs/${editingId}`, payload);
            } else {
                await axios.post('http://localhost:8000/api/jobs', payload);
            }

            setShowModal(false);
            setIsEditing(false);
            setEditingId(null);
            setFormData({ title: '', description: '', required_skills: '', experience_required: 0, location: 'Remote', salary_range: '', job_type: 'Full-time' });
            fetchJobs();
        } catch (err) {
            console.error(err);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this job role?')) {
            try {
                await axios.delete(`http://localhost:8000/api/jobs/${id}`);
                fetchJobs();
            } catch (err) {
                console.error(err);
            }
        }
    };

    return (
        <div className="p-8 bg-gray-50 dark:bg-dark min-h-screen">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold">Job Role Management</h2>
                <button
                    onClick={() => {
                        setIsEditing(false);
                        setFormData({ title: '', description: '', required_skills: '', experience_required: 0, location: 'Remote', salary_range: '', job_type: 'Full-time' });
                        setShowModal(true);
                    }}
                    className="btn-primary flex items-center space-x-2"
                >
                    <Plus size={20} />
                    <span>Create New Role</span>
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {jobs.map((job) => (
                    <div key={job.id} className="card hover:shadow-xl transition-shadow flex flex-col">
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-lg">
                                <Briefcase size={24} />
                            </div>
                            <div className="flex space-x-2">
                                <button onClick={() => handleEdit(job)} className="text-gray-400 hover:text-primary transition-colors p-1 rounded-md hover:bg-primary/10">
                                    <Edit3 size={18} />
                                </button>
                                <button onClick={() => handleDelete(job.id)} className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-md hover:bg-red-50">
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                        <h3 className="text-xl font-bold mb-1">{job.title}</h3>
                        <p className="text-sm text-gray-400 mb-4">{job.location || 'Remote'} · {job.job_type || 'Full-time'}</p>

                        <div className="mb-4">
                            <p className="text-xs font-semibold text-gray-400 uppercase mb-2">Required Skills</p>
                            <div className="flex flex-wrap gap-2">
                                {(Array.isArray(job.skills) ? job.skills : (job.skills ? job.skills.split(',') : [])).map(skill => (
                                    <span key={skill} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded-full">
                                        {skill.trim()}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-between items-center pt-4 border-t border-gray-100 dark:border-gray-700 mt-auto">
                            <span className="text-sm font-bold text-secondary">{job.salary_range || 'Competitive'}</span>
                            <span className="text-sm text-gray-500">{job.experience_required}+ years exp</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Simple Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto backdrop-blur-sm">
                    <div className="card w-full max-w-lg my-8 shadow-2xl animate-in zoom-in duration-200">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold">{isEditing ? 'Edit Job Role' : 'Create New Job Role'}</h3>
                            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">×</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Job Title</label>
                                    <input
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        value={formData.title}
                                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Description</label>
                                    <textarea
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        rows="3"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        required
                                    ></textarea>
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Required Skills (Comma separated)</label>
                                    <input
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        placeholder="React, Node.js, MySQL"
                                        value={formData.required_skills}
                                        onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Location</label>
                                    <input
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 shadow-sm"
                                        value={formData.location}
                                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Job Type</label>
                                    <select
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 shadow-sm"
                                        value={formData.job_type}
                                        onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                                    >
                                        <option>Full-time</option>
                                        <option>Part-time</option>
                                        <option>Contract</option>
                                        <option>Hybrid</option>
                                        <option>Remote</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Salary Range</label>
                                    <input
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 shadow-sm"
                                        placeholder="$80k - $120k"
                                        value={formData.salary_range}
                                        onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1 text-gray-600">Min Experience (Years)</label>
                                    <input
                                        type="number"
                                        className="w-full p-2.5 rounded-lg border dark:bg-gray-700 shadow-sm"
                                        value={formData.experience_required}
                                        onChange={(e) => setFormData({ ...formData, experience_required: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end space-x-3 mt-8">
                                <button type="button" onClick={() => setShowModal(false)} className="px-6 py-2.5 rounded-lg text-gray-500 font-bold hover:bg-gray-100 transition-colors">Cancel</button>
                                <button type="submit" className="btn-primary px-8 py-2.5 rounded-lg shadow-lg hover:shadow-primary/20 transition-all font-bold">
                                    {isEditing ? 'Save Changes' : 'Create Role'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default JobRoles;
