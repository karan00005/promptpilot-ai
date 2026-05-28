import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.compress import router as compress_router
from routers.billing import router as billing_router
from routers.auth import router as auth_router
from routers.context import router as context_router
from routers.proxy import router as proxy_router
from services.local_db import init_db

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize local database tables on application import/startup
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize SQLite local database tables: {e}")

app = FastAPI(
    title="PromptPilot AI API",
    description="The AI token optimization layer that cuts LLM API costs by 30–50%.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend, extension, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains and chrome-extension:// IDs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount compression and authentication routes
app.include_router(compress_router)
app.include_router(billing_router)
app.include_router(auth_router)
app.include_router(context_router)
app.include_router(proxy_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to PromptPilot AI API. For documentation, visit /docs",
        "docs_url": "/docs",
        "status": "healthy"
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("ENVIRONMENT", "production") == "development"
    logger.info(f"Starting PromptPilot FastAPI on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=reload)
