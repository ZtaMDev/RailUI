import os
import sys
import shutil
import subprocess
from typing import Optional

def _find_dars_bundler() -> Optional[str]:
    """
    Locate the dars-bundler binary in the `railui/bundler` directory.
    """
    generic = 'dars-bundler.exe' if sys.platform == 'win32' else 'dars-bundler'

    if sys.platform == 'win32':
        platform_names = ['dars-bundler-windows.exe', generic]
    elif sys.platform == 'darwin':
        import platform as _pl
        if _pl.machine() == 'arm64':
            platform_names = ['dars-bundler-mac-arm', 'dars-bundler-mac', generic]
        else:
            platform_names = ['dars-bundler-mac', generic]
    else:
        platform_names = ['dars-bundler-linux', generic]

    # Look in the railui/bundler folder
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundler_dir = os.path.join(pkg_dir, 'bundler')
    
    for name in platform_names:
        candidate = os.path.join(bundler_dir, name)
        if os.path.isfile(candidate):
            return candidate

    return None

def run_bundler(output_dir: str) -> bool:
    """
    Run dars-bundler on the given output directory to minify JS and CSS.
    Returns True if successful, False otherwise.
    """
    bundler = _find_dars_bundler()
    if not bundler:
        print("\033[33m[railui] Warning: dars-bundler not found in railui/bundler, skipping minification.\033[0m")
        return False

    cmd = [bundler, '--input', output_dir]
    try:
        print(f"\033[36m[railui]\033[0m minifying assets with \033[1mdars-bundler\033[0m...")
        # Make sure the bundler has executable permissions (on linux/mac)
        if sys.platform != 'win32' and not os.access(bundler, os.X_OK):
            os.chmod(bundler, 0o755)

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        if p.stdout is not None:
            for line in iter(p.stdout.readline, ''):
                line = line.strip()
                if line:
                    print(f"  \033[2m{line}\033[0m")
        p.wait()
        return p.returncode == 0
    except Exception as e:
        print(f"\033[31m[railui] Error running dars-bundler: {e}\033[0m")
        return False
