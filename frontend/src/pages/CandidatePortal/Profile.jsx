import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../services/AuthContext';
import { User, Mail, Phone, MapPin, Code, Briefcase, GraduationCap, Save, Loader2 } from 'lucide-react';

const Profile = () => {
    const { user } = useAuth();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            if (!user) return;
            try {
                const res = await axios.get(`http://localhost:8000/api/candidates/me/${user.id}`);
                setProfile(res.data);
            } catch (err) {
                console.error("Failed to fetch profile", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [user]);

    if (loading) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-secondary" size={40} />
        </div>
    );

    return (
        <div className="max-w-4xl space-y-8">
            <h2 className="text-2xl font-bold">Personal Profile</h2>

            <div className="card space-y-8">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6 border-b dark:border-gray-700 pb-8">
                    <div className="w-24 h-24 rounded-full bg-secondary flex items-center justify-center text-4xl text-white font-bold">
                        {profile?.name?.charAt(0) || 'C'}
                    </div>
                    <div className="text-center md:text-left flex-1">
                        <h3 className="text-2xl font-bold">{profile?.name}</h3>
                        <p className="text-gray-500">{profile?.preferred_role || 'Candidate'} with {profile?.experience_years} years experience</p>
                        <div className="mt-2 flex flex-wrap justify-center md:justify-start gap-2">
                            {profile?.skills?.length > 0 ? (
                                profile.skills.map(skill => (
                                    <span key={skill} className="px-3 py-1 bg-secondary/10 text-secondary text-xs font-bold rounded-full">
                                        {skill}
                                    </span>
                                ))
                            ) : (
                                <span className="text-xs text-gray-400 italic">No skills extracted from resume yet</span>
                            )}
                        </div>
                    </div>
                    <button className="btn-secondary px-6">Edit Profile</button>
                </div>

                {/* Info Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                        <h4 className="font-bold border-b dark:border-gray-700 pb-2 flex items-center">
                            <User size={18} className="mr-2" /> Contact Information
                        </h4>
                        <div className="space-y-2">
                            <p className="flex items-center text-sm"><Mail size={16} className="mr-3 text-gray-400" /> {profile?.email}</p>
                            <p className="flex items-center text-sm"><Phone size={16} className="mr-3 text-gray-400" /> Not Provided</p>
                            <p className="flex items-center text-sm"><MapPin size={16} className="mr-3 text-gray-400" /> Remote</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <h4 className="font-bold border-b dark:border-gray-700 pb-2 flex items-center">
                            <GraduationCap size={18} className="mr-2" /> Education
                        </h4>
                        <div className="space-y-2">
                            <p className="font-medium text-sm">Computer Science Background</p>
                            <p className="text-xs text-gray-500 italic">Extracted from resume analysis</p>
                        </div>
                    </div>
                </div>

                {/* Experience Section */}
                <div className="space-y-4">
                    <h4 className="font-bold border-b dark:border-gray-700 pb-2 flex items-center">
                        <Briefcase size={18} className="mr-2" /> Work Experience Highlights
                    </h4>
                    <div className="space-y-6">
                        <div className="relative pl-6 border-l-2 border-gray-100 dark:border-gray-700">
                            <div className="absolute left-[-9px] top-1 w-4 h-4 rounded-full bg-secondary border-4 border-white dark:border-gray-800"></div>
                            <p className="font-bold">{profile?.preferred_role || 'Software professional'}</p>
                            <p className="text-sm text-gray-500 mb-2">{profile?.experience_years} Years Experience</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                                Summary data extracted from resume processing and profile settings.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end pt-4">
                    <button className="btn-secondary flex items-center space-x-2">
                        <Save size={18} />
                        <span>Update Skills & Bio</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Profile;
