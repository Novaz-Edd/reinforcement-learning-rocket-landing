"""
FastAPI Backend for Rocket Landing Simulator

Provides RESTful endpoints for:
- Running full episodes
- Step-by-step simulation
- Real-time data streaming
- Environment management
"""

import os
import sys
import torch
import numpy as np
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from env import RocketEnv
from agent import PPOAgent


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

class StepData(BaseModel):
    """Single simulation step data."""
    y: float
    vy: float
    fuel: float
    action: int
    done: bool
    landed: bool
    crashed: bool
    reward: float


class EpisodeData(BaseModel):
    """Complete episode trajectory."""
    steps: List[StepData]
    total_reward: float
    status: str  # "landed", "crashed", "timeout"
    final_velocity: float
    total_steps: int


class ResetResponse(BaseModel):
    """Response after reset."""
    status: str
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Rocket Landing Simulator API",
    description="AI-powered rocket landing simulation using PPO reinforcement learning",
    version="1.0.0"
)

# Enable CORS for all origins (development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STATE
# ─────────────────────────────────────────────────────────────────────────────

class SimulationState:
    """Manages global simulation state."""
    
    def __init__(self):
        self.env: Optional[RocketEnv] = None
        self.agent: Optional[PPOAgent] = None
        self.obs = None
        self.episode_data = []
        self.episode_reward = 0.0
        self.is_running = False
        self.model_loaded = False
        
    def load_model(self, model_path: str):
        """Load trained PPO model."""
        try:
            self.env = RocketEnv()
            self.agent = PPOAgent(obs_dim=5, action_dim=4, hidden=128)
            self.agent.load(model_path)
            self.agent.net.eval()
            self.model_loaded = True
            print(f"✓ Model loaded: {model_path}")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self.model_loaded = False
            raise
    
    def reset_episode(self):
        """Reset environment for new episode."""
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")
        
        self.obs = self.env.reset()
        self.episode_data = []
        self.episode_reward = 0.0
        self.is_running = True
    
    def step(self) -> StepData:
        """Execute one environment step with deterministic policy."""
        if not self.is_running:
            raise RuntimeError("Episode not running")
        
        # Get deterministic action (argmax)
        obs_t = torch.FloatTensor(self.obs).unsqueeze(0)
        with torch.no_grad():
            logits, _ = self.agent.net(obs_t)
        action = torch.argmax(logits, dim=1).item()
        
        # Map 4-action to 2-action space
        if action >= 2:
            action = 1
        
        # Step environment
        self.obs, reward, done, info = self.env.step(action)
        self.episode_reward += reward
        
        # Create step data
        step_data = StepData(
            y=info["y"],
            vy=info["vy"],
            fuel=info["fuel"],
            action=action,
            done=done,
            landed=info["landed"],
            crashed=info["crashed"],
            reward=reward
        )
        
        self.episode_data.append(step_data)
        
        if done:
            self.is_running = False
        
        return step_data
    
    def get_episode_result(self) -> EpisodeData:
        """Get complete episode data."""
        if self.is_running:
            raise RuntimeError("Episode still running")
        
        # Determine status
        if self.env.landed:
            status = "landed"
        elif self.env.crashed:
            status = "crashed"
        else:
            status = "timeout"
        
        final_velocity = abs(self.env.landing_vy) if self.env.landing_vy is not None else abs(self.env.vy)
        
        return EpisodeData(
            steps=self.episode_data,
            total_reward=self.episode_reward,
            status=status,
            final_velocity=final_velocity,
            total_steps=len(self.episode_data)
        )


# Initialize global state
state = SimulationState()
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "ppo_ep2400.pt")

# Load model on startup
try:
    state.load_model(model_path)
except Exception as e:
    print(f"Warning: Model loading failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Rocket Landing Simulator API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": state.model_loaded,
        "endpoints": {
            "simulate": "GET /simulate - Run full episode",
            "step": "GET /step - Run one step",
            "reset": "POST /reset - Reset environment",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    print("[/health] Health check requested")
    return {
        "status": "healthy",
        "model_loaded": state.model_loaded,
        "environment_ready": state.env is not None
    }


@app.post("/reset")
async def reset():
    """Reset environment and start new episode."""
    print("\n[/reset] Resetting environment...")
    
    if not state.model_loaded:
        print("[/reset] ERROR: Model not loaded")
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        state.reset_episode()
        print("[/reset] SUCCESS: Episode initialized")
        return ResetResponse(
            status="success",
            message="Environment reset. Ready for simulation."
        )
    except Exception as e:
        print(f"[/reset] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/step")
async def step():
    """Execute one simulation step."""
    if not state.model_loaded:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not state.is_running:
        if len(state.episode_data) == 0:
            raise HTTPException(status_code=400, detail="Call /reset first to start episode")
        else:
            # Episode finished, return final result
            return {
                "done": True,
                "episode": state.get_episode_result().dict()
            }
    
    try:
        step_data = state.step()
        return {
            "done": step_data.done,
            "step": step_data.dict(),
            "episode_reward": state.episode_reward
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/simulate")
async def simulate():
    """Run complete episode and return trajectory."""
    print("\n[/simulate] Starting full episode simulation...")
    
    if not state.model_loaded:
        print("[/simulate] ERROR: Model not loaded")
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Reset and run until done
        state.reset_episode()
        print(f"[/simulate] Episode reset. Initial obs shape: {state.obs.shape}")
        
        step_count = 0
        while state.is_running:
            state.step()
            step_count += 1
            if step_count % 50 == 0:
                print(f"[/simulate] Step {step_count}: y={state.env.y:.2f}, vy={state.env.vy:.2f}, fuel={state.env.fuel:.1f}")
        
        # Get result
        result = state.get_episode_result()
        print(f"[/simulate] Episode complete: {result.status}, steps={result.total_steps}, reward={result.total_reward:.2f}")
        print(f"[/simulate] Final velocity: {result.final_velocity:.2f} m/s")
        print(f"[/simulate] Trajectory has {len(result.steps)} data points")
        
        return result.dict()
    
    except Exception as e:
        print(f"[/simulate] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def stats():
    """Get current episode statistics."""
    return {
        "model_loaded": state.model_loaded,
        "episode_running": state.is_running,
        "steps_completed": len(state.episode_data),
        "current_reward": state.episode_reward,
        "environment_ready": state.env is not None
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("ROCKET LANDING SIMULATOR - FastAPI Backend")
    print("="*70)
    print(f"Model loaded: {state.model_loaded}")
    print("Starting server on http://localhost:10000")
    print("Docs available at http://localhost:10000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000,
        log_level="info"
    )
