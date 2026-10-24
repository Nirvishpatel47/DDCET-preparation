import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.import_export_service import (
    process_import,
    export_questions,
    export_quarantined_records,
    TEMPLATES_DIR
)
from database.db import create_backup, restore_backup, list_backups

router = APIRouter(prefix="/api/import-export", tags=["Import & Export"])


class RestoreRequest(BaseModel):
    backup_path: str


@router.post("/preview")
async def preview_file(file: UploadFile = File(...)):
    """
    Parses and inspects uploaded JSON, CSV, or XLSX file.
    Performs duplicate detection and validation without committing to DB.
    """
    try:
        content = await file.read()
        res = process_import(content, file.filename, preview_only=True)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File preview failed: {str(e)}")


@router.post("/commit")
async def commit_file(file: UploadFile = File(...)):
    """
    Validates and commits valid MCQs to database.
    Quarantines rejected or invalid records with diagnostic error messages.
    """
    try:
        content = await file.read()
        res = process_import(content, file.filename, preview_only=False)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File import failed: {str(e)}")


@router.get("/template/{format_type}")
def download_template(format_type: str):
    """Provides downloadable Excel, CSV, or JSON template with sample demonstration questions."""
    fmt = format_type.lower()
    if fmt == "xlsx":
        path = os.path.join(TEMPLATES_DIR, "ddcet_question_template.xlsx")
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "csv":
        path = os.path.join(TEMPLATES_DIR, "ddcet_question_template.csv")
        media = "text/csv"
    elif fmt == "json":
        path = os.path.join(TEMPLATES_DIR, "ddcet_question_template.json")
        media = "application/json"
    elif fmt in ["md", "markdown"]:
        path = os.path.join(TEMPLATES_DIR, "ddcet_question_template.md")
        media = "text/markdown"
    else:
        raise HTTPException(status_code=400, detail="Invalid template format. Use md, xlsx, csv, or json.")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Template file not found.")

    return FileResponse(path, media_type=media, filename=os.path.basename(path))


@router.get("/export/questions")
def export_question_bank(
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    verified_only: bool = False,
    format_type: str = "json"
):
    """Exports questions in JSON, CSV, or XLSX format."""
    try:
        bytes_data, filename, media_type = export_questions(
            subject_id=subject_id,
            topic_id=topic_id,
            verified_only=verified_only,
            format_type=format_type
        )
        return Response(
            content=bytes_data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/quarantine")
def get_quarantined(batch_id: Optional[str] = None):
    """Returns quarantined records with error descriptions for correction."""
    records = export_quarantined_records(batch_id)
    return {"quarantined_count": len(records), "records": records}


@router.post("/backup/create")
def trigger_backup(label: Optional[str] = None):
    """Creates a point-in-time backup of the SQLite database."""
    try:
        path = create_backup(label)
        return {"status": "success", "backup_path": path, "filename": os.path.basename(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.get("/backup/list")
def get_backups():
    """Lists available backups."""
    return {"backups": list_backups()}


@router.post("/backup/restore")
def trigger_restore(req: RestoreRequest):
    """Restores database from specified backup file."""
    try:
        restore_backup(req.backup_path)
        return {"status": "success", "message": f"Successfully restored from {os.path.basename(req.backup_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
