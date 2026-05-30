import React, { useEffect, useRef, useMemo } from 'react';
import './PixiWorldReplay.css';

const PixiWorldReplay = ({ agentsData = [], maxWealth = 20 }) => {
  const canvasRef = useRef(null);
  
  // Generate deterministic positions for agents based on agent_id
  const agentPositions = useMemo(() => {
    const positions = {};
    agentsData.forEach(agent => {
      if (!positions[agent.agent_id]) {
        // Use agent_id to generate consistent position (0-1 range)
        const seed = agent.agent_id;
        // Simple pseudo-random based on seed
        const x = ((seed * 9.2103404712) % 1);
        const y = ((seed * 2.3160169283) % 1);
        positions[agent.agent_id] = { x, y };
      }
    });
    return positions;
  }, [agentsData]);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = 600;
    canvas.height = 500;

    // Dark background
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 20; i++) {
      const pos = (i / 20);
      const x = pos * canvas.width;
      const y = pos * canvas.height;
      
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw agents
    agentsData.forEach(agent => {
      const pos = agentPositions[agent.agent_id] || { x: 0.5, y: 0.5 };
      const x = pos.x * canvas.width;
      const y = pos.y * canvas.height;
      const radius = 6;

      // Color based on wealth
      let color = '#00ff88'; // default green
      if (agent.wealth > maxWealth * 0.7) {
        color = '#ff00ff'; // magenta if rich
      } else if (agent.wealth < maxWealth * 0.3) {
        color = '#ff0000'; // red if poor
      }

      // Gray out if dead
      if (agent.alive === false || agent.alive === 0 || agent.alive === 'False') {
        color = '#555555';
      }

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw outline
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw agent ID label for debugging
      ctx.fillStyle = '#00ff88';
      ctx.font = '10px Courier New';
      ctx.fillText(agent.agent_id, x + 8, y - 8);
    });

  }, [agentsData, maxWealth, agentPositions]);

  return <canvas ref={canvasRef} className="pixi-canvas" />;
};

export default PixiWorldReplay;
