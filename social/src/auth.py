from fastapi import APIRouter,status,Depends,HTTPException,Response,Request
from social.db.connection import get_db
from social.db.models import User,Refresh
from social.schemas.classes import Login,TokenData
from social.src.users import ph
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,insert,update,delete
from argon2.exceptions import VerifyMismatchError
from social.src.oauth import create_access_token,verify_refresh_token,get_current_user
from social.db.redis import add_blacklist,remove_active
route = APIRouter()

@route.post("/login",status_code=status.HTTP_200_OK)
async def login(request: Request,input: Login,response: Response,db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(User).filter(User.username == input.username))
    values = query.scalars().first()
    if not values:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f'invalid credentials')
    try:
        ph.verify(values.password,input.password.get_secret_value())
    except VerifyMismatchError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="invalid credential")
    payload = {"user_id": values.id,"username": values.username}
    token,refresh_input = await create_access_token(response,payload)
    user_agent = request.headers.get("User-Agent")
    request_query = await db.execute(insert(Refresh).values(user_agent = user_agent,**refresh_input.model_dump()))
    await db.commit()
    return {"access_token": token.access_token,"refresh_token": token.refresh_token,"jti": token.jti,"token_type": "bearer"}

@route.post("/refresh",tags=["refresh"])
async def refresh_token(response: Response,request: Request,db: AsyncSession = Depends(get_db)):
    payload,jti = verify_refresh_token(request)
    remove = await remove_active(jti)
    if remove == 0:
        query = await db.execute(select(Refresh).where(Refresh.refresh_jti == jti))
        detail = query.scalars().first()
        if detail.is_used is not None:
            # logout all user
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='malicious activity detected')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= 'unauthorized token')
    token,refresh_input = await create_access_token(response,payload) # we are going to rotate refresh for security sake
    query = await db.execute(update(Refresh).values(is_used=True).where(Refresh.refresh_jti == jti))
    await db.commit()
    input_query = await db.execute(insert(Refresh).values(user_agent=request.headers.get("User-Agent"),**refresh_input.model_dump()))
    await db.commit()
    return token


@route.post("/logout")
async def logout_user(response: Response,token: TokenData = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    valid= await remove_active(token.jti)
    await add_blacklist(token.jti)
    response.delete_cookie(
        key='refresh_cookie',
        secure=False #set to true if deployed
    )
    query =await  db.execute(update(Refresh).values(is_revoked = True).where(Refresh.refresh_jti == token.jti))
    await db.commit()
    
    return "success"
