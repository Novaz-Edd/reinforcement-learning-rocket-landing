import React, { useEffect, useRef, useState } from 'react'
import './SimulationCanvas.css'

const SimulationCanvas = React.forwardRef(({ stepData, status, simData, progress }, ref) => {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const [particles, setParticles] = useState([])
  const lastYRef = useRef(null)

  // Canvas dimensions
  const CANVAS_WIDTH = 600
  const CANVAS_HEIGHT = 700
  const HORIZON_Y = 150
  const GROUND_Y = CANVAS_HEIGHT - 100

  // Draw functions
  const drawBackground = (ctx) => {
    // Gradient background (deep blue to black)
    const gradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT)
    gradient.addColorStop(0, '#0a1628')
    gradient.addColorStop(0.5, '#0f2847')
    gradient.addColorStop(1, '#000000')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    // Horizon
    ctx.strokeStyle = 'rgba(100, 150, 255, 0.2)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(0, HORIZON_Y)
    ctx.lineTo(CANVAS_WIDTH, HORIZON_Y)
    ctx.stroke()

    // Water below
    const waterGradient = ctx.createLinearGradient(0, HORIZON_Y, 0, CANVAS_HEIGHT)
    waterGradient.addColorStop(0, 'rgba(20, 60, 150, 0.3)')
    waterGradient.addColorStop(1, 'rgba(10, 30, 80, 0.5)')
    ctx.fillStyle = waterGradient
    ctx.fillRect(0, HORIZON_Y, CANVAS_WIDTH, CANVAS_HEIGHT - HORIZON_Y)
  }

  const drawPlatform = (ctx) => {
    const platformWidth = 150
    const platformX = (CANVAS_WIDTH - platformWidth) / 2
    const platformY = GROUND_Y - 10

    // Platform glow
    ctx.shadowColor = 'rgba(100, 200, 255, 0.8)'
    ctx.shadowBlur = 15
    ctx.fillStyle = 'rgba(60, 120, 200, 0.6)'
    ctx.fillRect(platformX, platformY, platformWidth, 15)

    // Platform border
    ctx.strokeStyle = 'rgba(150, 200, 255, 0.9)'
    ctx.lineWidth = 2
    ctx.strokeRect(platformX, platformY, platformWidth, 15)
    ctx.shadowColor = 'transparent'
  }

  const drawRocket = (ctx, y, rocketStatus) => {
    const rocketX = CANVAS_WIDTH / 2
    const rocketHeight = 35
    const rocketWidth = 15

    // Determine color based on status
    let rocketColor = '#c0c0c0' // silver
    if (rocketStatus === 'landed') {
      rocketColor = '#4ade80' // green
    } else if (rocketStatus === 'crashed') {
      rocketColor = '#f87171' // red
    }

    // Rocket glow effect
    ctx.shadowColor = rocketColor
    ctx.shadowBlur = rocketStatus ? 20 : 10
    ctx.shadowOffsetX = 0
    ctx.shadowOffsetY = 0

    // Body
    ctx.fillStyle = rocketColor
    ctx.fillRect(rocketX - rocketWidth / 2, y - rocketHeight / 2, rocketWidth, rocketHeight)

    // Nose cone (triangle)
    ctx.fillStyle = '#ffd700' // gold
    ctx.beginPath()
    ctx.moveTo(rocketX, y - rocketHeight / 2 - 8)
    ctx.lineTo(rocketX - rocketWidth / 2, y - rocketHeight / 2)
    ctx.lineTo(rocketX + rocketWidth / 2, y - rocketHeight / 2)
    ctx.closePath()
    ctx.fill()

    // Window
    ctx.fillStyle = '#66d9ff'
    ctx.beginPath()
    ctx.arc(rocketX, y - 5, 2.5, 0, Math.PI * 2)
    ctx.fill()

    // Landing legs
    ctx.strokeStyle = rocketColor
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.moveTo(rocketX - 6, y + rocketHeight / 2)
    ctx.lineTo(rocketX - 6, y + rocketHeight / 2 + 8)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(rocketX + 6, y + rocketHeight / 2)
    ctx.lineTo(rocketX + 6, y + rocketHeight / 2 + 8)
    ctx.stroke()

    ctx.shadowColor = 'transparent'
  }

  const drawFlame = (ctx, y, action, intensity) => {
    if (action !== 1) return

    const rocketX = CANVAS_WIDTH / 2
    const flameMaxWidth = 12
    const flameMaxHeight = 25
    const flameWidth = flameMaxWidth * intensity
    const flameHeight = flameMaxHeight * intensity

    // Outer flame (orange-red)
    const flameColor = `rgba(255, ${150 - intensity * 50}, 0, ${0.8 * intensity})`
    ctx.fillStyle = flameColor
    ctx.beginPath()
    ctx.moveTo(rocketX, y + 20)
    ctx.lineTo(rocketX - flameWidth, y + 20 + flameHeight)
    ctx.lineTo(rocketX + flameWidth, y + 20 + flameHeight)
    ctx.closePath()
    ctx.fill()

    // Inner flame (yellow, brighter)
    const innerColor = `rgba(255, 255, 100, ${0.6 * intensity})`
    ctx.fillStyle = innerColor
    ctx.beginPath()
    ctx.moveTo(rocketX, y + 20 + flameHeight * 0.2)
    ctx.lineTo(rocketX - flameWidth * 0.6, y + 20 + flameHeight * 0.8)
    ctx.lineTo(rocketX + flameWidth * 0.6, y + 20 + flameHeight * 0.8)
    ctx.closePath()
    ctx.fill()
  }

  const drawParticles = (ctx) => {
    particles.forEach((particle) => {
      const alpha = particle.life / particle.maxLife
      ctx.globalAlpha = alpha * 0.7
      ctx.fillStyle = particle.color
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fill()
    })
    ctx.globalAlpha = 1.0
  }

  const drawStatus = (ctx) => {
    if (!stepData) return

    let statusText = ''
    let statusColor = ''

    if (status === 'landed') {
      statusText = '✅ SUCCESSFUL LANDING'
      statusColor = 'rgba(74, 222, 128, 0.9)'
    } else if (status === 'crashed') {
      statusText = '💥 CRASH'
      statusColor = 'rgba(248, 113, 113, 0.9)'
    }

    if (statusText) {
      ctx.font = 'bold 28px "Inter", sans-serif'
      ctx.textAlign = 'center'
      ctx.shadowColor = statusColor
      ctx.shadowBlur = 20
      ctx.fillStyle = statusColor
      ctx.fillText(statusText, CANVAS_WIDTH / 2, 60)
      ctx.shadowColor = 'transparent'
    }
  }

  const drawProgressBar = (ctx) => {
    const barY = CANVAS_HEIGHT - 30
    const barWidth = 200
    const barX = (CANVAS_WIDTH - barWidth) / 2
    const barHeight = 4

    // Background
    ctx.fillStyle = 'rgba(100, 100, 100, 0.3)'
    ctx.fillRect(barX, barY, barWidth, barHeight)

    // Progress
    const progressWidth = barWidth * progress
    const progressGradient = ctx.createLinearGradient(barX, barY, barX + progressWidth, barY)
    progressGradient.addColorStop(0, '#3b82f6')
    progressGradient.addColorStop(1, '#8b5cf6')
    ctx.fillStyle = progressGradient
    ctx.fillRect(barX, barY, progressWidth, barHeight)
  }

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      console.warn("🎬 [Canvas] Canvas element not found!")
      return
    }

    console.log("🎬 [Canvas] Animation loop started, stepData:", stepData)

    const ctx = canvas.getContext('2d')

    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      // Draw elements
      drawBackground(ctx)
      drawPlatform(ctx)

      if (stepData) {
        // Convert world Y (0-100) to canvas Y
        const rocketCanvasY = HORIZON_Y + (1 - stepData.y / 100) * (GROUND_Y - HORIZON_Y)

        // Emit particles if thrust
        if (stepData.action === 1) {
          for (let i = 0; i < 3; i++) {
            const newParticle = {
              x: CANVAS_WIDTH / 2 + (Math.random() - 0.5) * 20,
              y: rocketCanvasY + 20,
              vx: (Math.random() - 0.5) * 40,
              vy: 30 + Math.random() * 20,
              life: 0.5,
              maxLife: 0.5,
              size: 3 + Math.random() * 2,
              color: `hsl(${10 + Math.random() * 30}, 100%, 50%)`
            }
            setParticles(prev => [...prev.slice(-50), newParticle])
          }
        }

        // Update particles
        setParticles(prev =>
          prev
            .map(p => ({
              ...p,
              x: p.x + p.vx * (1 / 60),
              y: p.y + p.vy * (1 / 60),
              vy: p.vy + 200 * (1 / 60), // gravity
              life: p.life - 1 / 60
            }))
            .filter(p => p.life > 0)
        )

        drawParticles(ctx)
        drawFlame(ctx, rocketCanvasY, stepData.action, stepData.action ? 0.8 : 0)
        drawRocket(ctx, rocketCanvasY, status)
      } else {
        // Draw "waiting" message  
        ctx.font = '16px Arial'
        ctx.fillStyle = 'rgba(100, 150, 255, 0.7)'
        ctx.textAlign = 'center'
        ctx.fillText('Click "Start Simulation" to begin', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)
      }

      drawProgressBar(ctx)
      drawStatus(ctx)

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [stepData, status, progress, particles])

  return (
    <canvas
      ref={canvasRef}
      width={CANVAS_WIDTH}
      height={CANVAS_HEIGHT}
      className="simulation-canvas"
    />
  )
})

SimulationCanvas.displayName = 'SimulationCanvas'

export default SimulationCanvas
