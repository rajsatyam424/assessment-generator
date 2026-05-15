"""
Entry point — run with: uvicorn assessment_engine.api:app
Or: python -m assessment_engine
"""

import uvicorn
from . import config

app = None  # lazy import to avoid circular deps on module-level import


def main():
    global app
    from .api import app as _app
    app = _app

    host = config._env_str("HOST", "0.0.0.0")
    port = config._env_int("PORT", 8000)

    print(f"Assessment Generator API")
    print(f"  Provider: {config.PROVIDER}")
    print(f"  Model:    {config.MODEL}")
    print(f"  Server:   http://{host}:{port}")
    print(f"  Docs:     http://{host}:{port}/docs")
    print(f"  Output:   {config.OUTPUT_DIR}")
    print()

    uvicorn.run(
        "assessment_engine.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
