from fastapi import APIRouter, HTTPException
from models.schemas import SessionStartRequest, SubmitAnswerRequest, CompleteSessionRequest
from services.practice_service import (
    create_practice_session,
    get_session_state,
    record_question_answer,
    complete_session,
    get_session_summary
)

router = APIRouter(prefix="/api/practice", tags=["Practice & Exams"])


@router.post("/start")
def start_session(req: SessionStartRequest):
    try:
        session_data = create_practice_session(
            session_type=req.session_type,
            size=req.size,
            subject_id=req.subject_id,
            topic_id=req.topic_id,
            subtopic_id=req.subtopic_id,
            difficulty=req.difficulty,
            time_limit_minutes=req.time_limit_minutes
        )
        return session_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.get("/{session_id}")
def get_session(session_id: str):
    try:
        return get_session_state(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/answer")
def submit_answer(req: SubmitAnswerRequest):
    try:
        res = record_question_answer(
            session_id=req.session_id,
            question_id=req.question_id,
            selected_option=req.selected_option,
            time_spent_seconds=req.time_spent_seconds,
            is_marked_for_review=req.is_marked_for_review,
            confidence=req.confidence,
            mistake_category=req.mistake_category
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complete")
def finish_session(req: CompleteSessionRequest):
    try:
        res = complete_session(
            session_id=req.session_id,
            time_taken_seconds=req.time_taken_seconds
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}/summary")
def get_summary(session_id: str):
    try:
        return get_session_summary(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
