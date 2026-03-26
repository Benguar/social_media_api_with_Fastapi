from fastapi import APIRouter,status,HTTPException,Depends
from social.db.models import Posts,Likes
from social.db.connection import get_db
from sqlalchemy.orm import joinedload,selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from social.schemas.classes import Posts_class,PostResponse,Posts_Update,TokenData
from sqlalchemy import select,insert,delete,update,func
from social.src.oauth import get_current_user
from social.src.Groq import call_groq
 
route = APIRouter()

@route.get("")
async def get_posts(search: str |None = None,user_id: TokenData = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    if search == None:
        query =await  db.execute(select(Posts).options(joinedload(Posts.user),selectinload(Posts.likes)).where(Posts.user_id == user_id.id))
    else:
        query =await db.execute(select(Posts,func.count(Likes.post_id).label("likes")).join(Likes,Posts.id == Likes.post_id, isouter=True).group_by(Posts.id).where(Posts.posts.contains(search)))
    result = query.scalars().all()
    if not result:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= 'No posts yet')
    return result
@route.get("/{post_id}",response_model=PostResponse)
async def get_post(post_id: int,user_id: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query =await  db.execute(select(Posts).options(joinedload(Posts.user),selectinload(Posts.likes)).filter(Posts.user_id == user_id.id, Posts.id == post_id))
    result = query.scalars().first()

    if not result:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    return result

@route.post("/add_post", status_code=status.HTTP_201_CREATED)
async def add_post(input: Posts_class,user_id: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    input.user_id = user_id.id
    query = await db.execute(insert(Posts).values(**input.model_dump()).returning(Posts))
    await db.commit()
    summary = await call_groq(input.posts)
    return input.posts,summary

@route.delete("/delete_post/{delete_post}")
async def delete_post(delete_post: int,user_id: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = await db.execute(delete(Posts).filter(Posts.id == delete_post,Posts.user_id == user_id.id))
    if query.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f'Post not found')
    await db.commit()
    return "successful"
    

@route.patch("/update_post/{post_id}")
async def update_post(post_id: int,input: Posts_Update,user_id: TokenData = Depends(get_current_user),db: AsyncSession = Depends(get_db)):

    query =await db.execute(update(Posts).values(**input.model_dump(exclude_unset=True)).filter(Posts.id ==  post_id,Posts.user_id == user_id.id).returning(Posts))
    result = query.scalars().first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'post not found')
    await db.commit()
    return result