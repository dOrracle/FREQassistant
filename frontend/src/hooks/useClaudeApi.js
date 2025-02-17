import { useState, useCallback } from 'react';

export const useClaudeApi = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const callApi = useCallback(async (endpoint, options = {}) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    ...options.headers,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { isLoading, error, callApi };
};