import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './services/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import RecruiterDashboard from './pages/RecruiterPortal/Dashboard';
import CandidateDashboard from './pages/CandidatePortal/Dashboard';

import RecruiterLayout from './components/RecruiterLayout';
import CandidateLayout from './components/CandidateLayout';

import Candidates from './pages/RecruiterPortal/Candidates';
import Applications from './pages/RecruiterPortal/Applications';
import Analytics from './pages/RecruiterPortal/Analytics';
import Settings from './pages/RecruiterPortal/Settings';

import Jobs from './pages/CandidatePortal/Jobs';
import Profile from './pages/CandidatePortal/Profile';
import JobRoles from './pages/RecruiterPortal/JobRoles';
import CVUpload from './pages/CandidatePortal/CVUpload';

const ProtectedRoute = ({ children, role }) => {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading Session...</div>;
    if (!user) return <Navigate to="/login" />;
    if (role && user.role !== role) return <Navigate to="/" />;
    return children;
};

const AppRoutes = () => {
    const { user } = useAuth();

    return (
        <Routes>
            <Route path="/login" element={!user ? <Login /> : <Navigate to={user.role === 'recruiter' ? '/recruiter/dashboard' : '/candidate/dashboard'} />} />
            <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />

            <Route path="/recruiter" element={<ProtectedRoute role="recruiter"><RecruiterLayout /></ProtectedRoute>}>
                <Route index element={<Navigate to="dashboard" />} />
                <Route path="dashboard" element={<RecruiterDashboard />} />
                <Route path="jobs" element={<JobRoles />} />
                <Route path="applications" element={<Applications />} />
                <Route path="candidates" element={<Candidates />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="settings" element={<Settings />} />
            </Route>

            <Route path="/candidate" element={<ProtectedRoute role="candidate"><CandidateLayout /></ProtectedRoute>}>
                <Route index element={<Navigate to="dashboard" />} />
                <Route path="dashboard" element={<CandidateDashboard />} />
                <Route path="upload" element={<CVUpload />} />
                <Route path="jobs" element={<Jobs />} />
                <Route path="profile" element={<Profile />} />
            </Route>

            <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
    );
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen">
                    <AppRoutes />
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
