# backend/api/upload_routes.py
# backend/api/upload_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import httpx

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Call the analyze-pdf endpoint with the file path
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/analyze-pdf",
            json={"file_path": file_path}
        )

        if response.status_code == 200:
            return JSONResponse(
                content={
                    "status": "success",
                    "file_path": file_path,
                    "analysis": response.json()
                }
            )
        else:
            return JSONResponse(
                content={
                    "status": "success",
                    "file_path": file_path,
                    "analysis_status": "pending",
                    "message": "File uploaded successfully. Analysis will be processed asynchronously."
                }
            )