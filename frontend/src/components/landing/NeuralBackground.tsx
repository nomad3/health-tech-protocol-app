import React, { useCallback, useEffect, useRef } from 'react';

const config = {
  particleCount: 120,
  connectionDistance: 140,
  mouseDistance: 200,
  electricDistance: 120,
  colors: {
    primary: '#14b8a6', // teal-500
    secondary: '#818cf8', // indigo-400
    accent: '#c084fc', // purple-400
  },
};

interface ParticleData {
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  vx: number;
  vy: number;
  size: number;
  baseSize: number;
  color: string;
  floatOffset: number;
  floatSpeed: number;
  floatRadius: number;
  baseAlpha: number;
  alpha: number;
  isElectric: boolean;
}

const NeuralBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef<{ x: number | null; y: number | null }>({ x: null, y: null });
  const particlesRef = useRef<ParticleData[]>([]);
  const animationRef = useRef<number>(0);
  const dimensionsRef = useRef({ width: 0, height: 0 });

  const createParticle = useCallback((width: number, height: number): ParticleData => {
    const x = Math.random() * width;
    const y = Math.random() * height;
    const color = Math.random() > 0.5 ? config.colors.primary :
      Math.random() > 0.5 ? config.colors.secondary : config.colors.accent;
    const baseAlpha = 0.4 + Math.random() * 0.3;

    return {
      x,
      y,
      baseX: x,
      baseY: y,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 2.5 + 1.5,
      baseSize: Math.random() * 2.5 + 1.5,
      color,
      floatOffset: Math.random() * Math.PI * 2,
      floatSpeed: 0.01 + Math.random() * 0.02,
      floatRadius: 2 + Math.random() * 4,
      baseAlpha,
      alpha: baseAlpha,
      isElectric: false,
    };
  }, []);

  const initParticles = useCallback((width: number, height: number) => {
    particlesRef.current = [];
    for (let i = 0; i < config.particleCount; i++) {
      particlesRef.current.push(createParticle(width, height));
    }
  }, [createParticle]);

  const updateParticle = useCallback((p: ParticleData, mouse: { x: number | null; y: number | null }) => {
    // Floating animation
    p.floatOffset += p.floatSpeed;
    p.baseX += p.vx;
    p.baseY += p.vy;

    // Bounce off edges
    const { width, height } = dimensionsRef.current;
    if (p.baseX < 0 || p.baseX > width) p.vx *= -1;
    if (p.baseY < 0 || p.baseY > height) p.vy *= -1;

    p.x = p.baseX + Math.sin(p.floatOffset) * p.floatRadius;
    p.y = p.baseY + Math.cos(p.floatOffset * 0.7) * p.floatRadius;
    p.isElectric = false;

    if (mouse.x !== null && mouse.y !== null) {
      const dx = mouse.x - p.x;
      const dy = mouse.y - p.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < config.mouseDistance) {
        const proximity = 1 - distance / config.mouseDistance;
        p.alpha = p.baseAlpha + proximity * 0.4;
        p.size = p.baseSize + proximity * 3;

        if (distance < config.electricDistance) {
          p.isElectric = true;
        }
      } else {
        p.alpha = p.baseAlpha;
        p.size = p.baseSize;
      }
    }
  }, []);

  const drawParticle = useCallback((ctx: CanvasRenderingContext2D, p: ParticleData) => {
    if (p.isElectric) {
      ctx.shadowBlur = 25;
      ctx.shadowColor = p.color;
    } else {
      ctx.shadowBlur = 15;
      ctx.shadowColor = p.color;
    }

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.globalAlpha = p.alpha;
    ctx.fill();

    // Extra bright core for electric nodes
    if (p.isElectric) {
      ctx.globalAlpha = 0.95;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * 0.4, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.shadowBlur = 0;
  }, []);

  const drawElectricConnections = useCallback((ctx: CanvasRenderingContext2D, mouse: { x: number | null; y: number | null }, particles: ParticleData[]) => {
    if (mouse.x === null || mouse.y === null) return;

    const electricNodes = particles
      .filter((p) => {
        const dx = mouse.x! - p.x;
        const dy = mouse.y! - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        return dist < config.electricDistance;
      })
      .sort((a, b) => {
        const distA = Math.sqrt(Math.pow(mouse.x! - a.x, 2) + Math.pow(mouse.y! - a.y, 2));
        const distB = Math.sqrt(Math.pow(mouse.x! - b.x, 2) + Math.pow(mouse.y! - b.y, 2));
        return distA - distB;
      })
      .slice(0, 5);

    electricNodes.forEach((node) => {
      const dx = mouse.x! - node.x;
      const dy = mouse.y! - node.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const proximity = 1 - distance / config.electricDistance;

      // Draw lightning with multiple layers
      for (let layer = 0; layer < 3; layer++) {
        ctx.beginPath();
        ctx.moveTo(mouse.x!, mouse.y!);

        // Lightning segments with randomness
        const segments = 5;
        for (let i = 1; i < segments; i++) {
          const t = i / segments;
          const x = mouse.x! + (node.x - mouse.x!) * t + (Math.random() - 0.5) * 15 * (1 - t);
          const y = mouse.y! + (node.y - mouse.y!) * t + (Math.random() - 0.5) * 15 * (1 - t);
          ctx.lineTo(x, y);
        }
        ctx.lineTo(node.x, node.y);

        if (layer === 0) {
          ctx.strokeStyle = node.color;
          ctx.lineWidth = 4 * proximity;
          ctx.globalAlpha = 0.15 * proximity;
          ctx.shadowBlur = 20;
          ctx.shadowColor = node.color;
        } else if (layer === 1) {
          ctx.strokeStyle = node.color;
          ctx.lineWidth = 2 * proximity;
          ctx.globalAlpha = 0.5 * proximity;
          ctx.shadowBlur = 10;
          ctx.shadowColor = node.color;
        } else {
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 0.8 * proximity;
          ctx.globalAlpha = 0.8 * proximity;
          ctx.shadowBlur = 5;
          ctx.shadowColor = '#ffffff';
        }

        ctx.stroke();
      }
      ctx.shadowBlur = 0;
    });
  }, []);

  const drawConnections = useCallback((ctx: CanvasRenderingContext2D, particles: ParticleData[], mouse: { x: number | null; y: number | null }) => {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < config.connectionDistance) {
          let opacity = 1 - distance / config.connectionDistance;
          let isElectricConnection = false;

          if (mouse.x !== null && mouse.y !== null) {
            const distToMouse1 = Math.sqrt(Math.pow(mouse.x - particles[i].x, 2) + Math.pow(mouse.y - particles[i].y, 2));
            const distToMouse2 = Math.sqrt(Math.pow(mouse.x - particles[j].x, 2) + Math.pow(mouse.y - particles[j].y, 2));
            const minDistToMouse = Math.min(distToMouse1, distToMouse2);

            if (minDistToMouse < config.mouseDistance) {
              const mouseProximity = 1 - minDistToMouse / config.mouseDistance;
              opacity = Math.min(1, opacity + mouseProximity * 0.5);

              if (minDistToMouse < config.electricDistance) {
                isElectricConnection = true;
              }
            }
          }

          ctx.beginPath();

          if (isElectricConnection) {
            ctx.strokeStyle = particles[i].color;
            ctx.lineWidth = 1.5 + opacity * 1.5;
            ctx.globalAlpha = opacity * 0.8;
            ctx.shadowBlur = 10;
            ctx.shadowColor = particles[i].color;
          } else {
            ctx.strokeStyle = particles[i].color;
            ctx.lineWidth = 0.5 + opacity * 0.5;
            ctx.globalAlpha = opacity * 0.4;
          }

          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
          ctx.shadowBlur = 0;
        }
      }
    }
  }, []);

  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = dimensionsRef.current;
    const particles = particlesRef.current;
    const mouse = mouseRef.current;

    ctx.clearRect(0, 0, width, height);

    // Draw electric lightning from mouse
    drawElectricConnections(ctx, mouse, particles);

    // Update and draw particles
    for (let i = 0; i < particles.length; i++) {
      updateParticle(particles[i], mouse);
      drawParticle(ctx, particles[i]);
    }

    // Draw connections between particles
    drawConnections(ctx, particles, mouse);

    ctx.globalAlpha = 1;
    animationRef.current = requestAnimationFrame(animate);
  }, [drawElectricConnections, drawConnections, updateParticle, drawParticle]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const handleResize = () => {
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      dimensionsRef.current = { width: rect.width, height: rect.height };
      initParticles(rect.width, rect.height);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    const handleMouseLeave = () => {
      mouseRef.current = { x: null, y: null };
    };

    // Initial setup
    handleResize();

    // Start animation
    animate();

    // Event listeners
    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationRef.current);
    };
  }, [animate, initParticles]);

  return (
    <div ref={containerRef} className="absolute inset-0 z-0 overflow-hidden">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ background: 'transparent' }}
      />
    </div>
  );
};

export default NeuralBackground;
