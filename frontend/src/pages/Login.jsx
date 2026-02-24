import React, { useState } from 'react';
import { useAuth } from '../services/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await login(email, password);
            // res is the user object directly from FastAPI
            navigate(res.role === 'recruiter' ? '/recruiter' : '/candidate');
        } catch (err) {
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-dark">
            <div className="card w-full max-w-md">
                <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Sign in to Bug-Busters</h2>
                <p className="text-center text-gray-600 dark:text-gray-400 mb-8">Login to your account</p>

                {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Email Address</label>
                        <input
                            type="email"
                            className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 outline-none focus:border-primary"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Password</label>
                        <input
                            type="password"
                            className="w-full p-3 rounded-lg border dark:bg-gray-700 dark:border-gray-600 outline-none focus:border-primary"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn-primary w-full py-3">Login</button>
                </form>

                <p className="mt-6 text-center text-gray-600 dark:text-gray-400">
                    Don't have an account? <Link to="/register" className="text-primary hover:underline">Register here</Link>
                </p>
            </div>
        </div>
    );
};

export default Login;
