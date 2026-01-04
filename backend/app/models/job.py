from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class JobCreate(BaseModel):
    model: str = "sora2"
    fighter1: Optional[str] = None
    fighter2: Optional[str] = None
    prompt: str
    imageSource: str
    options: Dict
    videoParams: Dict


class JobResponse(BaseModel):
    id: str
    model: str = "sora2"
    fighter1: Optional[str] = None
    fighter2: Optional[str] = None
    prompt: str
    imageSource: str
    status: str  # pending, uploading, generating, downloading, completed, failed
    options: Dict
    videoParams: Dict
    kieTaskId: Optional[str] = None
    videoUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    cost: Optional[float] = None  # Cost in credits/dollars
    error: Optional[str] = None
    createdAt: str
    updatedAt: str
    completedAt: Optional[str] = None


class JobStatus(BaseModel):
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
