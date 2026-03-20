import React, { useState, useRef, useEffect } from 'react'
import './App.css'

export default function App() {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const loopTimeoutRef = useRef(null)
  
  // State management
  const [trajectory, setTrajectory] = useState([])
  const [frame, setFrame] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('idle')
  const [statusFade, setStatusFade] = useState(1)
  const [error, setError] = useState(null)
  const [runHistory, setRunHistory] = useState([])
  const [totalRuns, setTotalRuns] = useState(0)

  // Canvas dimensions
  const CANVAS_WIDTH = 600
  const CANVAS_HEIGHT = 700
  const HORIZON_Y = 150
  const GROUND_Y = CANVAS_HEIGHT - 100
  
  // Easing function for smooth interpolation
  const easeInOutQuad = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t

  // Fetch new simulation
  const fetchSimulation = async () => {
    try {
      const response = await fetch('http://localhost:10000/simulate')
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (err) {
      console.error('❌ Fetch error:', err)
      setError(err.message)
      return null
    }
  }

  // Run continuous loop
  const runSimulationLoop = async (shouldContinue) => {
    if (!shouldContinue) return

    setStatusFade(0.5) // Fade out
    
    // Wait 500ms before fetching next
    await new Promise(resolve => {
      loopTimeoutRef.current = setTimeout(resolve, 500)
    })

    const data = await fetchSimulation()
    if (!data) {
      setIsRunning(false)
      return
    }

    setTrajectory(data.steps || [])
    setFrame(0)
    setStatusFade(1) // Fade in
    setStatus(data.status || 'running')
    
    // Record result
    const isSuccess = data.status === 'landed'
    setRunHistory(prev => [...prev.slice(-9), isSuccess])
    setTotalRuns(prev => prev + 1)
  }

  // START CONTINUOUS SIMULATION
  const startSimulation = async () => {
    console.log('🚀 Starting continuous simulation...')
    setIsLoading(true)
    setError(null)
    setFrame(0)
    setStatus('running')
    setStatusFade(1)

    const data = await fetchSimulation()
    if (!data) {
      setIsLoading(false)
      return
    }

    setTrajectory(data.steps || [])
    setStatus(data.status || 'running')
    setIsRunning(true)
    setIsLoading(false)

    // Record first run
    const isSuccess = data.status === 'landed'
    setRunHistory([isSuccess])
    setTotalRuns(1)
  }

  // STOP SIMULATION
  const stopSimulation = () => {
    console.log('⏹ Stopping continuous simulation')
    setIsRunning(false)
    if (loopTimeoutRef.current) {
      clearTimeout(loopTimeoutRef.current)
    }
  }

  // RESET
  const resetSimulation = () => {
    console.log('🔄 Resetting')
    setIsRunning(false)
    if (loopTimeoutRef.current) {
      clearTimeout(loopTimeoutRef.current)
    }
    setTrajectory([])
    setFrame(0)
    setStatus('idle')
    setStatusFade(1)
    setError(null)
    setRunHistory([])
    setTotalRuns(0)
  }

  // Calculate success rate
  const successCount = runHistory.filter(v => v === true).length
  const successRate = totalRuns > 0 ? Math.round((successCount / totalRuns) * 100) : 0

  // ANIMATION LOOP
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let particleList = []

    // Calculate max height for dynamic scaling
    const getMaxHeight = () => {
      if (trajectory.length === 0) return 100
      return Math.max(...trajectory.map(t => t.y), 50)
    }

    // Draw small sparkling stars in background
    const drawStars = () => {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.15)'
      for (let i = 0; i < 40; i++) {
        const x = (i * 73 + 37) % CANVAS_WIDTH
        const y = (i * 127 + 51) % (CANVAS_HEIGHT * 0.4)
        ctx.beginPath()
        ctx.arc(x, y, 0.8, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    // Draw atmospheric vignette
    const drawVignette = () => {
      const vignette = ctx.createRadialGradient(
        CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 0,
        CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, CANVAS_WIDTH * 0.7
      )
      vignette.addColorStop(0, 'rgba(0, 0, 0, 0)')
      vignette.addColorStop(1, 'rgba(0, 0, 0, 0.4)')
      ctx.fillStyle = vignette
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
    }

    // Particle class for exhaust effect
    class Particle {
      constructor(x, y) {
        this.x = x
        this.y = y
        this.vx = (Math.random() - 0.5) * 3
        this.vy = Math.random() * 2 + 1
        this.life = 1
        this.size = Math.random() * 3 + 2
      }

      update() {
        this.x += this.vx
        this.y += this.vy
        this.life -= 0.05
      }

      draw(ctx) {
        ctx.globalAlpha = this.life * 0.6
        ctx.fillStyle = '#ff6b35'
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fill()
        ctx.globalAlpha = 1
      }
    }

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = '#000a14'
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      // Draw background gradient
      const grad = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT)
      grad.addColorStop(0, '#0a1628')
      grad.addColorStop(0.5, '#0f2847')
      grad.addColorStop(1, '#000000')
      ctx.fillStyle = grad
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      // Draw stars
      drawStars()

      // Draw rocket and telemetry
      if (trajectory.length > 0) {
        const currentData = trajectory[Math.min(frame, trajectory.length - 1)]
        
        if (currentData) {
          // ============================================
          // AUTO SCALE CAMERA SYSTEM
          // ============================================
          const maxHeight = getMaxHeight()
          const topPadding = 60             // Space at top for HUD
          const bottomPadding = 100         // Space at bottom for platform
          const viewableHeight = CANVAS_HEIGHT - topPadding - bottomPadding
          
          // Normalize Y to [0, 1] range
          const normalizedY = currentData.y / maxHeight
          
          // Map to canvas with padding
          const rocketCanvasY = topPadding + (1 - normalizedY) * viewableHeight
          
          // Clamp to stay on screen (with margin)
          const rocketMargin = 40
          const clampedRocketY = Math.max(
            topPadding - rocketMargin,
            Math.min(rocketCanvasY, CANVAS_HEIGHT - bottomPadding + rocketMargin)
          )

          // ============================================
          // DRAW DYNAMIC HORIZON
          // ============================================
          const horizonNormalizedY = 50 / maxHeight
          const horizonY = topPadding + (1 - horizonNormalizedY) * viewableHeight
          
          ctx.strokeStyle = 'rgba(100, 150, 255, 0.2)'
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.moveTo(0, horizonY)
          ctx.lineTo(CANVAS_WIDTH, horizonY)
          ctx.stroke()

          // ============================================
          // DRAW GROUND / PLATFORM
          // ============================================
          const groundNormalizedY = 0 / maxHeight
          const groundY = topPadding + (1 - groundNormalizedY) * viewableHeight
          
          const platformWidth = 150
          const platformX = (CANVAS_WIDTH - platformWidth) / 2
          const platformY = Math.min(groundY - 10, CANVAS_HEIGHT - 30)

          ctx.shadowColor = 'rgba(100, 200, 255, 0.8)'
          ctx.shadowBlur = 25
          ctx.fillStyle = 'rgba(60, 120, 200, 0.6)'
          ctx.fillRect(platformX, platformY, platformWidth, 15)

          ctx.strokeStyle = 'rgba(150, 200, 255, 0.9)'
          ctx.lineWidth = 2
          ctx.strokeRect(platformX, platformY, platformWidth, 15)
          ctx.shadowColor = 'transparent'

          // Draw rocket
          const rocketX = CANVAS_WIDTH / 2
          const rocketHeight = 35
          const rocketWidth = 15

          let rocketColor = '#c0c0c0'
          if (status === 'landed') rocketColor = '#4ade80'
          else if (status === 'crashed') rocketColor = '#f87171'

          // Draw flame effect
          if (currentData.action === 1 && (status === 'running' || !status.includes('crash'))) {
            const flameHeight = Math.random() * 15 + 10
            const flameWidth = rocketWidth + 4

            // Gradient flame
            const flameGrad = ctx.createLinearGradient(
              rocketX, clampedRocketY + rocketHeight,
              rocketX, clampedRocketY + rocketHeight + flameHeight
            )
            flameGrad.addColorStop(0, 'rgba(255, 107, 53, 0.9)')
            flameGrad.addColorStop(0.5, 'rgba(255, 170, 0, 0.5)')
            flameGrad.addColorStop(1, 'rgba(255, 170, 0, 0)')

            ctx.fillStyle = flameGrad
            ctx.beginPath()
            ctx.moveTo(rocketX - flameWidth / 2, clampedRocketY + rocketHeight)
            ctx.lineTo(rocketX + flameWidth / 2, clampedRocketY + rocketHeight)
            ctx.lineTo(rocketX, clampedRocketY + rocketHeight + flameHeight)
            ctx.fill()

            // Add particles
            if (Math.random() > 0.6) {
              particleList.push(new Particle(rocketX, clampedRocketY + rocketHeight))
            }
          }

          // Draw rocket body
          ctx.shadowColor = rocketColor
          ctx.shadowBlur = 20
          ctx.fillStyle = rocketColor
          ctx.fillRect(rocketX - rocketWidth / 2, clampedRocketY, rocketWidth, rocketHeight)

          // Draw nose cone
          ctx.fillStyle = '#FFD700'
          ctx.beginPath()
          ctx.moveTo(rocketX - rocketWidth / 2, clampedRocketY)
          ctx.lineTo(rocketX, clampedRocketY - 10)
          ctx.lineTo(rocketX + rocketWidth / 2, clampedRocketY)
          ctx.fill()

          // Draw window
          ctx.fillStyle = '#87CEEB'
          ctx.beginPath()
          ctx.arc(rocketX, clampedRocketY + 8, 3, 0, Math.PI * 2)
          ctx.fill()

          ctx.shadowColor = 'transparent'

          // ============================================
          // DRAW LARGE HEIGHT INDICATOR (TOP CENTER)
          // ============================================
          ctx.fillStyle = 'rgba(59, 130, 246, 0.2)'
          ctx.strokeStyle = 'rgba(100, 150, 255, 0.5)'
          ctx.lineWidth = 2
          ctx.fillRect(CANVAS_WIDTH / 2 - 100, 10, 200, 50)
          ctx.strokeRect(CANVAS_WIDTH / 2 - 100, 10, 200, 50)
          
          ctx.fillStyle = '#60a5fa'
          ctx.font = 'bold 28px Arial'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(`${currentData.y.toFixed(1)}m`, CANVAS_WIDTH / 2, 35)
          
          ctx.fillStyle = 'rgba(100, 150, 255, 0.7)'
          ctx.font = 'bold 10px Arial'
          ctx.fillText('ALTITUDE', CANVAS_WIDTH / 2, 18)

          // ============================================
          // DRAW HUD AND ALTITUDE MARKER
          // ============================================
          ctx.fillStyle = `rgba(255, 255, 255, ${0.9 * statusFade})`
          ctx.font = 'bold 11px Arial'
          ctx.textAlign = 'left'
          ctx.textBaseline = 'top'

          const hudX = 20
          let hudY = 75
          
          ctx.fillText(`Velocity: ${Math.abs(currentData.vy).toFixed(2)}m/s`, hudX, hudY)
          hudY += 18
          ctx.fillText(`Fuel: ${currentData.fuel.toFixed(1)}%`, hudX, hudY)
          hudY += 18
          ctx.fillText(`Action: ${currentData.action === 1 ? 'THRUST' : 'IDLE'}`, hudX, hudY)

          // Draw altitude scale on right side (BRIGHT & BOLD)
          ctx.fillStyle = 'rgba(100, 180, 255, 0.8)'
          ctx.font = 'bold 11px Arial'
          ctx.textAlign = 'right'
          ctx.textBaseline = 'middle'
          
          const altitudeMarks = 6
          for (let i = 0; i <= altitudeMarks; i++) {
            const markAltitude = (maxHeight / altitudeMarks) * i
            const markNormalizedY = markAltitude / maxHeight
            const markY = topPadding + (1 - markNormalizedY) * viewableHeight
            
            if (markY >= topPadding && markY <= CANVAS_HEIGHT - bottomPadding) {
              // Tick line (brighter)
              ctx.strokeStyle = 'rgba(100, 180, 255, 0.6)'
              ctx.lineWidth = 2
              ctx.beginPath()
              ctx.moveTo(CANVAS_WIDTH - 10, markY)
              ctx.lineTo(CANVAS_WIDTH - 40, markY)
              ctx.stroke()
              
              // Altitude text (bright)
              ctx.fillStyle = 'rgba(150, 200, 255, 0.9)'
              ctx.fillText(`${markAltitude.toFixed(0)}m`, CANVAS_WIDTH - 50, markY)
            }
          }

          // Draw altitude bar on right edge
          ctx.strokeStyle = 'rgba(100, 150, 255, 0.4)'
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.moveTo(CANVAS_WIDTH - 37, topPadding)
          ctx.lineTo(CANVAS_WIDTH - 37, CANVAS_HEIGHT - bottomPadding)
          ctx.stroke()

          // ============================================
          // DRAW STATUS MESSAGE
          // ============================================
          if (status === 'landed' || status === 'crashed') {
            ctx.font = 'bold 28px Arial'
            ctx.textAlign = 'center'
            
            if (status === 'landed') {
              ctx.fillStyle = `rgba(74, 222, 128, ${statusFade * 0.9})`
              ctx.shadowColor = `rgba(74, 222, 128, ${statusFade * 0.5})`
              ctx.fillText('✅ LANDED!', CANVAS_WIDTH / 2, 60)
            } else {
              ctx.fillStyle = `rgba(248, 113, 113, ${statusFade * 0.9})`
              ctx.shadowColor = `rgba(248, 113, 113, ${statusFade * 0.5})`
              
            }
            ctx.shadowColor = 'transparent'
          }

          // Draw progress bar
          const progress = frame / trajectory.length
          const barY = CANVAS_HEIGHT - 30
          const barWidth = 200
          const barX = (CANVAS_WIDTH - barWidth) / 2

          ctx.fillStyle = 'rgba(100, 100, 100, 0.3)'
          ctx.fillRect(barX, barY, barWidth, 4)

          ctx.fillStyle = '#3b82f6'
          ctx.fillRect(barX, barY, barWidth * progress, 4)
        }
      } else {
        // No data - show message
        ctx.fillStyle = 'rgba(100, 150, 255, 0.7)'
        ctx.font = '16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('Click "START" to begin simulation', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)
      }

      // Update and draw particles
      particleList.forEach((p, idx) => {
        p.update()
        p.draw(ctx)
        if (p.life <= 0) {
          particleList.splice(idx, 1)
        }
      })

      // Draw vignette overlay
      drawVignette()

      // Handle frame advancement
      if (isRunning && trajectory.length > 0) {
        if (frame < trajectory.length - 1) {
          setFrame(prev => prev + 1)
        } else {
          // Episode ended - start new loop
          runSimulationLoop(isRunning)
        }
      }

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [frame, isRunning, trajectory, status, statusFade])

  // Get current data for stats
  const currentData = trajectory[Math.min(frame, trajectory.length - 1)]

  return (
    <div className="app-container">
      <div className="app-background"></div>

      <div className="app-wrapper">
        {/* LEFT PANEL - CONTROLS */}
        <div className="control-section">
          <div className="control-header">
            <h1>🚀 Rocket AI Simulator</h1>
            <p className="control-subtitle">PPO Autonomous Landing System</p>
          </div>
          
          <div className="button-group">
            <button 
              onClick={startSimulation}
              disabled={isLoading || isRunning}
              className="btn btn-start"
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  LOADING...
                </>
              ) : (
                <>
                  <span>▶</span>
                  START
                </>
              )}
            </button>

            <button 
              onClick={stopSimulation}
              disabled={!isRunning}
              className="btn btn-stop"
            >
              <span>⏹</span>
              STOP
            </button>

            <button 
              onClick={resetSimulation}
              className="btn btn-reset"
            >
              <span>🔄</span>
              RESET
            </button>
          </div>

          {error && <div className="error-box">{error}</div>}

          {/* Performance stats */}
          <div className="divider"></div>
          <div className="performance-stats">
            <div className="perf-item">
              <span className="perf-label">Total Runs</span>
              <span className="perf-value">{totalRuns}</span>
            </div>
            <div className="perf-item">
              <span className="perf-label">Success Rate</span>
              <span className="perf-value">{successRate}%</span>
            </div>
          </div>
        </div>

        {/* CENTER - CANVAS */}
        <div className="canvas-section">
          <canvas
            ref={canvasRef}
            width={CANVAS_WIDTH}
            height={CANVAS_HEIGHT}
            className="simulation-canvas"
          />
        </div>

        {/* RIGHT PANEL - STATS */}
        <div className="stats-section">
          <div className="stats-header">
            <h2>📊 TELEMETRY</h2>
          </div>

          <div className="stat-box">
            <div className="stat-label">Height</div>
            <div className="stat-value animate-value">{currentData?.y?.toFixed(1) || '—'} m</div>
          </div>

          <div className="stat-box">
            <div className="stat-label">Velocity</div>
            <div className="stat-value animate-value">{Math.abs(currentData?.vy || 0).toFixed(2)} m/s</div>
          </div>

          <div className="stat-box">
            <div className="stat-label">Fuel</div>
            <div className="stat-value animate-value">{currentData?.fuel?.toFixed(1) || '—'}%</div>
          </div>

          <div className={`stat-box status-box status-${status}`} style={{ opacity: statusFade }}>
            <div className="stat-label">Status</div>
            <div className="stat-value">
              {status === 'landed' && '✅ LANDED'}
              {status === 'crashed' && '💥 CRASHED'}
              {status === 'running' && '🚀 FLYING'}
              {!['landed', 'crashed', 'running'].includes(status) && '⏸ IDLE'}
            </div>
          </div>

          {trajectory.length > 0 && (
            <>
              <div className="divider"></div>
              <div className="stat-box">
                <div className="stat-label">Total Steps</div>
                <div className="stat-value">{trajectory.length}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Frame</div>
                <div className="stat-value">{frame + 1}/{trajectory.length}</div>
              </div>
            </>
          )}

          {totalRuns > 0 && (
            <>
              <div className="divider"></div>
              <div className="stat-box">
                <div className="stat-label">Success Rate</div>
                <div className="stat-value">{successRate}%</div>
              </div>
              <div className="success-history">
                {runHistory.map((success, idx) => (
                  <div 
                    key={idx} 
                    className={`history-dot ${success ? 'success' : 'failure'}`}
                    title={success ? 'Landed' : 'Crashed'}
                  ></div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
