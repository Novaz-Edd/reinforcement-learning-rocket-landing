# QUICK START VISUAL GUIDE

## What You Should See Right Now

### 1. Backend Status (Check Terminal 1)
```
Model loaded <- C:\...\models\ppo_ep2400.pt
✓ Model loaded: C:\...\models\ppo_ep2400.pt
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
```

### 2. Frontend Status (Check Terminal 2)
```
> rocket-landing-simulator@1.0.0 dev
> vite

  VITE v4.5.14  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h to show help
```

### 3. Open Browser - http://localhost:5173/

You should see a dashboard with THREE PANELS:

```
┌──────────────────────────────────────────────────────────────┐
│                AIRocket Landing Simulator                    │
├────────────────┬────────────────────┬──────────────────────┤
│  CONTROLS      │  CANVAS            │  METRICS             │
│                │                    │                      │
│ [Start]         │  Dark space        │ Status:      IDLE   │
│ [Reset]        │  gradient          │ Height:      --m    │
│ [Step Mode]    │                    │ Velocity:    --m/s  │
│ [Next Step]    │  "Click Start →    │ Fuel:        --% Sim" │  Action:   -- │
│                │                    │                      │
│ Model: PPO     │                    │ Steps:       0/0     │
│ Ep2400         │                    │                      │
│                │                    │ [Start to begin]     │
└────────────────┴────────────────────┴──────────────────────┘
```

### 4. Click "Start Simulation"

Wait 2-3 seconds, then you should see:

```
┌──────────────────────────────────────────────────────────────┐
│                AI Rocket Landing Simulator                   │
├────────────────┬────────────────────┬──────────────────────┤
│  CONTROLS      │  CANVAS            │  METRICS             │
│                │                    │                      │
│ [Start]         │  ▲▲▲▲▲▲▲▲▲        │ Status:    FLYING    │
│ [Reset]        │  ║Sky Gradient║    │ Height:    67.3 m   │
│ [Next Step]    │  ║            ║    │ Velocity:  -8.2 m/s │
│ [Step Mode]    │  ║            ║    │ Fuel:      95.0 %   │
│                │  ║    ╱╲       ║    │ Action:    THRUST   │
│                │  ║   ╱  ╲ (Rocket)║    │                      │
│                │  ║ Flame╱╲║    │ Steps:     12/158   │
│                │  ║         *  ║    │                      │
│                │  ║      (particles)║│ Progress:  ████░░░  │
│                │  ║            ║    │                      │
│                │  ▼▼▼▼▼▼▼▼▼ Ground ║    │                      │
│                │                    │                      │
└────────────────┴────────────────────┴──────────────────────┘
```

### 5. Watching the Animation

As the simulation runs, you'll see:

**T=0-30 steps (Early descent):**
- Rocket falling fast
- Velocity increasing (negative)
- Fuel decreasing
- Action alternates between 0 (IDLE) and 1 (THRUST)
- Particles appear when thrusting

**T=30-100 steps (Mid descent):**
- Rocket slowing down (when thrusting)
- Height gradually decreasing
- Agent learning to control descent
- More particles/flame effects

**T=100-end (Final approach):**
- Rocket approaching ground (y < 5m)
- Final push to land safely
- Either:
  - **GREEN STATUS**: Successful landing (vy < 4 m/s)
  - **RED STATUS**: Crash (vy > 15 m/s)

**At end of episode:**
```
Status: LANDED (green) or CRASHED (red)
Height: 0.0m
Velocity: 0.5 m/s (landed) or 40.2 m/s (crashed)
Final Stats:
  - Total Steps: 158
  - Total Reward: -66.22 (crashed) or +145.3 (landed)
  - Fuel Remaining: 0.0%
```

---

## Browser Console Debugging (F12 > Console Tab)

You should see logs like:

```javascript
📌 [handleStartClick] Starting in AUTO mode
🔄 [resetEnv] Resetting environment...
🔄 [resetEnv] Calling POST /reset
🔄 [resetEnv] Response status: 200
🔄 [resetEnv] SUCCESS
🚀 [runSimulation] Starting full episode fetch...
🚀 [runSimulation] Fetching from: http://localhost:10000/simulate
🚀 [runSimulation] Response status: 200
🚀 [runSimulation] Data received: {
  status: "crashed",
  totalSteps: 158,
  totalReward: -66.22,
  stepsCount: 158,
  firstStep: {y: 56.29, vy: -6.25, fuel: 99.0, action: 1, done: false, …},
  lastStep: {y: 0, vy: -40.22, fuel: 0, action: 1, done: true, …}
}
🚀 [runSimulation] Episode complete: crashed
🎬 [Canvas] Animation loop started, stepData: {y: 56.29, vy: -6.25, …}
```

---

## Network Tab (Browser DevTools)

Check for these requests:

```
GET http://localhost:10000/health
  Status: 200
  Response: {status: "healthy", model_loaded: true, ...}

POST http://localhost:10000/reset
  Status: 200
  Response: {status: "success", message: "Environment reset..."}

GET http://localhost:10000/simulate
  Status: 200
  Load time: 15-30 seconds (normal for full episode)
  Response size: ~50-100 KB
  Response: {
    steps: [{...}, {...}, ...],
    total_reward: -66.22,
    status: "crashed",
    ...
  }
```

---

## Expected Behavior - Checklist

As you click "Start Simulation", verify:

- [ ] Button becomes disabled (shows loading)
- [ ] Canvas shows dark background
- [ ] Rocket appears (vertical silver bar)
- [ ] Rocket is centered horizontally
- [ ] Rocket starts falling (moving down)
- [ ] Orange/yellow flame appears below rocket
- [ ] Particles emit from flame
- [ ] Metrics panel shows updating values:
  - [ ] Height decreasing
  - [ ] Velocity becoming more negative (faster fall)
  - [ ] Fuel decreasing
  - [ ] Status shows "FLYING"
  - [ ] Step counter incrementing
- [ ] Progress bar at bottom fills
- [ ] Animation ends with status message
- [ ] Final metrics displayed
- [ ] "Start" button becomes active again

---

## If Something's Wrong

### Canvas is blank/dark
**Check**: Browser console for errors
**Fix**: Make sure /simulate endpoint returned data

### Rocket not visible
**Check**: Console logs say "Animation loop started"
**Fix**: Verify stepData contains y, vy values

### Metrics not updating
**Check**: Network tab shows /simulate response
**Fix**: Make sure simData contains steps array

### Button doesn't work
**Check**: Console for "ERROR: ..."
**Fix**: Verify backend is http://localhost:10000 (not 8000)

### Performance is sluggy
**Check**: Browser console, particle count
**Fix**: Normal during simulation, should be smooth after

---

## Test Simulation Flow

1. **Click "Start"** → See "click to begin message" disappear
2. **Wait 2-3 seconds** → Rocket appears, starts falling
3. **Watch 20 seconds** → Rocket descends with animation
4. **See result** → Final status (landed/crashed) displayed
5. **Click "Reset"** → Canvas goes back to "click to begin"
6. **Click "Start" again** → New simulation runs (different result)

---

## Troubleshooting Checklist

```
[ ] Both terminals show "ready" messages
[ ] Browser opens without errors (F12 no red errors)
[ ] Canvas element visible (not blank)
[ ] Clicking buttons doesn't cause errors
[ ] Network requests show 200 OK status
[ ] Rocket appears and moves
[ ] Episode completes with final stats
[ ] Can start multiple simulations
```

---

**If all checks pass, your application is working perfectly!**
**Share the visual by taking a screenshot or recording a short video.**
