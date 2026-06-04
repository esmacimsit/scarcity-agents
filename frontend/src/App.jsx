import React, { useState, useEffect } from 'react';
import './App.css';

// Lazy load components to catch import errors
const PixiWorldReplay = React.lazy(() => import('./components/PixiWorldReplay'));
const MetricsPanel = React.lazy(() => import('./components/MetricsPanel'));
const Controls = React.lazy(() => import('./components/Controls'));
const ScenarioSelector = React.lazy(() => import('./components/ScenarioSelector'));

function App() {
  const [simulationData, setSimulationData] = useState(null);
  const [currentTimestep, setCurrentTimestep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playSpeed, setPlaySpeed] = useState(1);
  const [selectedScenario, setSelectedScenario] = useState('');
  const [error, setError] = useState(null);
  const [availableScenarios, setAvailableScenarios] = useState([]);

  // Load manifest and set default scenario
  useEffect(() => {
    fetch('/logs/manifest.json')
      .then(res => res.json())
      .then(data => {
        setAvailableScenarios(data.available_scenarios || []);
        // Set default scenario to first available
        if (data.available_scenarios && data.available_scenarios.length > 0) {
          setSelectedScenario(data.available_scenarios[0]);
        }
      })
      .catch(err => console.error('Error loading manifest:', err));
  }, []);

  // Load simulation data when scenario changes
  useEffect(() => {
    if (!selectedScenario) return;
    
    fetch(`/logs/${selectedScenario}.json`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to load scenario`);
        return res.json();
      })
      .then(data => {
        if (!data || !data.step_log || data.step_log.length === 0) {
          throw new Error('Invalid scenario data: missing or empty step_log');
        }
        setSimulationData(data);
        setCurrentTimestep(0);
        setIsPlaying(false);
        setError(null);
      })
      .catch(err => {
        console.error('Error loading scenario:', err);
        setError(`Failed to load ${selectedScenario}: ${err.message}`);
      });
  }, [selectedScenario]);

  useEffect(() => {
    if (!isPlaying || !simulationData) return;
    const interval = setInterval(() => {
      setCurrentTimestep(prev => {
        const max = simulationData.step_log.length - 1;
        return prev >= max ? prev : prev + 1;
      });
    }, 100 / playSpeed);
    return () => clearInterval(interval);
  }, [isPlaying, simulationData, playSpeed]);

  if (error) return <div style={{ color: '#ff0000', padding: '20px', fontSize: '18px' }}>Error: {error}</div>;
  if (!simulationData) return <div style={{ color: '#00ff88', padding: '20px', fontSize: '18px' }}>Loading...</div>;

  const currentStepData = simulationData.step_log[currentTimestep];
  const agentsAtTimestep = simulationData.agent_log.filter(a => a.timestep === currentTimestep);

  return (
    <div className="app">
      <div className="header">
        <h1>Scarcity Agents Simulator</h1>
        <React.Suspense fallback={<div>Loading...</div>}>
          <ScenarioSelector 
            selectedScenario={selectedScenario}
            onScenarioChange={setSelectedScenario}
          />
        </React.Suspense>
      </div>

      <div className="main-container">
        <div className="world-panel">
          <React.Suspense fallback={<div>Loading...</div>}>
            <PixiWorldReplay 
              agentsData={agentsAtTimestep}
              maxWealth={20}
            />
          </React.Suspense>
        </div>

        <div className="right-panel">
          <React.Suspense fallback={<div>Loading...</div>}>
            <MetricsPanel 
              stepData={currentStepData}
              policy={simulationData.metadata.policy}
            />
          </React.Suspense>
        </div>
      </div>

      <React.Suspense fallback={<div>Loading...</div>}>
        <Controls
          currentTimestep={currentTimestep}
          maxTimestep={simulationData.step_log.length - 1}
          isPlaying={isPlaying}
          playSpeed={playSpeed}
          onTimestepChange={setCurrentTimestep}
          onPlayPause={() => setIsPlaying(!isPlaying)}
          onSpeedChange={setPlaySpeed}
        />
      </React.Suspense>
    </div>
  );
}

export default App;
