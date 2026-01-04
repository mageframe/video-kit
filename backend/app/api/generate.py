from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import uuid
import os

from app.services.kie_client import KieClient
from app.services.job_manager import JobManager
from app.models.job import JobCreate, JobResponse

router = APIRouter()
kie_client = KieClient()
job_manager = JobManager()


class GenerateRequest(BaseModel):
    model: str = "sora2"
    fighter1: Optional[str] = None
    fighter2: Optional[str] = None
    customImageId: str  # ID of the custom image to use
    prompt: str
    music: bool = False
    voices: bool = False
    commentators: bool = False
    duration: int = 5
    quality: str = "720p"
    aspectRatio: str = "16:9"


@router.post("/generate", response_model=JobResponse)
async def generate_video(request: GenerateRequest):
    """
    Generate a fight video using Kie.ai API.

    1. Determine which fighter image(s) to use
    2. Upload image to Kie.ai
    3. Submit video generation request
    4. Create job to track progress
    """
    try:
        # Get custom image path
        base_path = os.getenv("DATA_PATH", "../data")
        image_path = f"{base_path}/custom-images/{request.customImageId}"

        # Verify image exists
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404,
                detail=f"Custom image not found: {request.customImageId}"
            )

        # Create job
        job_id = str(uuid.uuid4())
        job = await job_manager.create_job(
            job_id=job_id,
            model=request.model,
            fighter1=request.fighter1,
            fighter2=request.fighter2,
            prompt=request.prompt,
            image_source="custom",
            options={
                "music": request.music,
                "voices": request.voices,
                "commentators": request.commentators,
            },
            video_params={
                "duration": request.duration,
                "quality": request.quality,
                "aspectRatio": request.aspectRatio,
            }
        )

        # Upload image and generate video (async background task)
        await job_manager.start_generation(job_id, image_path)

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-custom-image")
async def upload_custom_image(file: UploadFile = File(...)):
    """Upload a custom fighter image for video generation."""
    try:
        base_path = os.getenv("DATA_PATH", "../data")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = f"{base_path}/custom-images/{file_id}.jpg"

        # Ensure directory exists
        os.makedirs(f"{base_path}/custom-images", exist_ok=True)

        # Save file
        import aiofiles
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        return {"fileId": file_id, "filePath": file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
