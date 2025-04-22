from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os

# Import local modules (to be created)
from config.database import engine, Base, get_db
from api import auth, api_keys, system_prompt, rss_feeds, trading, wallet

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CT-5 Crypto Trading Bot API",
    description="Backend API for CT-5 Crypto Trading Bot with 80s-retro design",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(api_keys.router, prefix="/api/keys", tags=["API Keys"])
app.include_router(system_prompt.router, prefix="/api/system", tags=["System Prompt"])
app.include_router(rss_feeds.router, prefix="/api/rss", tags=["RSS Feeds"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])


# Root endpoint
@app.get("/")
def read_root():
    return {
        "name": "CT-5 Crypto Trading Bot API",
        "status": "online",
        "version": "0.1.0"
    }

# Health check endpoints
@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/db-health")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute("SELECT 1").scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "details": {
                "host": os.getenv("DB_HOST", "unknown"),
                "port": os.getenv("DB_PORT", "unknown"),
                "database": os.getenv("DB_NAME", "unknown"),
                "user": os.getenv("DB_USER", "unknown")
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "details": {
                "host": os.getenv("DB_HOST", "unknown"),
                "port": os.getenv("DB_PORT", "unknown"),
                "database": os.getenv("DB_NAME", "unknown"),
                "user": os.getenv("DB_USER", "unknown")
            }
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
