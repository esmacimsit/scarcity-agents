import React from 'react';
import './MetricsPanel.css';

const MetricsPanel = ({ stepData, policy }) => {
  if (!stepData) return null;

  const metrics = [
    { label: '👥 Alive', value: stepData.alive },
    { label: '💀 Dead Total', value: stepData.dead_total },
    { label: '🍎 Avg Food', value: (stepData.price || 0).toFixed(2) },
    { label: '💰 Price', value: stepData.price?.toFixed(2) || 'N/A' },
    { label: '📊 Gini (Survivor)', value: stepData.gini_survivor?.toFixed(3) || 'N/A' },
    { label: '📈 Gini (Population)', value: stepData.gini_population?.toFixed(3) || 'N/A' },
    { label: '🔄 Gather Count', value: stepData.gather_count },
    { label: '🏗️  Work Count', value: stepData.work_count },
  ];

  return (
    <div className="metrics-panel">
      <div className="metrics-header">
        <h2>📊 Metrics</h2>
        <div className="policy-badge">
          Policy: <strong>{policy.toUpperCase()}</strong>
        </div>
      </div>

      <div className="metrics-grid">
        {metrics.map((metric, idx) => (
          <div key={idx} className="metric-card">
            <span className="metric-label">{metric.label}</span>
            <span className="metric-value">{metric.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsPanel;
