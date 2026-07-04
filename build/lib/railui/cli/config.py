import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class RailUIConfig:
    outdir: str = "dist"
    port: int = 5173
    open_browser: bool = True
    bundle: bool = True
    platform: str = "railway"  # 'railway' or 'vercel'
    public_dirs: List[str] = field(default_factory=lambda: ["public", "assets"])

def load_config(project_dir: str, cli_args: Any) -> RailUIConfig:
    """
    Load configuration from railui.config.json, falling back to defaults,
    and override with any CLI arguments that were explicitly provided.
    """
    config = RailUIConfig()
    
    config_path = os.path.join(project_dir, "railui.config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "outdir" in data: config.outdir = data["outdir"]
            if "port" in data: config.port = data["port"]
            if "open_browser" in data: config.open_browser = data["open_browser"]
            if "bundle" in data: config.bundle = data["bundle"]
            if "platform" in data: config.platform = data["platform"]
            if "public_dirs" in data: config.public_dirs = data["public_dirs"]
        except Exception as e:
            print(f"\033[33m[railui] Warning: Failed to parse railui.config.json: {e}\033[0m")

    # CLI Overrides (only if they are different from argparse defaults / explicitly passed)
    # Argparse passes None if an optional flag isn't provided (if we configure it right),
    # or we can just check if hasattr. We'll assume the caller passes only explicit overrides or we check carefully.
    
    if hasattr(cli_args, "outdir") and cli_args.outdir is not None:
        config.outdir = cli_args.outdir
        
    if hasattr(cli_args, "port") and cli_args.port is not None:
        config.port = cli_args.port
        
    if hasattr(cli_args, "no_open") and cli_args.no_open:
        config.open_browser = False
        
    if hasattr(cli_args, "no_bundle") and cli_args.no_bundle:
        config.bundle = False
        
    if hasattr(cli_args, "platform") and cli_args.platform is not None:
        config.platform = cli_args.platform

    return config
