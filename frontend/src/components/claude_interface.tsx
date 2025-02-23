import * as React from 'react';
import { useState, useCallback } from 'react';
import { MessageCircle, BrainCircuit, BarChart2, Loader } from 'lucide-react';
import { useClaudeApi } from '../hooks/useClaudeApi';
import { TabType, Message } from '../types';
import TabButton from './TabButton';
import ChatPanel from './ChatPanel';
import MLPanel from './MLPanel';
import MetricsPanel from './MetricsPanel';

const LoadingSpinner: React.FC = () => (
    <div className="flex items-center justify-center">
        <Loader className="w-5 h-5 animate-spin text-blue-500" />
    </div>
);

interface ClaudeInterfaceProps {
    initialMessages?: Message[];
    onError?: (error: string) => void;
}

const ClaudeInterface: React.FC<ClaudeInterfaceProps> = ({ 
    initialMessages = [], 
    onError 
}) => {
    const [activeTab, setActiveTab] = useState<TabType>('chat');
    const { isLoading, error } = useClaudeApi();

    const handleTabClick = useCallback((tab: TabType) => {
        setActiveTab(tab);
    }, []);

    const renderTab = useCallback((tab: TabType, icon: React.ReactNode, label: string) => (
        <TabButton
            tab={tab}
            icon={icon}
            label={label}
            isSelected={activeTab === tab}
            onClick={handleTabClick}
        />
    ), [activeTab, handleTabClick]);

    return (
        <div className="flex h-screen bg-white dark:bg-gray-900" role="main">
            <nav aria-label="Main navigation">
                <ul role="tablist" aria-label="Interface sections">
                    {renderTab('chat', <MessageCircle className="w-6 h-6 text-white" />, 'Chat')}
                    {renderTab('ml', <BrainCircuit className="w-6 h-6 text-white" />, 'ML')}
                    {renderTab('metrics', <BarChart2 className="w-6 h-6 text-white" />, 'Metrics')}
                </ul>
            </nav>

            <div className="flex-1 flex flex-col overflow-hidden">
                <div className="h-16 bg-gray-100 dark:bg-gray-800 flex items-center px-4 justify-between">
                    <h1 className="text-xl font-bold dark:text-white">Claude AI Assistant</h1>
                    {isLoading && <LoadingSpinner />}
                </div>

                {error && (
                    <div className="m-4 p-4 bg-red-100 text-red-700 rounded" role="alert">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                <div className="flex-1 overflow-hidden p-4">
                    <div 
                        role="tabpanel"
                        id={`panel-${activeTab}`}
                        aria-labelledby={`tab-${activeTab}`}
                        className="h-full"
                    >
                        {activeTab === 'chat' && (
                            <ChatPanel 
                                initialMessages={initialMessages}
                                onError={onError}
                            />
                        )}
                        {activeTab === 'ml' && (
                            <MLPanel 
                                onError={onError}
                            />
                        )}
                        {activeTab === 'metrics' && (
                            <MetricsPanel 
                                onError={onError}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ClaudeInterface;
