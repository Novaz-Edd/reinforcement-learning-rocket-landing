# AI Rocket Landing Simulator - Setup & Usage Guide

## Project Overview

A production-ready web application featuring:
- **FastAPI Backend**: RESTful API for simulating trained PPO rocket landing agent
- **React Frontend**: Modern UI with Canvas-based visualization and glassmorphism design
- **Real-time Simulation**: Step-by-step or full-episode execution modes
- **Professional Dashboard**: SpaceX/NASA-inspired interface with live telemetry

---

## Current Status

### ✓ Completed Components

**Backend (`backend/`)**
- `main.py` - FastAPI server with 6 endpoints (370 lines)
  - `/health` - Server health check
  - `/reset` - Initialize new episode
  - `/step` - Execute single timestep
  - `/simulate` - Run complete episode
  - `/stats` - Get session statistics
  - Swagger UI at `/docs`

**Frontend (`frontend/`)**
- `src/App.jsx` - Main React component with state management
- `src/components/SimulationCanvas.jsx` - Canvas animation (60 FPS target)
- `src/components/ControlPanel.jsx` - User controls & mode toggle
- `src/components/MetricsPanel.jsx` - Real-time telemetry display
- `src/App.css` - Glassmorphism theme & responsive layout
- `src/components/*.css` - Component-specific styling
- `vite.config.js` - Vite bundler configuration
- `package.json` - npm dependencies installed

**Configuration**
- Python venv (3.11.1) with dependencies: torch, fastapi, uvicorn, pydantic, requests
- npm packages: react, react-dom, vite

---

## Running the Application

### Prerequisites
- Python 3.11+ with venv configured
- Node.js 14+ with npm
- Both servers will run locally on `localhost`

### Step 1: Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Start Uvicorn server (runs on port 10000)
python -m uvicorn main:app --host 0.0.0.0 --port 10000
```

Expected output:
```
Model loaded: ...\models\ppo_ep2400.pt
INFO:     Started server process [...]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

**API endpoints available at:**
- Health check: `http://localhost:10000/health`
- API docs: `http://localhost:10000/docs` (Swagger UI)

### Step 2: Start Frontend Development Server

```bash
# In new terminal, navigate to frontend directory
cd frontend

# Start Vite dev server (runs on port 5173)
npm run dev
```

Expected output:
```
VITE v4.x.x  ready in xxx ms

  Local:   http://localhost:5173/
  Network: http://192.168.x.x:5173/
```

### Step 3: Open Application

Visit `http://localhost:5173/` in your browser.

---

## Using the Application

### Dashboard Layout

**Left Panel - Controls**
- **Start Simulation**: Run full episode (auto-play)
- **Step Mode**: Toggle manual/auto execution
- **Next Step**: Advance one timestep (in step mode)
- **Reset**: Clear and prepare for new simulation
- Model info display

**Center - Canvas Visualization**
- Real-time rocket animation
- Particle effects (flames, exhaust)
- Ground/platform rendering
- Status messages
- Progress indicator

**Right Panel - Telemetry**
- **Status Indicator**: Green/Red/Yellow (flying/landed/crashed)
- **Height**: Current altitude (0-100m)
- **Velocity**: Descent speed (m/s)
- **Fuel**: Remaining fuel percentage
- **Action**: Current control (IDLE/THRUST)
- **Episode Results**: Final stats on completion

### Simulation Modes

#### Auto-Run Mode (Default)
1. Click "Start Simulation"
2. AI agent automatically controls the rocket
3. Watch complete descent to landing/crash
4. Dashboard shows real-time metrics

#### Step-by-Step Mode (Manual Control)
1. Enable "Step Mode" toggle
2. Click "Start" to initialize
3. Click "Next Step" to advance frame-by-frame
4. Useful for detailed observation of agent decisions

---

