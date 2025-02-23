import { useState } from 'react';

interface ApiError extends Error {
    status?: number;
}

export const useClaudeApi = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const callApi = async <T>(url: string, options?: RequestInit): Promise<T> => {
        setIsLoading(true);
        setError(null);
        
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data as T;
        } catch (err) {
            const apiError = err as ApiError;
            const errorMessage = apiError.message || 'An error occurred';
            setError(`${errorMessage}${apiError.status ? ` (${apiError.status})` : ''}`);
            throw apiError;
        } finally {
            setIsLoading(false);
        }
    };

    return { isLoading, error, callApi };
};
