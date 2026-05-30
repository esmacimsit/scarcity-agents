import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import './ChartsPanel.css';

const ChartsPanel = ({ stepLog, currentTimestep }) => {
  // Prepare data for charts
  const chartData = stepLog.slice(0, currentTimestep + 1).map(step => ({
    timestep: step.timestep,
    alive: step.alive,
    price: step.price,
    gini: step.gini_survivor,
  }));

  return (
    <div className="charts-panel">
      <h3>📈 Live Metrics</h3>

      <div className="chart-container">
        <h4>Alive Agents</h4>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="timestep" stroke="#888" fontSize={10} />
            <YAxis stroke="#888" fontSize={10} />
            <Line 
              type="monotone" 
              dataKey="alive" 
              stroke="#00ff88" 
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h4>Price Over Time</h4>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="timestep" stroke="#888" fontSize={10} />
            <YAxis stroke="#888" fontSize={10} />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#ff00ff" 
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h4>Gini Index</h4>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="timestep" stroke="#888" fontSize={10} />
            <YAxis stroke="#888" fontSize={10} />
            <Line 
              type="monotone" 
              dataKey="gini" 
              stroke="#ffff00" 
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChartsPanel;
