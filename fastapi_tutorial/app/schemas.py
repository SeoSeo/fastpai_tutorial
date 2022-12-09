from pydantic import BaseModel, Field


# ResourceId 클래스 추가.
class ResourceId(BaseModel):
    id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    score: int

    class Config:
        orm_mode = True

# 퀴즈 관련 추가
# 모델 정의


class QuizCreate(BaseModel):
    question: str = Field(..., title="퀴즈 질문", example="🇰🇷 대한민국의 수도는?")
    content: str = Field(..., title="퀴즈 내용", example="1️⃣ 서울\n2️⃣ 인천\n3️⃣ 부산\n4️⃣ 대구")
    answer: int = Field(..., title="정답", example=1)
    # parsing을 pydantic이 다 해 주는 것.


class Quiz(QuizCreate):
    # QuizCreate 상속 받아서 진행
    id: int

    class Config:
        orm_mode = True
