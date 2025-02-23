import * as React from 'react';
import { useState } from 'react';
import { Message } from '../types';
import { useClaudeApi } from '../hooks/useClaudeApi';

interface ChatPanelProps {
    initialMessages?: Message[];
    onError?: (error: string) => void;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ initialMessages = [], onError }) => {
    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [input, setInput] = useState('');
    const { isLoading, error, callApi } = useClaudeApi();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            content: input,
            role: 'user',
            timestamp: Date.now()
        };

        try {
            setMessages(prev => [...prev, newMessage]);
            setInput('');

            const response = await callApi<{response: string}>('/api/v1/claude/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: input })
            });

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                content: response.response,
                role: 'assistant',
                timestamp: Date.now()
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            if (onError) onError(err instanceof Error ? err.message : 'An error occurred');
        }
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto p-4">
                {messages.map(message => (
                    <div 
                        key={message.id}
                        className={`mb-4 p-3 rounded-lg ${
                            message.role === 'user' 
                                ? 'bg-blue-100 ml-auto' 
                                : 'bg-gray-100'
                        }`}
                    >
                        {message.content}
                    </div>
                ))}
                {isLoading && (
                    <div className="text-gray-500">Claude is thinking...</div>
                )}
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
            </div>
            <form onSubmit={handleSubmit} className="p-4 border-t">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-2 border rounded"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatPanel;
