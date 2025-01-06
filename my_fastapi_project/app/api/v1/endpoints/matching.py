from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import dependencies
from app.schemas.matching import UserMatchingCreate, UserMatching
from app.services.gpt_matching_service import GPTMatchingService

router = APIRouter()

@router.post("/match/", response_model=List[Dict])
def get_matching_candidates(
    category_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user_id: int = Depends(dependencies.get_current_user_id)
):
    matching_service = GPTMatchingService(db)
    matches = matching_service.get_matching_candidates(current_user_id, category_id)
    return matches

@router.post("/match/create/", response_model=UserMatching)
def create_matching(
    matching_data: UserMatchingCreate,
    callee_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user_id: int = Depends(dependencies.get_current_user_id)
):
    matching_service = GPTMatchingService(db)
    # GPT로 최종 확인
    match_analysis = matching_service._analyze_match(
        current_user_id, 
        callee_id, 
        matching_data.matching_category_id
    )
    
    # 매칭 점수가 너무 낮으면 경고
    if match_analysis["score"] < 0.3:
        raise HTTPException(
            status_code=400,
            detail=f"Low matching score ({match_analysis['score']}). Reason: {match_analysis['reasoning']}"
        )
    
    matching = matching_service.create_matching(
        caller_id=current_user_id,
        callee_id=callee_id,
        category_id=matching_data.matching_category_id,
        comment=f"{matching_data.comment}\n\nGPT 분석: {match_analysis['recommendation']}"
    )
    return matching