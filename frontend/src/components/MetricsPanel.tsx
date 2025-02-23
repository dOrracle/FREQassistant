import * as React from 'react';
import PerformanceChart from './PerformanceChart';
import { Metrics } from '../types';

interface MetricsPanelProps {
    onError?: (error: string) => void;
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ onError }) => {
    const [metricsData, setMetricsData] = React.useState<Metrics[]>([]);

    const handleError = (error: unknown) => {
        const errorMessage = error instanceof Error ? error.message : String(error);
        onError?.(errorMessage);
    };

    React.useEffect(() => {
        // Fetch metrics data here and set it to metricsData
        const fetchMetricsData = async () => {
            try {
                const response = await fetch('/api/metrics');
                const data: Metrics[] = await response.json();
                setMetricsData(data);
            } catch (error) {
                handleError(error);
            }
        };

        fetchMetricsData();
    }, [onError]);

    return (
        <div>
            <h2 className="text-xl mb-4">Performance Metrics</h2>
            <PerformanceChart data={metricsData} darkMode={false} />
        </div>
    );
};

export default MetricsPanel;