## API Endpoints

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "environment_ready": true
}
```

### POST `/reset`
Initialize new episode.

**Response:**
```json
{
  "status": "success",
  "message": "Environment reset. Ready for simulation."
}
```

### GET `/step`
Execute single timestep.

**Response:**
```json
{
  "done": false,
  "step": {
    "y": 51.6,
    "vy": -6.7,
    "fuel": 99.0,
    "action": 1,
    "done": false,
    "landed": false,
    "crashed": false,
    "reward": 0.034
  },
  "episode_reward": 0.034
}
```

### GET `/simulate`
Run complete episode.

**Response:**
```json
{
  "steps": [
    {"y": 100.0, "vy": -1.0, "fuel": 100.0, "action": 0, ...},
    ...
  ],
  "total_reward": 145.3,
  "status": "landed",
  "final_velocity": 0.5,
  "total_steps": 127
}
```

### GET `/stats`
Session statistics.

**Response:**
```json
{
  "last_episode_reward": 145.3,
  "episodes_run": 3
}
```

---

## Frontend Architecture

### Component Hierarchy
```
App
├── SimulationCanvas (Canvas animation & rendering)
├── ControlPanel (User controls & info)
└── MetricsPanel (Telemetry display)
```

### State Management
- React hooks (useState, useEffect, useRef)
- API polling (50ms interval in step mode)
- Real-time data binding to canvas

### Canvas Rendering
- 60 FPS requestAnimationFrame loop
- Particle system (gravity, lifetime)
- World-to-screen coordinate conversion
- Status-based color coding

### Design System
- **Theme**: Dark space with gradient background
- **Panels**: Glassmorphism (rgba + backdrop blur)
- **Colors**: Blue primary, Purple secondary, Green success, Red danger
- **Responsive**: Adapts to desktop/tablet/mobile

---

## Troubleshooting

### Backend won't start

**Error: `No module named 'uvicorn'`**
```bash
# Install Python dependencies
pip install uvicorn fastapi torch pydantic requests
```

**Error: `Cannot connect to localhost:10000`**
- Verify backend server is running: `python -m uvicorn main:app --port 10000`
- Check no other service is using port 10000: `netstat -ano | findstr :10000` (Windows)

### Frontend won't load

**Error: `npm: command not found`**
- Install Node.js from https://nodejs.org/

**Error: `Module not found`**
```bash
# Reinstall dependencies
cd frontend
npm install
npm run dev
```

**Port 5173 already in use**
```bash
# Vite will automatically use next available port (5174, 5175, etc.)
# Or kill process on port 5173
```

### API Connection Issues

**Error: `CORS` in browser console**
- Backend has CORS enabled for all origins
- Ensure both servers are running
- Check browser console for specific errors

**Error: `Model not found`**
- Verify `models/ppo_ep2400.pt` exists in project root
- Check backend logs: "Model loaded" message on startup

---

## Performance Optimization

### Canvas Animation
- Particle system capped at 50 particles to maintain 60 FPS
- Delta-time based physics for smooth motion
- Efficient redraw with background clearing

### API Communication
- Step mode polls every 50ms (adjustable in App.jsx)
- Full simulation returns complete trajectory in single request
- No long-polling or WebSocket overhead

### Build for Production

```bash
# Frontend production build
cd frontend
npm run build

# Output: dist/ folder with optimized bundle
# Serve with: npx serve dist/
```

Backend deployment options:
- Railway (easy, has free tier)
- Fly.io
- AWS EC2 / Lambda
- Docker container

---

## File Structure

```
rocket_landing/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── env.py                  # RocketEnv simulation
│   ├── agent.py                # PPOAgent model
│   ├── model.py                # Network architecture
│   └── __pycache__/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main component
│   │   ├── App.css             # Main styles
│   │   ├── main.jsx            # React entry point
│   │   └── components/
│   │       ├── SimulationCanvas.jsx
│   │       ├── SimulationCanvas.css
│   │       ├── ControlPanel.jsx
│   │       ├── ControlPanel.css
│   │       ├── MetricsPanel.jsx
│   │       └── MetricsPanel.css
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── node_modules/
│
├── models/
│   └── ppo_ep2400.pt           # Trained model
│
└── SETUP_GUIDE.md              # This file
```

---

## Next Steps

### Deployment
1. Deploy backend to Railway/Fly.io
2. Update frontend API base URL to deployed backend
3. Deploy frontend to Vercel/Netlify
4. Share public URL

### Enhancement Ideas
- Add training dashboard (episodes, rewards over time)
- Record & share videos of simulations
- Add different difficulty modes
- Implement multiple model selection
- Add performance metrics (FPS, lag indicators)
- Create downloadable telemetry data

### Development Tasks
- [ ] Add E2E tests (Cypress/Playwright)
- [ ] Implement error boundaries
- [ ] Add loading skeletons
- [ ] Create Favicon
- [ ] Add PWA support
- [ ] Implement dark/light theme toggle

---

## Support

For issues or questions:
1. Check browser console for errors (F12)
2. Check backend terminal for API errors
3. Verify both services are running
4. Review API response format

**Quick Test:**
```bash
# Test API directly
curl http://localhost:10000/health
curl -X POST http://localhost:10000/reset
curl http://localhost:10000/stats
```

---

**Built with**: PyTorch (RL), FastAPI, React 18, Vite, Canvas API
**Status**: Production-Ready
**Last Updated**: 2024
