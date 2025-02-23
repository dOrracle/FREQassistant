export type TabType = 'chat' | 'ml' | 'metrics';
export interface ApiResponse {
   response: string;
}
export interface Message {
   role: 'user' | 'assistant';
   content: string;
}
export interface Metrics {
   name: string;
   accuracy: number;
   loss: number;
}
export interface ErrorProps {
   message: string;
}

// Add minimal component and render code
import React from 'react';
import ReactDOM from 'react-dom';

const App = () => <div>FreqAI Assistant</div>;
ReactDOM.render(<App />, document.getElementById('root') || document.createElement('div'));

export default App;