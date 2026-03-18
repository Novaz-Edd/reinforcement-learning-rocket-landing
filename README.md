# 🚀 AI Rocket Landing Simulator

A production-ready web application that demonstrates a trained reinforcement learning (PPO) agent controlling a rocket through atmospheric descent and landing.

**Live Demo**: [Coming Soon] | **Video Demo**: [Coming Soon]

---

## 🎯 Features

- **AI-Powered Simulation**: Trained PPO reinforcement learning agent
- **Real-Time Visualization**: Smooth 60 FPS Canvas-based animation
- **Interactive Controls**: Auto-run and step-by-step modes
- **Live Telemetry**: Height, velocity, fuel, and action display
- **Professional UI**: SpaceX/NASA-inspired glassmorphism design
- **Responsive Layout**: Desktop, tablet, and mobile compatible
- **RESTful API**: FastAPI backend with full Swagger documentation

---

## 🚀 Quick Start

### Option 1: Automatic (Windows)
Double-click **`START.bat`** in the project root. This will:
- Verify Python and Node.js are installed
- Start backend server (port 10000)
- Start frontend server (port 5173)
- Open application in your browser

### Option 2: Manual (All Platforms)

**Terminal 1 - Start Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 10000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install  # Only needed first time
npm run dev
```

**Open Browser:**
```
http://localhost:5173/
```

---

## 📊 Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  AI ROCKET LANDING SIMULATOR                        │
├─────────────────┬──────────────┬──────────────────┤
│                 │              │                  │
│  CONTROLS       │   CANVAS     │    METRICS      │
│                 │              │                  │
│ • Start         │   Rocket ⚡   │ Status: Flying  │
│ • Reset         │   Animation  │ Height: 75.4m   │
│ • Step Mode     │   Particles  │ Velocity: -5.2ms│
│ • Next Step     │   60 FPS     │ Fuel: 87%       │
│                 │              │ Action: THRUST  │
│ Model: PPO      │              │                 │
│ Ep2400          │              │ Episode Stats   │
│                 │              │ (on landing)    │
│                 │              │                 │
└─────────────────┴──────────────┴──────────────────┘
```

---

## 🎮 How to Use

### Auto-Run Mode
1. Open application
2. Click **"Start Simulation"**
3. Watch AI control rocket descent
4. View landing/crash results

### Step-by-Step Mode
1. Toggle **"Step Mode"** checkbox
2. Click **"Start"** to initialize
3. Click **"Next Step"** to advance one frame
4. Perfect for observing AI decisions

### Understanding the Display

**Status Indicator (Top Right)**
- 🟢 Green = Flying normally
- 🔴 Red = Crashed
- 🟡 Yellow = Warning (low fuel/high velocity)

**Metrics**
- **Height**: Altitude above ground (0-100m)
- **Velocity**: Descent speed (negative = falling)
- **Fuel**: Remaining propellant (0-100%)
- **Action**: Current control input (IDLE or THRUST)

---

## 🏗️ Architecture

### Backend (FastAPI - Python)
```python
# 6 Endpoints
GET /health        → Server status
POST /reset         → New episode
GET /step           → Single timestep
GET /simulate       → Full episode
GET /stats          → Session stats
GET /docs           → Swagger UI
```

**Key Files:**
- `backend/main.py` - FastAPI server (370 lines)
- `backend/env.py` - RocketEnv simulation
- `backend/agent.py` - PPO agent inference
- `backend/model.py` - Network architecture

**Model**: `models/ppo_ep2400.pt` (trained for 2400 episodes)

### Frontend (React + Vite)
```javascript
// Component Structure
App (Main)
├── ControlPanel (User controls)
├── SimulationCanvas (Canvas animation)
└── MetricsPanel (Telemetry display)
```

**Key Files:**
- `frontend/src/App.jsx` - Main component
- `frontend/src/components/SimulationCanvas.jsx` - Canvas rendering
- `frontend/src/components/ControlPanel.jsx` - Controls
- `frontend/src/components/MetricsPanel.jsx` - Metrics display

---

## 📋 Project Structure

```
rocket_landing/
├── START.bat                    ← Click this to run!
├── README.md                    ← You are here
├── SETUP_GUIDE.md              → Detailed setup instructions
├── DEPLOYMENT_CHECKLIST.md     → Deployment guide
│
├── backend/
│   ├── main.py                 (370 lines) FastAPI server
│   ├── env.py                  RocketEnv simulation
│   ├── agent.py                PPO agent
│   ├── model.py                Network architecture
│   ├── train.py                Training script (reference)
│   └── requirements.txt         Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             (180 lines) Main component
│   │   ├── App.css             (180 lines) Main styles
│   │   ├── main.jsx            React entry point
│   │   └── components/
│   │       ├── SimulationCanvas.jsx    (260 lines)
│   │       ├── SimulationCanvas.css    
│   │       ├── ControlPanel.jsx        (75 lines)
│   │       ├── ControlPanel.css        (200 lines)
│   │       ├── MetricsPanel.jsx        (110 lines)
│   │       └── MetricsPanel.css        (220 lines)
│   ├── index.html              HTML entry point
│   ├── vite.config.js          Vite config
│   ├── package.json            Dependencies
│   └── dist/                   (auto-generated on build)
│
├── models/
│   └── ppo_ep2400.pt           Trained rocket landing agent
│
└── README.md                   This file
```

