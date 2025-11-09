/**
 * Waveform visualizer component for showing audio recording animation.
 */
import React, { useEffect, useRef } from 'react';
import './WaveformVisualizer.css';

const WaveformVisualizer = ({ isActive }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!isActive) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const bars = 50;
    const barWidth = width / bars;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw animated bars
      for (let i = 0; i < bars; i++) {
        // Create wave effect with different frequencies
        const time = Date.now() / 1000;
        const frequency = 2 + Math.sin(i / 10);
        const amplitude = 20 + Math.sin(time * frequency + i / 5) * 15;

        const barHeight = amplitude;
        const x = i * barWidth;
        const y = (height - barHeight) / 2;

        // Gradient color
        const gradient = ctx.createLinearGradient(0, 0, 0, height);
        gradient.addColorStop(0, '#1890ff');
        gradient.addColorStop(1, '#096dd9');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth - 2, barHeight);
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  return (
    <div className="waveform-visualizer">
      <canvas
        ref={canvasRef}
        width={800}
        height={100}
        className="waveform-canvas"
      />
    </div>
  );
};

export default WaveformVisualizer;
