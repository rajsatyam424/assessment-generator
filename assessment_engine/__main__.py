"""
Entry point — run with: uvicorn assessment_engine.api:app
Or: python -m assessment_engine
"""

import uvicorn
from . import config


def main():
    host = config._env_str("HOST", "0.0.0.0")
    port = config._env_int("PORT", 8000)

    print(f"Assessment Generator API")
    print(f"  Provider: {config.PROVIDER}")
    print(f"  Model:    {config.MODEL}")
    print(f"  Server:   http://{host}:{port}")
    print(f"  Output:   JSON only (no docx)")

    uvicorn.run(
        "assessment_engine.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
