# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.email_routes import router as email_router
from api.chat_routes import router as chat_router

# Create FastAPI application
app = FastAPI(title="Startup Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(email_router)
app.include_router(chat_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Startup Analyzer API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)