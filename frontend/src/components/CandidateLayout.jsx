import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import { FileUp, Search, User, LogOut } from 'lucide-react';

const CandidateLayout = () => {
    const { user, logout } = useAuth();
    const location = useLocation();

    const menuItems = [
        { icon: <FileUp size={20} />, label: 'Upload CV', path: '/candidate/dashboard' },
        { icon: <Search size={20} />, label: 'Browse Jobs', path: '/candidate/jobs' },
        { icon: <User size={20} />, label: 'My Profile', path: '/candidate/profile' },
    ];

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <div className="w-64 bg-white border-r border-gray-100 flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-primary">Bug-Busters</h1>
                    <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Candidate Portal</p>
                </div>

                <nav className="flex-1 px-4 space-y-1">
                    {menuItems.map((item) => {
                        const isActive = location.pathname === item.path || (item.path === '/candidate/dashboard' && location.pathname === '/candidate');
                        return (
                            <Link
                                key={item.label}
                                to={item.path}
                                className={`flex items-center space-x-3 p-3 rounded-md transition ${isActive
                                    ? 'bg-gray-100 text-primary font-semibold'
                                    : 'text-gray-500 hover:bg-gray-50'
                                    }`}
                            >
                                {item.icon}
                                <span className="text-sm font-medium">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <button onClick={logout} className="flex items-center space-x-3 w-full p-3 text-red-500 hover:bg-red-50 rounded-md transition-colors">
                        <LogOut size={18} />
                        <span className="text-sm font-medium">Logout</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Navbar */}
                <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-8">
                    <h2 className="text-lg font-semibold text-gray-800">
                        {menuItems.find(item => item.path === location.pathname)?.label || 'Candidate Portal'}
                    </h2>
                    <div className="flex items-center space-x-4">
                        <div className="text-right mr-2">
                            <p className="text-xs font-bold text-gray-900">{user?.name}</p>
                            <p className="text-[10px] text-gray-500 uppercase tracking-tight">{user?.role}</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-secondary text-white flex items-center justify-center font-bold">
                            {user?.name?.[0].toUpperCase()}
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <main className="flex-1 overflow-y-auto p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default CandidateLayout;
