import React from 'react';
import { BarChart3, TrendingUp, Users, Target } from 'lucide-react';

const Analytics = () => {
    return (
        <div className="space-y-8">
            <h2 className="text-2xl font-bold">Recruitment Analytics</h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="card p-6 border-l-4 border-blue-500">
                    <p className="text-gray-500 text-sm mb-1">Applications</p>
                    <h3 className="text-3xl font-bold">1,284</h3>
                    <p className="text-green-500 text-xs mt-2 flex items-center">
                        <TrendingUp size={12} className="mr-1" /> +12% from last month
                    </p>
                </div>
                <div className="card p-6 border-l-4 border-green-500">
                    <p className="text-gray-500 text-sm mb-1">Matches Found</p>
                    <h3 className="text-3xl font-bold">842</h3>
                    <p className="text-green-500 text-xs mt-2 flex items-center">
                        <TrendingUp size={12} className="mr-1" /> +5% from last month
                    </p>
                </div>
                <div className="card p-6 border-l-4 border-purple-500">
                    <p className="text-gray-500 text-sm mb-1">Avg. Quality</p>
                    <h3 className="text-3xl font-bold">76%</h3>
                    <p className="text-red-500 text-xs mt-2 flex items-center">
                        -2% from last month
                    </p>
                </div>
                <div className="card p-6 border-l-4 border-amber-500">
                    <p className="text-gray-500 text-sm mb-1">Hires Made</p>
                    <h3 className="text-3xl font-bold">24</h3>
                    <p className="text-green-500 text-xs mt-2 flex items-center">
                        <TrendingUp size={12} className="mr-1" /> +2 from last month
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="card h-64 flex flex-col items-center justify-center text-gray-400 italic">
                    <BarChart3 size={48} className="mb-4 text-gray-300" />
                    <p>Skill Matching Trends Chart</p>
                    <p className="text-xs mt-2">(Interactive Chart Placeholder)</p>
                </div>
                <div className="card h-64 flex flex-col items-center justify-center text-gray-400 italic">
                    <Target size={48} className="mb-4 text-gray-300" />
                    <p>Source Contribution Analytics</p>
                    <p className="text-xs mt-2">(Interactive Pie Placeholder)</p>
                </div>
            </div>
        </div>
    );
};

export default Analytics;
