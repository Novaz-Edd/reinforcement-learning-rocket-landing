import React, { useState, useRef, useEffect } from 'react'
import './App.css'

export default function App() {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  
  // State management
  const [trajectory, setTrajectory] = useState([])
  const [frame, setFrame] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  // Canvas dimensions
  const CANVAS_WIDTH = 600
  const CANVAS_HEIGHT = 700
  const HORIZON_Y = 150
  const GROUND_Y = CANVAS_HEIGHT - 100

  // START SIMULATION
  const startSimulation = async () => {
    console.log('🚀 [startSimulation] Button clicked - fetching from backend...')
    setIsLoading(true)
    setError(null)
    setFrame(0)

    try {
      console.log('🚀 Fetching: http://localhost:10000/simulate')
      const response = await fetch('http://localhost:10000/simulate')
      console.log(`🚀 Response status: ${response.status}`)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('🚀 Data received:', {
        status: data.status,
        steps: data.total_steps,
        reward: data.total_reward,
        trajectory_length: data.steps?.length
      })

      setTrajectory(data.steps || [])
      setStatus(data.status || 'running')
      setIsRunning(true)
      setIsLoading(false)
    } catch (err) {
      console.error('❌ Fetch error:', err)
      setError(err.message)
      setIsLoading(false)
    }
  }

  // STOP SIMULATION
  const stopSimulation = () => {
    console.log('⏹ [stopSimulation] Stopping animation')
    setIsRunning(false)
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
  }

  // RESET
  const resetSimulation = () => {
    console.log('🔄 [resetSimulation] Resetting')
    setIsRunning(false)
    setTrajectory([])
    setFrame(0)
    setStatus('idle')
    setError(null)
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
  }

  // ANIMATION LOOP
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')

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

      // Draw horizon
      ctx.strokeStyle = 'rgba(100, 150, 255, 0.2)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(0, HORIZON_Y)
      ctx.lineTo(CANVAS_WIDTH, HORIZON_Y)
      ctx.stroke()

      // Draw platform
      const platformWidth = 150
      const platformX = (CANVAS_WIDTH - platformWidth) / 2
      const platformY = GROUND_Y - 10

      ctx.shadowColor = 'rgba(100, 200, 255, 0.8)'
      ctx.shadowBlur = 15
      ctx.fillStyle = 'rgba(60, 120, 200, 0.6)'
      ctx.fillRect(platformX, platformY, platformWidth, 15)

      ctx.strokeStyle = 'rgba(150, 200, 255, 0.9)'
      ctx.lineWidth = 2
      ctx.strokeRect(platformX, platformY, platformWidth, 15)
      ctx.shadowColor = 'transparent'

      // Draw rocket and telemetry
      if (trajectory.length > 0) {
        const currentData = trajectory[Math.min(frame, trajectory.length - 1)]
        
        if (currentData) {
          // Convert world Y (0-100) to canvas Y
          const rocketCanvasY = HORIZON_Y + (1 - currentData.y / 100) * (GROUND_Y - HORIZON_Y)

          // Draw rocket
          const rocketX = CANVAS_WIDTH / 2
          const rocketHeight = 35
          const rocketWidth = 15

          let rocketColor = '#c0c0c0'
          if (status === 'landed') rocketColor = '#4ade80'
          else if (status === 'crashed') rocketColor = '#f87171'

          ctx.shadowColor = rocketColor
          ctx.shadowBlur = 15
          ctx.fillStyle = rocketColor
          ctx.fillRect(rocketX - rocketWidth / 2, rocketCanvasY, rocketWidth, rocketHeight)

          // Draw nose cone
          ctx.fillStyle = '#FFD700'
          ctx.beginPath()
          ctx.moveTo(rocketX - rocketWidth / 2, rocketCanvasY)
          ctx.lineTo(rocketX, rocketCanvasY - 10)
          ctx.lineTo(rocketX + rocketWidth / 2, rocketCanvasY)
          ctx.fill()

          // Draw window
          ctx.fillStyle = '#87CEEB'
          ctx.beginPath()
          ctx.arc(rocketX, rocketCanvasY + 8, 3, 0, Math.PI * 2)
          ctx.fill()

          ctx.shadowColor = 'transparent'

          // Draw HUD
          ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
          ctx.font = 'bold 12px Arial'
          ctx.textAlign = 'left'

          const hudX = 20
          let hudY = 30
          
          ctx.fillText(`Height: ${currentData.y.toFixed(2)}m`, hudX, hudY)
          hudY += 20
          ctx.fillText(`Velocity: ${Math.abs(currentData.vy).toFixed(2)}m/s`, hudX, hudY)
          hudY += 20
          ctx.fillText(`Fuel: ${currentData.fuel.toFixed(1)}%`, hudX, hudY)
          hudY += 20
          ctx.fillText(`Action: ${currentData.action === 1 ? 'THRUST' : 'IDLE'}`, hudX, hudY)

          // Draw status message
          if (status === 'landed' || status === 'crashed') {
            ctx.font = 'bold 28px Arial'
            ctx.textAlign = 'center'
            
            if (status === 'landed') {
              ctx.fillStyle = 'rgba(74, 222, 128, 0.9)'
              ctx.shadowColor = '#4ade80'
              ctx.fillText('✅ LANDED!', CANVAS_WIDTH / 2, 60)
            } else {
              ctx.fillStyle = 'rgba(248, 113, 113, 0.9)'
              ctx.shadowColor = '#f87171'
              ctx.fillText('💥 CRASHED', CANVAS_WIDTH / 2, 60)
            }
            ctx.shadowColor = 'transparent'
          }

          // Draw progress
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

      // Continue animation if running
      if (isRunning && trajectory.length > 0 && frame < trajectory.length - 1) {
        setFrame(prev => prev + 1)
      }

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [frame, isRunning, trajectory, status])

  // Get current data for stats
  const currentData = trajectory[Math.min(frame, trajectory.length - 1)]

  return (
    <div className="app-container">
      <div className="app-background"></div>

      <div className="app-wrapper">
        {/* LEFT PANEL - BUTTONS */}
        <div className="control-section">
          <h2>🚀 ROCKET SIMULATOR</h2>
          
          <button 
            onClick={startSimulation}
            disabled={isLoading || isRunning}
            className="btn btn-start"
          >
            {isLoading ? '⏳ LOADING...' : '▶ START'}
          </button>

          <button 
            onClick={stopSimulation}
            disabled={!isRunning}
            className="btn btn-stop"
          >
            ⏹ STOP
          </button>

          <button 
            onClick={resetSimulation}
            className="btn btn-reset"
          >
            🔄 RESET
          </button>

          {error && <div className="error-box">{error}</div>}
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
          <h2>📊 TELEMETRY</h2>

          <div className="stat-box">
            <div className="stat-label">Height</div>
            <div className="stat-value">{currentData?.y?.toFixed(1) || '—'} m</div>
          </div>

          <div className="stat-box">
            <div className="stat-label">Velocity</div>
            <div className="stat-value">{Math.abs(currentData?.vy || 0).toFixed(2)} m/s</div>
          </div>

          <div className="stat-box">
            <div className="stat-label">Fuel</div>
            <div className="stat-value">{currentData?.fuel?.toFixed(1) || '—'}%</div>
          </div>

          <div className={`stat-box status-box status-${status}`}>
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
        </div>
      </div>
    </div>
  )
}
