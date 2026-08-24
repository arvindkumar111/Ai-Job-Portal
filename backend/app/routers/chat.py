from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.rag_chat import answer_chat_question

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    result = answer_chat_question(
        db=db,
        api_key=request.gemini_api_key,
        question=request.question,
        job_id=request.job_id,
        resume_text=request.resume_text,
        conversation_history=request.conversation_history,
    )
    return ChatResponse(**result)