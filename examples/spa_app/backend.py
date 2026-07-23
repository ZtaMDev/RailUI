"""
examples/spa_app/backend.py

Custom FastAPI backend configuration for the spa_app example.
This file is automatically detected and loaded by RailUI at startup.

Key points:
- Create a FastAPI instance and pass it to RailUI(app)
- This app instance is used by the RailUI server — you own the full FastAPI app
- Add CORS, auth middleware, databases, custom API routes — anything FastAPI supports
- @server_action functions can be defined here or in any other file imported by main.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from railui.backend import RailUI, server_action

# 1. Create your FastAPI app
app = FastAPI(title="SPA App Backend")

# 2. Register it with RailUI — this tells the RailUI server to use YOUR app
rail = RailUI(app)

# 3. Add any middleware (e.g. CORS for external frontends, auth headers, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Define custom API routes (e.g. for mobile apps, public APIs, webhooks, etc.)
@app.get("/api/health")
async def health_check():
    """Health check endpoint for Railway/Render/Heroku uptime monitoring."""
    return {"status": "ok", "framework": "RailUI"}

@app.get("/api/version")
async def version():
    """Return the framework version."""
    import railui
    return {"version": railui.__version__}