---

## 🔧 Technical Stack

### Backend
- **Framework**: FastAPI (Python web framework)
- **AI/ML**: PyTorch (inference engine)
- **Server**: Uvicorn (ASGI server)
- **API**: RESTful with CORS enabled
- **Validation**: Pydantic models

### Frontend
- **Framework**: React 18 (UI library)
- **Bundler**: Vite (fast build tool)
- **Rendering**: HTML5 Canvas
- **Styling**: CSS3 (Glassmorphism design)
- **Animation**: RequestAnimationFrame (60 FPS)

### Deployment
- **Backend**: Railway, Fly.io, or Heroku
- **Frontend**: Vercel, Netlify, or GitHub Pages
- **Optional**: Docker containerization

---

## 📈 Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Backend startup | <5s | ~3-4s |
| Model load | ~5s | ~4s |
| API response | <100ms | ~50-80ms |
| Canvas FPS | 60 | ~55-60 |
| Browser load | <2s | ~1.2s |
| Full episode | <30s | ~15-20s |

---

## 🚀 Deployment

### Local Development (Current)
Already running on `localhost:5173` (frontend) and `localhost:10000` (backend)

### Production Deployment

**1. Build Frontend**
```bash
cd frontend
npm run build
```

**2. Deploy Frontend**
- Upload `frontend/dist/` to Vercel/Netlify
- Or host on GitHub Pages

**3. Deploy Backend**
- Push to Railway/Fly.io
- Auto-deploys from GitHub
- Updates API URL in frontend config

**See DEPLOYMENT_CHECKLIST.md for detailed steps**

---

## 🎓 Learning Resources

### How the AI Works
The rocket is controlled by a **Proximal Policy Optimization (PPO)** agent trained with reinforcement learning:
- **Actions**: 0=IDLE, 1=THRUST, 2=GIMBAL_LEFT, 3=GIMBAL_RIGHT
- **Observations**: [altitude, velocity, fuel, x_pos, angle]
- **Goal**: Land safely with minimal fuel and low velocity

### Code Walkthrough
1. **Frontend**: `App.jsx` fetches data from `/step` or `/simulate`
2. **Canvas**: `SimulationCanvas.jsx` renders 60 FPS animation
3. **Backend**: `main.py` runs `env.step()` using trained `agent`
4. **Environment**: `env.py` simulates rocket physics
5. **Agent**: `agent.py` uses policy from `ppo_ep2400.pt`

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Install dependencies
pip install fastapi uvicorn torch pydantic requests

# Then try again
python -m uvicorn main:app --port 10000
```

### Frontend won't load
```bash
# Install Node packages
cd frontend
npm install

# Then start dev server
npm run dev
```

### API Connection error
- Ensure both servers running on correct ports
- Check browser console (F12) for CORS issues
- Verify backend responds: `curl http://localhost:10000/health`

### Port already in use
```bash
# Windows - Kill process on port
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or let Vite use next port (5174, 5175, etc.)
```

---

## 📝 API Documentation

### Swagger UI
Automatically generated at: **http://localhost:10000/docs**

### Example Requests

**Get Health**
```bash
curl http://localhost:10000/health
```

**Reset Environment**
```bash
curl -X POST http://localhost:10000/reset
```

**Get Single Step**
```bash
curl http://localhost:10000/step
```

**Run Full Episode**
```bash
curl http://localhost:10000/simulate
```

---

## 🎨 Design System

### Colors
- **Primary**: #3b82f6 (Blue) - Main actions
- **Secondary**: #8b5cf6 (Purple) - Metrics
- **Success**: #4ade80 (Green) - Landed/OK
- **Danger**: #f87171 (Red) - Crashed/Error

### Typography
- **Family**: System fonts (Segoe UI, Roboto)
- **Headings**: Bold, larger size
- **Body**: Regular weight, legible size

### Components
- **Panels**: Glassmorphism (rgba + blur)
- **Buttons**: Gradient, rounded corners
- **Animations**: Smooth 0.3s transitions

---

## 📸 Screenshots

[To be added after initial deployment]

---

## 🤝 Contributing

Interested in improving this project? Ideas:
- [ ] Add training dashboard
- [ ] Implement video recording
- [ ] Create multiple difficulty levels
- [ ] Add leaderboard
- [ ] Support multiple models
- [ ] Improve particle effects
- [ ] Add wind simulation
- [ ] Create replay feature

---

## 📄 License

This project is provided as-is for educational and portfolio purposes.

---

## 🙏 Credits

**Built with:**
- PyTorch (AI/ML)
- FastAPI (Backend)
- React (Frontend)
- Vite (Build tool)

---

## 📧 Questions?

Check the docs:
1. **SETUP_GUIDE.md** - Installation & usage
2. **DEPLOYMENT_CHECKLIST.md** - Deployment & production

---

## ✨ Status

- ✅ Backend: Complete & Tested
- ✅ Frontend: Complete & Running
- ✅ API: All endpoints working
- ✅ Deployment: Ready for production
- 🎯 Next: Share with the world!

---

**Ready to run?** → Double-click `START.bat` or run:
```bash
cd backend && python -m uvicorn main:app --port 10000  # Terminal 1
cd frontend && npm run dev                              # Terminal 2
```

Then visit: **http://localhost:5173/**

🚀 Enjoy the rocket landing simulator!
