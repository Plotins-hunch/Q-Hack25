# backend/main.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.email_routes import router as email_router
from api.chat_routes import router as chat_router
from api.upload_routes import router as upload_router

# Import the data extraction module
from PDFDataExtraction import main as extract_pdf_data

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
app.include_router(upload_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Startup Analyzer API"}

# Define a model for the file path request
class FilePathRequest(BaseModel):
    file_path: str

# Add endpoint to process PDF after upload
@app.post("/api/analyze-pdf")
async def analyze_pdf(request: FilePathRequest):
    try:
        # Call the PDFDataExtraction module with the uploaded file path
        result = extract_pdf_data(request.file_path)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to analyze PDF: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)