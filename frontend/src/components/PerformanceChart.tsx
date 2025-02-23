import * as React from 'react';
import { LineChart, Line, ResponsiveContainer, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts';
import { Metrics } from '../types';

interface PerformanceChartProps {
    data: Metrics[];
    darkMode?: boolean;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ data, darkMode = false }) => {
    const textColor = darkMode ? '#fff' : '#666';
    
    return (
        <div 
            className="h-64 w-full"
            role="region"
            aria-label="Performance metrics chart"
        >
            <ResponsiveContainer>
                <LineChart 
                    data={data}
                    margin={{ top: 10, right: 10, bottom: 20, left: 10 }}
                >
                    <CartesianGrid 
                        strokeDasharray="3 3" 
                        stroke={darkMode ? '#444' : '#ccc'}
                    />
                    <XAxis
                        dataKey="name"
                        stroke={textColor}
                        label={{ 
                            value: 'Timeline',
                            position: 'bottom',
                            style: { fill: textColor }
                        }}
                    />
                    <YAxis
                        stroke={textColor}
                        label={{ 
                            value: 'Values',
                            angle: -90,
                            position: 'left',
                            style: { fill: textColor }
                        }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: darkMode ? 'rgba(0, 0, 0, 0.85)' : 'rgba(255, 255, 255, 0.95)',
                            border: `1px solid ${darkMode ? '#444' : '#ccc'}`,
                            borderRadius: '4px',
                            color: textColor
                        }}
                    />
                    <Line
                        type="monotone"
                        dataKey="accuracy"
                        stroke="#8884d8"
                        name="Accuracy"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="loss"
                        stroke="#82ca9d"
                        name="Loss"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PerformanceChart;
