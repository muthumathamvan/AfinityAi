    /**
     * Particle Animation System
     * Creates floating neural network-style particles in the background
     */

    class ParticleSystem {
        constructor(canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.particles = [];
            this.particleCount = 80;
            this.connectionDistance = 150;
            this.mouse = { x: null, y: null };
            
            this.init();
            this.setupEventListeners();
            this.animate();
        }
        
        init() {
            this.resize();
            this.createParticles();
        }
        
        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        
        createParticles() {
            this.particles = [];
            for (let i = 0; i < this.particleCount; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    radius: Math.random() * 2 + 1,
                    opacity: Math.random() * 0.5 + 0.3
                });
            }
        }
        
        setupEventListeners() {
            window.addEventListener('resize', () => {
                this.resize();
                this.createParticles();
            });
            
            window.addEventListener('mousemove', (e) => {
                this.mouse.x = e.clientX;
                this.mouse.y = e.clientY;
            });
            
            window.addEventListener('mouseleave', () => {
                this.mouse.x = null;
                this.mouse.y = null;
            });
        }
        
        drawParticle(particle) {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            
            // Create gradient for particles
            const gradient = this.ctx.createRadialGradient(
                particle.x, particle.y, 0,
                particle.x, particle.y, particle.radius * 2
            );
            gradient.addColorStop(0, `rgba(139, 92, 246, ${particle.opacity})`);
            gradient.addColorStop(0.5, `rgba(99, 102, 241, ${particle.opacity * 0.7})`);
            gradient.addColorStop(1, `rgba(6, 182, 212, 0)`);
            
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
        }
        
        drawConnection(p1, p2, distance) {
            const opacity = (1 - distance / this.connectionDistance) * 0.3;
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`;
            this.ctx.lineWidth = 0.5;
            this.ctx.stroke();
        }
        
        updateParticle(particle) {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Mouse interaction
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = this.mouse.x - particle.x;
                const dy = this.mouse.y - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    const force = (100 - distance) / 100;
                    particle.vx -= (dx / distance) * force * 0.1;
                    particle.vy -= (dy / distance) * force * 0.1;
                }
            }
            
            // Boundary check with wrapping
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Add slight random drift
            particle.vx += (Math.random() - 0.5) * 0.02;
            particle.vy += (Math.random() - 0.5) * 0.02;
            
            // Limit velocity
            const maxSpeed = 1;
            const speed = Math.sqrt(particle.vx * particle.vx + particle.vy * particle.vy);
            if (speed > maxSpeed) {
                particle.vx = (particle.vx / speed) * maxSpeed;
                particle.vy = (particle.vy / speed) * maxSpeed;
            }
            
            // Pulsing opacity
            particle.opacity = 0.3 + Math.sin(Date.now() * 0.001 + particle.x) * 0.2;
        }
        
        animate() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Update and draw particles
            this.particles.forEach(particle => {
                this.updateParticle(particle);
                this.drawParticle(particle);
            });
            
            // Draw connections
            for (let i = 0; i < this.particles.length; i++) {
                for (let j = i + 1; j < this.particles.length; j++) {
                    const dx = this.particles[i].x - this.particles[j].x;
                    const dy = this.particles[i].y - this.particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < this.connectionDistance) {
                        this.drawConnection(this.particles[i], this.particles[j], distance);
                    }
                }
            }
            
            requestAnimationFrame(() => this.animate());
        }
    }

    // Initialize particle system when DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('particleCanvas');
        if (canvas) {
            new ParticleSystem(canvas);
        }
    });
