import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkSession = () => {
            const savedUser = localStorage.getItem('bugbusters_user');
            if (savedUser) {
                try {
                    setUser(JSON.parse(savedUser));
                } catch (e) {
                    console.error('Failed to parse saved user', e);
                    localStorage.removeItem('bugbusters_user');
                }
            }
            setLoading(false);
        };
        checkSession();
    }, []);

    const login = async (email, password) => {
        const response = await axios.post('http://localhost:8000/api/auth/login', { email, password });
        if (response.data) {
            setUser(response.data);
            localStorage.setItem('bugbusters_user', JSON.stringify(response.data));
        }
        return response.data;
    };

    const logout = async () => {
        setUser(null);
        localStorage.removeItem('bugbusters_user');
    };

    const register = async (userData) => {
        const response = await axios.post('http://localhost:8000/api/auth/register', userData);
        // After registration, we don't automatically log in yet, 
        // but the login logic above handles persistence.
        return response.data;
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
