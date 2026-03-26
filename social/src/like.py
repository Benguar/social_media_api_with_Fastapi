from fastapi import APIRouter,Depends,status,HTTPException
from social.db.connection import get_db
from social.db.models import Likes
from social.schemas.classes import Like,TokenData
from sqlalchemy import select,insert,update,delete
from social.src.oauth import get_current_user
from sqlalchemy.orm import Session

route = APIRouter()

@route.post("",status_code=status.HTTP_201_CREATED)
def like(input: Like,user: TokenData = Depends(get_current_user),db: Session = Depends(get_db)):

    
    query = db.execute(select(Likes).where(Likes.post_id == input.post_id, Likes.user_id == user.id)).scalars().first()

    if input.dir == 1:
        if not query:
            add_like= db.execute(insert(Likes).values(post_id = input.post_id,user_id = user.id))
            db.commit()
            return "Liked"
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'post already liked')
    elif input.dir == 0:
        if  not query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail= f'can not unlike')
        else:
            remove_like = db.execute(delete(Likes).where(Likes.post_id == input.post_id, Likes.user_id == user.id))
            db.commit()
            return "Unliked"
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f'invalid dir {input.dir}')
