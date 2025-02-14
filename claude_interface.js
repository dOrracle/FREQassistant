import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MessageCircle, BrainCircuit, BarChart2, Settings, Loader } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useClaudeApi } from '../hooks/useClaudeApi';
import { API_ENDPOINTS } from '../constants/api';
import PropTypes from 'prop-types';

export const LoadingSpinner = () => (
    <div className="flex items-center justify-center">
        <Loader className="w-5 h-5 animate-spin text-blue-500" />
    </div>
);

export default function ClaudeInterface() {
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([]);
    const [mlMetrics, setMlMetrics] = useState({});
    const [isTraining, setIsTraining] = useState(false);
    const [input, setInput] = useState('');

    const { isLoading, error, callApi } = useClaudeApi();

    // Cache metrics data
    const [cachedMetrics, setCachedMetrics] = useState({
        data: null,
        timestamp: null
    });

    const fetchMetrics = useCallback(async () => {
        // Only fetch if cache is older than 5 minutes
        if (cachedMetrics.timestamp && Date.now() - cachedMetrics.timestamp < 300000) {
            setMlMetrics(cachedMetrics.data);
            return;
        }

        try {
            const data = await callApi(API_ENDPOINTS.METRICS);
            setMlMetrics(data);
            setCachedMetrics({
                data,
                timestamp: Date.now()
            });
        } catch (err) {
            // Error handling is done in useClaudeApi
        }
    }, [cachedMetrics, callApi]);

    useEffect(() => {
        if (activeTab === 'metrics') {
            fetchMetrics();
        }
    }, [activeTab, fetchMetrics]);

    const sendMessage = async (message) => {
        try {
            const data = await callApi(API_ENDPOINTS.MESSAGE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            setMessages(prev => [...prev, 
                { role: 'user', content: message },
                { role: 'assistant', content: data.response }
            ]);

            setInput('');

        } catch (err) {
            console.error(err);
        }
    };

    const clearHistory = async () => {
        try {
            await callApi(API_ENDPOINTS.CLEAR_HISTORY, {
                method: 'POST'
            });
            setMessages([]);
        } catch (err) {
            console.error(err);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (input.trim()) {
                sendMessage(input.trim());
            }
        }
    };

    const startTraining = async () => {
        try {
            await callApi(API_ENDPOINTS.START_TRAINING, {
                method: 'POST'
            });
            setIsTraining(true);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="flex h-screen bg-white dark:bg-gray-900">
            {/* Sidebar */}
            <div className="w-16 bg-gray-800 flex flex-col items-center py-4">
                <button 
                    onClick={() => setActiveTab('chat')}
                    className={`p-2 mb-4 rounded transition-colors ${
                        activeTab === 'chat' ? 'bg-blue-500' : 'hover:bg-gray-700'
                    }`}>
                    <MessageCircle className="w-6 h-6 text-white" />
                </button>
                <button 
                    onClick={() => setActiveTab('ml')}
                    className={`p-2 mb-4 rounded transition-colors ${
                        activeTab === 'ml' ? 'bg-blue-500' : 'hover:bg-gray-700'
                    }`}>
                    <BrainCircuit className="w-6 h-6 text-white" />
                </button>
                <button 
                    onClick={() => setActiveTab('metrics')}
                    className={`p-2 mb-4 rounded transition-colors ${
                        activeTab === 'metrics' ? 'bg-blue-500' : 'hover:bg-gray-700'
                    }`}>
                    <BarChart2 className="w-6 h-6 text-white" />
                </button>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <div className="h-16 bg-gray-100 dark:bg-gray-800 flex items-center px-4 justify-between">
                    <h1 className="text-xl font-bold dark:text-white">Claude AI Assistant</h1>
                    <div className="flex items-center gap-4">
                        {isLoading && <Loader className="w-5 h-5 animate-spin" />}
                        <button 
                            onClick={clearHistory}
                            disabled={isLoading}
                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50">
                            Clear History
                        </button>
                    </div>
                </div>

                {/* Error Display */}
                {error && (
                    <Alert variant="destructive" className="m-4">
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {/* Content Area */}
                <div className="flex-1 overflow-hidden p-4">
                    {activeTab === 'chat' && (
                        <div className="h-full flex flex-col">
                            <div className="flex-1 overflow-y-auto">
                                {messages.map((msg, i) => (
                                    <div key={i} className="mb-4">
                                        <div className={`p-3 rounded ${
                                            msg.role === 'user' 
                                                ? 'bg-blue-100 dark:bg-blue-900' 
                                                : 'bg-gray-100 dark:bg-gray-800'
                                        }`}>
                                            {msg.content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            
                            <div className="h-24 border-t dark:border-gray-700">
                                <textarea 
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    disabled={isLoading}
                                    className="w-full h-full p-2 resize-none bg-white dark:bg-gray-800 
                                             dark:text-white focus:ring-2 focus:ring-blue-500 
                                             outline-none"
                                    placeholder="Type your message..."
                                />
                            </div>
                        </div>
                    )}

                    {activeTab === 'ml' && (
                        <div className="dark:text-white">
                            <h2 className="text-xl mb-4">ML Training Status</h2>
                            {isTraining ? (
                                <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded">
                                    <h3>Currently Training</h3>
                                    <div className="flex items-center mt-2">
                                        <Loader className="w-5 h-5 animate-spin mr-2" />
                                        <span>Training in progress...</span>
                                    </div>
                                </div>
                            ) : (
                                <div className="p-4 bg-green-100 dark:bg-green-900 rounded">
                                    <h3>Ready for Training</h3>
                                    <button 
                                        onClick={startTraining}
                                        disabled={isLoading}
                                        className="px-4 py-2 bg-blue-500 text-white rounded mt-2 
                                                 hover:bg-blue-600 disabled:opacity-50">
                                        Start New Training
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'metrics' && (
                        <div className="dark:text-white">
                            <h2 className="text-xl mb-4">Performance Metrics</h2>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={mlMetrics}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Line type="monotone" dataKey="accuracy" stroke="#8884d8" />
                                        <Line type="monotone" dataKey="loss" stroke="#82ca9d" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}