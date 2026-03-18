import React from 'react'
import './ControlPanel.css'

export default function ControlPanel({
  onStart,
  onStop,
  onReset,
  isRunning,
  stepMode,
  onStepModeChange,
  onNextStep,
  canStep
}) {
  return (
    <div className="control-panel">
      <div className="panel-header">
        <h2>CONTROLS</h2>
        <div className="header-accent"></div>
      </div>

      <div className="panel-content">
        {/* Main Buttons - LARGE AND VISIBLE */}
        <div className="button-group">
          <button
            className={`btn btn-primary ${isRunning ? 'pulse' : ''}`}
            onClick={onStart}
            disabled={isRunning && !stepMode}
            style={{ fontSize: '16px', padding: '16px 20px' }}
          >
            🚀 START
          </button>

          <button
            className="btn btn-danger"
            onClick={onStop}
            disabled={!isRunning && !stepMode}
            style={{ fontSize: '16px', padding: '16px 20px' }}
          >
            ⏹ STOP
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={onReset}
            style={{ fontSize: '16px', padding: '16px 20px' }}
          >
            🔄 RESET
          </button>
        </div>

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={stepMode}
              onChange={(e) => onStepModeChange(e.target.checked)}
              disabled={isRunning}
            />
            <span className="toggle-text">Step Mode</span>
          </label>
          <span className="mode-description">
            {stepMode ? 'Manual stepping' : 'Auto simulation'}
          </span>
        </div>

        {/* Next Step Button */}
        {stepMode && (
          <button
            className="btn btn-step"
            onClick={onNextStep}
            disabled={!canStep}
          >
            ⬇ Next Step
          </button>
        )}

        {/* Info Box */}
        <div className="info-box">
          <h3>How to Use</h3>
          <ul>
            <li>Click <strong>START</strong> to run simulation</li>
            <li>Watch live telemetry on the right</li>
            <li>Click <strong>STOP</strong> to pause</li>
            <li>Click <strong>RESET</strong> to start over</li>
          </ul>
        </div>

        {/* Model Info */}
        <div className="model-info">
          <p className="info-label">Model</p>
          <p className="info-value">PPO (ep2400)</p>
          <p className="info-label">Policy</p>
          <p className="info-value">Deterministic</p>
        </div>
      </div>
    </div>
  )
}
