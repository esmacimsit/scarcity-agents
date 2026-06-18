import React, { useEffect, useRef, useMemo, useState } from 'react';
import './PixiWorldReplay.css';

import aliveImageSrc from '../../../karakter/canlı.jpeg';
import deadImageSrc from '../../../karakter/ölü.jpeg';

const aliveImage = new Image();
aliveImage.src = aliveImageSrc;

const deadImage = new Image();
deadImage.src = deadImageSrc;

const PixiWorldReplay = ({ agentsData = [], currentStep = 0, maxWealth = 20 }) => {
  const canvasRef = useRef(null);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  
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

  // Resimlerin yüklenmesini bekle ve yüklendiğinde canvas'ı tekrar çizmesi için state'i güncelle
  useEffect(() => {
    let loaded = 0;
    const onLoad = () => {
      loaded += 1;
      if (loaded >= 2) setImagesLoaded(true);
    };

    if (aliveImage.complete && aliveImage.naturalWidth > 0) onLoad(); else aliveImage.onload = onLoad;
    if (deadImage.complete && deadImage.naturalWidth > 0) onLoad(); else deadImage.onload = onLoad;
    
    aliveImage.onerror = () => console.error("canlı.jpeg yüklenemedi. Çözümlenen yol:", aliveImageSrc);
    deadImage.onerror = () => console.error("ölü.jpeg yüklenemedi. Çözümlenen yol:", deadImageSrc);
  }, []);

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
    
    // CSV'den gelen tüm ajan verisini timestep'e (mevcut adıma) göre filtrele
    // Eğer timestep verisi yoksa veya filtre boş dönerse tamamını kullan
    const currentAgents = agentsData.filter(
      agent => agent.timestep === currentStep || agent.step === currentStep
    );
    const agentsToDraw = currentAgents.length > 0 ? currentAgents : agentsData;

    // Draw agents
    agentsToDraw.forEach(agent => {
      let x, y;
      
      // Simülasyondan gelen gerçek pozisyonları (grid: 20x20) kullanmayı dene
      if (agent.pos && Array.isArray(agent.pos)) {
        x = (agent.pos[0] + 0.5) * (canvas.width / 20);
        y = (agent.pos[1] + 0.5) * (canvas.height / 20);
      } else if (agent.x !== undefined && agent.y !== undefined) {
        x = (agent.x + 0.5) * (canvas.width / 20);
        y = (agent.y + 0.5) * (canvas.height / 20);
      } else {
        // Yoksa rastgele üretilen pozisyonları kullan
        const pos = agentPositions[agent.agent_id] || { x: 0.5, y: 0.5 };
        x = pos.x * canvas.width;
        y = pos.y * canvas.height;
      }

      const imgSize = 24; // Karelere daha iyi sığması için 32'den 24'e küçültüldü
      const haloRadius = (imgSize / 2) + 4; // Resmin etrafında duracak zenginlik halesi

      // Color based on wealth
      let color = '#00ff88'; // default green
      if (agent.wealth > maxWealth * 0.7) {
        color = '#ff00ff'; // magenta if rich
      } else if (agent.wealth < maxWealth * 0.3) {
        color = '#ff0000'; // red if poor
      }

      const isDead = agent.alive === false || agent.alive === 0 || agent.alive === 'False';

      // Gray out if dead
      if (isDead) {
        color = '#555555';
      }

      // Arkasına zenginlik/durum rengini gösteren hafif bir hale çiziyoruz
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.4;
      ctx.beginPath();
      ctx.arc(x, y, haloRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1.0;

      const currentImage = isDead ? deadImage : aliveImage;

      if (imagesLoaded && currentImage.complete && currentImage.naturalWidth > 0) {
        // Resim hazırsa karakterin resmini çiz
        ctx.save();
        
        // JPEG resimleri kare olduğu için onları çember şeklinde kırpıyoruz
        ctx.beginPath();
        ctx.arc(x, y, imgSize / 2, 0, Math.PI * 2);
        ctx.closePath();
        ctx.clip();
        
        ctx.drawImage(currentImage, x - imgSize / 2, y - imgSize / 2, imgSize, imgSize);
        
        ctx.restore();
      } else {
        // Resim yoksa veya henüz yüklenmediyse eski yuvarlak şekli çiz (Fallback)
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, imgSize / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      
      // Draw agent ID label for debugging
      ctx.fillStyle = '#00ff88';
      ctx.font = '10px Courier New';
      ctx.fillText(agent.agent_id, x + 8, y - 8);
    });

  }, [agentsData, currentStep, maxWealth, agentPositions, imagesLoaded]);

  return <canvas ref={canvasRef} className="pixi-canvas" />;
};

export default PixiWorldReplay;
