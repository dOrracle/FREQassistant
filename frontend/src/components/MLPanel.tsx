import * as React from 'react';
import { useState } from 'react';
import { useClaudeApi } from '../hooks/useClaudeApi';

interface MLPanelProps {
    onError?: (error: string) => void;
}

const MLPanel: React.FC<MLPanelProps> = ({ onError }) => {
    const [description, setDescription] = useState('');
    const { isLoading, error, callApi } = useClaudeApi();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!description.trim()) return;

        try {
            const response = await callApi<{status: string}>('/api/v1/claude/start-training', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });

            setDescription('');
        } catch (err) {
            if (onError) onError(err instanceof Error ? err.message : 'An error occurred');
        }
    };

    return (
        <div className="p-4">
            <h2 className="text-xl mb-4">ML Model Training</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="description" className="block mb-2">
                        Strategy Description
                    </label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        className="w-full p-2 border rounded"
                        rows={4}
                        placeholder="Describe your trading strategy..."
                        disabled={isLoading}
                    />
                </div>
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
                <button
                    type="submit"
                    disabled={isLoading || !description.trim()}
                    className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
                >
                    Start Training
                </button>
            </form>
        </div>
    );
};

export default MLPanel;
