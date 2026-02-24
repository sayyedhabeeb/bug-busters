import React from 'react';
import { User, Bell, Shield, Database, Save } from 'lucide-react';

const Settings = () => {
    return (
        <div className="max-w-4xl space-y-8">
            <h2 className="text-2xl font-bold">Portal Settings</h2>

            <div className="card space-y-6">
                <div className="flex items-center space-x-4 border-b dark:border-gray-700 pb-6">
                    <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-2xl text-white font-bold">
                        R
                    </div>
                    <div>
                        <h3 className="text-xl font-bold">Company Profile</h3>
                        <p className="text-gray-500">Manage your organization details and logo</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-1">Company Name</label>
                        <input className="w-full p-2 rounded border dark:bg-gray-700 dark:border-gray-600" defaultValue="Acme Corp" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Recruiter Email</label>
                        <input className="w-full p-2 rounded border dark:bg-gray-700 dark:border-gray-600" defaultValue="recruiter@acme.com" />
                    </div>
                </div>

                <div className="space-y-4">
                    <h4 className="font-bold border-b dark:border-gray-700 pb-2 flex items-center">
                        <Bell size={18} className="mr-2" /> Notifications
                    </h4>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">New Candidate Alert</p>
                            <p className="text-xs text-gray-500">Get notified when someone matches your job role above 80%</p>
                        </div>
                        <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">System Training Complete</p>
                            <p className="text-xs text-gray-500">Notify when AI model retraining is finished</p>
                        </div>
                        <input type="checkbox" className="w-5 h-5 accent-primary" />
                    </div>
                </div>

                <div className="flex justify-end pt-4">
                    <button className="btn-primary flex items-center space-x-2">
                        <Save size={18} />
                        <span>Save Changes</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Settings;
