import React, { useState } from 'react';
import { useAuth } from '../services/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        role: 'candidate',
        industry: '',
        experience_level: '',
        preferred_role: ''
    });
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Sanitize data: convert experience to number
            const sanitizedData = {
                ...formData,
                experience_level: formData.experience_level === '' ? 0 : parseInt(formData.experience_level),
                industry: formData.industry || null,
                preferred_role: formData.preferred_role || null
            };
            await register(sanitizedData);
            navigate('/login');
        } catch (err) {
            setError('Registration failed. Please check your details and try again.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-dark py-12">
            <div className="card w-full max-w-2xl">
                <h2 className="text-3xl font-bold mb-6 text-center text-primary">Join Bug-Busters</h2>
                <p className="text-center text-gray-600 mb-8">Create your recruiter or candidate account</p>

                {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-gray-700 dark:text-gray-300 mb-2">Full Name / Company Name</label>
                            <input name="name" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" required />
                        </div>
                        <div>
                            <label className="block text-gray-700 dark:text-gray-300 mb-2">Email Address</label>
                            <input type="email" name="email" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" required />
                        </div>
                        <div>
                            <label className="block text-gray-700 dark:text-gray-300 mb-2">Password</label>
                            <input type="password" name="password" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" required />
                        </div>
                        <div>
                            <label className="block text-gray-700 dark:text-gray-300 mb-2">Role</label>
                            <select name="role" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600">
                                <option value="candidate">Candidate</option>
                                <option value="recruiter">Recruiter</option>
                            </select>
                        </div>

                        {formData.role === 'recruiter' ? (
                            <div className="col-span-1 md:col-span-2">
                                <label className="block text-gray-700 dark:text-gray-300 mb-2">Industry</label>
                                <input name="industry" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" placeholder="e.g. Technology, Healthcare" />
                            </div>
                        ) : (
                            <>
                                <div>
                                    <label className="block text-gray-700 dark:text-gray-300 mb-2">Experience (Years)</label>
                                    <input type="number" name="experience_level" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" />
                                </div>
                                <div>
                                    <label className="block text-gray-700 dark:text-gray-300 mb-2">Preferred Role</label>
                                    <input name="preferred_role" onChange={handleChange} className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600" placeholder="e.g. Frontend Developer" />
                                </div>
                            </>
                        )}
                    </div>

                    <button type="submit" className="btn-primary w-full py-3 mt-8">Create Account</button>
                </form>

                <p className="mt-6 text-center text-gray-600 dark:text-gray-400">
                    Already have an account? <Link to="/login" className="text-primary hover:underline">Login here</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
