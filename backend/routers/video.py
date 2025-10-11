from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.dbutils import get_db
from models.models import Job
from models.schemas import VideoDubCreate, VideoDubResponse, VideoDubStatus
from models.enums import JobStatus
from services.video_processor import process_video_dubbing_sync

router = APIRouter()

@router.post("/create", response_model=VideoDubResponse, summary="Create a new video dubbing job")
def create_video_dub_job(
    video_dub: VideoDubCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    
    db_job = Job(
        video_url=video_dub.video_url,
        target_language=video_dub.target_language,
        status=JobStatus.PENDING
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    background_tasks.add_task(process_video_dubbing_sync, db_job.job_id)
    
    return VideoDubResponse(
        job_id=db_job.job_id,
        status=db_job.status,
        message="Video dubbing job created successfully. Processing will begin shortly."
    )

@router.get("/status/{job_id}", response_model=VideoDubStatus, summary="Get video dubbing job status")
def get_video_dub_status(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return VideoDubStatus(
        job_id=job.job_id,
        video_url=job.video_url,
        target_language=job.target_language,
        status=JobStatus(job.status),
        error_code=job.error_code,
        output_video_path=job.output_video_path,
        created_at=job.created_at,
        updated_at=job.updated_at
    )

@router.get("/jobs", response_model=list[VideoDubStatus], summary="List all video dubbing jobs")
def list_video_dub_jobs(db: Session = Depends(get_db)):    
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    
    return [
        VideoDubStatus(
            job_id=job.job_id,
            video_url=job.video_url,
            target_language=job.target_language,
            status=JobStatus(job.status),
            error_code=job.error_code,
            output_video_path=job.output_video_path,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        for job in jobs
    ]
