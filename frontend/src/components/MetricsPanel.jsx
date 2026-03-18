import React from 'react'
import './MetricsPanel.css'

export default function MetricsPanel({ stepData, status, simData, step }) {
  const getStatusColor = () => {
    if (status === 'landed') return '#4ade80'
    if (status === 'crashed') return '#f87171'
    if (status === 'running') return '#fbbf24'
    return '#94a3b8'
  }

  const getStatusText = () => {
    switch (status) {
      case 'landed':
        return 'LANDED'
      case 'crashed':
        return 'CRASHED'
      case 'timeout':
        return 'TIMEOUT'
      case 'running':
        return 'FLYING'
      default:
        return 'IDLE'
    }
  }

  const formatValue = (value, decimals = 2) => {
    if (value === null || value === undefined) return '--'
    return typeof value === 'number' ? value.toFixed(decimals) : value
  }

  return (
    <div className="metrics-panel">
      <div className="panel-header">
        <h2>Telemetry</h2>
        <div className="header-accent"></div>
      </div>

      <div className="panel-content">
        {/* Status Indicator */}
        <div className="status-container">
          <div className="status-indicator" style={{ backgroundColor: getStatusColor() }}></div>
          <div className="status-text">{getStatusText()}</div>
        </div>

        {/* Metrics Grid */}
        <div className="metrics-grid">
          {/* Height Metric */}
          <div className="metric-card">
            <div className="metric-label">Height</div>
            <div className="metric-value">
              {formatValue(stepData?.y)} <span className="unit">m</span>
            </div>
            <div className="metric-bar">
              <div
                className="metric-bar-fill"
                style={{
                  width: stepData ? `${(stepData.y / 100) * 100}%` : '0%',
                  backgroundColor: '#3b82f6'
                }}
              ></div>
            </div>
          </div>

          {/* Velocity Metric */}
          <div className="metric-card">
            <div className="metric-label">Velocity</div>
            <div className="metric-value">
              {formatValue(stepData?.vy, 2)} <span className="unit">m/s</span>
            </div>
            <div className="metric-bar">
              <div
                className="metric-bar-fill"
                style={{
                  width: stepData ? `${Math.min(Math.abs(stepData.vy) / 20 * 100, 100)}%` : '0%',
                  backgroundColor: Math.abs(stepData?.vy || 0) > 5 ? '#f87171' : '#8b5cf6'
                }}
              ></div>
            </div>
          </div>

          {/* Fuel Metric */}
          <div className="metric-card">
            <div className="metric-label">Fuel</div>
            <div className="metric-value">
              {formatValue(stepData?.fuel)} <span className="unit">%</span>
            </div>
            <div className="metric-bar">
              <div
                className="metric-bar-fill"
                style={{
                  width: stepData ? `${stepData.fuel}%` : '0%',
                  backgroundColor: stepData?.fuel < 20 ? '#f97316' : '#10b981'
                }}
              ></div>
            </div>
          </div>

          {/* Action Metric */}
          <div className="metric-card">
            <div className="metric-label">Action</div>
            <div className="metric-value action">
              {stepData?.action === 1 ? (
                <>
                  <span className="flame">🔥</span> THRUST
                </>
              ) : (
                <>
                  <span className="idle">◯</span> IDLE
                </>
              )}
            </div>
          </div>
        </div>

        {/* Episode Stats */}
        {simData && (
          <div className="stats-box">
            <h3>Episode Results</h3>
            <div className="stats-row">
              <span className="stats-label">Total Steps:</span>
              <span className="stats-value">{simData.total_steps}</span>
            </div>
            <div className="stats-row">
              <span className="stats-label">Total Reward:</span>
              <span className="stats-value">
                {formatValue(simData.total_reward, 1)}
              </span>
            </div>
            <div className="stats-row">
              <span className="stats-label">Landing Velocity:</span>
              <span className="stats-value">
                {formatValue(simData.final_velocity, 2)} m/s
              </span>
            </div>
            {simData.status === 'landed' && (
              <div className="success-message">
                ✅ Safe landing achieved!
              </div>
            )}
            {simData.status === 'crashed' && (
              <div className="crash-message">
                💥 Collision detected
              </div>
            )}
          </div>
        )}

        {/* Current Step Display */}
        <div className="step-counter">
          <span>Step: {step}</span>
        </div>
      </div>
    </div>
  )
}
