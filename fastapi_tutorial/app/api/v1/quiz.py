from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from app import models, schemas
from app.database import get_db
# db 끌어오는 과정은 동일


router = APIRouter()


@router.get("", response_model=List[schemas.Quiz])
async def get_quiz_list(db: Session = Depends(get_db)):
    return db.query(models.Quiz).all()


@router.post("", response_model=schemas.ResourceId, status_code=status.HTTP_201_CREATED)
async def create_quiz(data: schemas.QuizCreate, db: Session = Depends(get_db)):
    row = models.Quiz(**data.dict())
    db.add(row)
    db.commit()

    return row


@router.get("/random", response_model=schemas.Quiz)
async def get_quiz_randomly(db: Session = Depends(get_db)):
    return db.query(models.Quiz).order_by(func.RAND()).first()
    # SQL 로 하자면
    '''
    SELECT *
    FROM quiz
    ORDER BY RAND();
    db.query(models.Quiz).order_by(func.RAND()).first()
    '''
