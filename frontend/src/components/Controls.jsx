import React from 'react';
import './Controls.css';

const Controls = ({
  currentTimestep,
  maxTimestep,
  isPlaying,
  playSpeed,
  onTimestepChange,
  onPlayPause,
  onSpeedChange,
}) => {
  const speeds = [0.5, 1, 2, 5, 10];

  return (
    <div className="controls">
      <div className="control-group">
        <button
          className={`play-button ${isPlaying ? 'playing' : ''}`}
          onClick={onPlayPause}
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>

        <button className="reset-button" onClick={() => onTimestepChange(0)}>
          Reset
        </button>
      </div>

      <div className="control-group">
        <label>Speed: {playSpeed.toFixed(1)}x</label>
        <div className="speed-buttons">
          {speeds.map(speed => (
            <button
              key={speed}
              className={`speed-btn ${playSpeed === speed ? 'active' : ''}`}
              onClick={() => onSpeedChange(speed)}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>

      <div className="control-group timeline">
        <div className="timeline-label">
          Timestep: {currentTimestep} / {maxTimestep}
        </div>
        <input
          type="range"
          min="0"
          max={maxTimestep}
          value={currentTimestep}
          onChange={e => onTimestepChange(parseInt(e.target.value))}
          className="timeline-slider"
        />
      </div>
    </div>
  );
};

export default Controls;
