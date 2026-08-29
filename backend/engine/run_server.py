"""
run_server.py — Development server entry point.

Run from the engine/ directory:

    python run_server.py
    # or
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

The server must be started from the engine/ directory so that all
relative imports (config.py, database/, agent/, etc.) resolve correctly.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
    )
