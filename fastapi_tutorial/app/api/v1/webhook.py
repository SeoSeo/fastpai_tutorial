from fastapi import APIRouter, Body, Request, Depends
from pydantic import HttpUrl
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.lib import telegram

router = APIRouter()
bot = telegram.Telegram(settings.TELEGRAM_BOT_TOKEN)


# 유저 추가.
def add_user(user: schemas.User, db: Session) -> models.User:
    row = models.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(row)
    db.commit()
    return row


# GET
@router.get("")
async def get_webhook():
    return await bot.get_webhook()


# POST
@router.post("")
async def set_webhook(url: HttpUrl = Body(..., embed=True)):
    return await bot.set_webhook(url)  # 이걸 이용한 방법.


@router.post(f"/{settings.TELEGRAM_BOT_TOKEN.get_secret_value()}")
async def webhook(request: Request, db: Session = Depends(get_db)):
    # webhook 에 get_secret_value로서 처리되어있으므로 telegram의 docs을 따른 것.
    req = await request.json()
    print(req)  # 추가.
    update = telegram.schemas.Update.parse_obj(req)
    message = update.message
    user = update.message.from_

    db_user = db.query(models.User).filter_by(id=user.id).first()
    # user 가 없을 때
    if not db_user:
        db_user = add_user(user, db)
        # 위에 로직 따로 분리. 재사용성을 위해서. 이러한 자주 쓰는 로직은 utils.py 같이 이후 분리하기도 함.

    # 아래에서 위처럼 함수 처리 하여 변경.
    #     row = models.User(
    #         id=user.id,
    #         username=user.username,
    #         first_name=user.first_name,
    #         last_name=user.last_name,
    #     )
    #     db.add(row)
    #     db.commit()

    # 메세지 추가.
    # ref : https://core.telegram.org/bots/api#sendmessage
    msg = "✨ '문제' 또는 '퀴즈'라고 말씀하시면 문제를 냅니다!"
    if "문제" in message.text or "퀴즈" in message.text or "quiz" in message.text:
        quiz = db.query(models.Quiz).order_by(func.RAND()).first()
        # db.query(models.Quiz).order_by(func.RAND()).first() 를 SQL로 할 때,
        '''
        SELECT *
        FROM quiz
        ORDER BY RAND();
        '''
        if not quiz:
            await bot.send_message(message.chat.id, "퀴즈가 없습니다")
            return

        db_user.quiz_id = quiz.id  # AttributeError: 'NoneType' object has no attribute 'quiz_id'
        msg = f"질문 - {quiz.question}\n\n{quiz.content}"  # text 추가.
    # 퀴즈를 풀고 있고 & 정답이 isnumeric 일 때
    elif db_user.quiz_id and message.text.isnumeric():
        correct = db_user.quiz.answer == int(message.text)
        # quiz 테이블의 answer 에 접속하여 결과(동일하므로 True)를 correct에 저장.
        msg = f"아쉽네요, {db_user.quiz.answer}번이 정답입니다. :("

        # 정답일 때
        if correct:
            db_user.score += 1
            msg = f"{db_user.quiz.answer}번, 정답입니다! :)"

        db_user.quiz_id = None

    await bot.send_message(message.chat.id, msg)  # https://core.telegram.org/bots/api#sendmessage
    db.commit()

    return "webhook - OK"
