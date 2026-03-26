from fastapi import status,APIRouter,HTTPException,Depends
from social.db.models import User,Posts
from social.schemas.classes import User_class,UserResponse,User_update,Login,TokenData
from social.db.connection import get_db
from sqlalchemy.orm import Session,selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,insert,delete,update
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from social.src.oauth import get_current_user



ph = PasswordHasher()

route = APIRouter()





@route.get("/user", status_code= status.HTTP_200_OK,response_model= UserResponse)
async def get_user(id: TokenData = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    print(id)
    query = await db.execute(select(User).options(selectinload(User.posts)).filter(User.id == id.id))
    return query.scalars().first()


@route.post("/add_user", status_code= status.HTTP_201_CREATED)
async def add_user(input: User_class, db: AsyncSession = Depends(get_db)):
    hash = ph.hash(input.password.get_secret_value())
    input.password = hash
    query = await db.execute(insert(User).values(**input.model_dump()).returning(User))
    result = query.scalars().first()
    dict_result = {
        'username': result.username,
        'email': result.email,
        'password': result.password
    }
    await db.commit()
    return dict_result

@route.delete('/delete_user')
async def delete_user(id: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = await db.execute(delete(User).filter(User.id == id.id))
    await db.commit()
    return "successful"

@route.patch('/update_user')
async def update_user(input: User_update,id: TokenData = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    query = await db.execute(update(User).values(**input.model_dump(exclude_unset= True)).filter(User.id == id.id).ret)
    await db.commit()
    return "successful"


