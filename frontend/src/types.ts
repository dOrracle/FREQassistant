export type TabType = 'chat' | 'ml' | 'metrics';

export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: number;
}

export interface Metrics {
    name: string;
    accuracy: number;
    loss: number;
}
