"""
railui/backend/__init__.py

FastAPI backend integration classes and helpers for RailUI.
Allows developers to attach a custom FastAPI instance to the framework.
"""
from fastapi import FastAPI
from railui.core.actions import server_action

class RailUI:
    """
    Integrates a custom FastAPI application instance with the RailUI runtime.
    Use this inside `backend.py` to add custom routes, middleware, CORS, databases, etc.
    """
    _instance = None

    def __init__(self, app: FastAPI):
        self.app = app
        RailUI._instance = self
