import jwt,asyncio
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
from datetime import datetime,timedelta,timezone
from social.schemas.classes import TokenData,Token,RefreshInput
from fastapi import Depends,status,HTTPException,Response,Cookie,Request
from social.db.settings import settings
from fastapi.security import OAuth2PasswordBearer
from social.db.settings import settings
from uuid6 import uuid7
from typing import Annotated
from social.db.redis import add_active,check_blacklist


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'/social/login/v1')


SECRET_KEY = settings.JWT_KEY
ALGORITHM = settings.ALGORITHM
EXPIRE_MIN = 10

async def create_access_token(response: Response,data: dict):
    access_payload = data.copy()
    refresh_payload = data.copy()
    jti = str(uuid7())

    access_expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    access_payload['exp'] = access_expire
    access_payload['jti'] = str(uuid7())
    access_payload['parent'] = jti
    access_payload['refresh'] = False
    access_token = jwt.encode(access_payload,SECRET_KEY,algorithm=ALGORITHM)

    refresh_expire = datetime.now(timezone.utc) + timedelta(days=7)
    refresh_payload['jti'] =  jti
    refresh_payload['exp'] = refresh_expire
    refresh_payload['refresh'] = True
    refresh_token = jwt.encode(refresh_payload,SECRET_KEY,algorithm=ALGORITHM)
    await add_active(jti)
    input: RefreshInput = RefreshInput(user_id=refresh_payload['user_id'],refresh_jti=jti,is_revoked=False,is_used=False,created_at=datetime.now(timezone.utc),expire_at=refresh_expire)
    response.set_cookie(
        key= "refresh_token",
        value= refresh_token,
        httponly= True,
        secure= False,
        samesite= "lax",
        path= "/social/refresh"
    )
    token = Token(access_token=access_token,refresh_token=refresh_token,jti=jti)
    return token,input

async def verify_access_token(token: str, credentials_exception):
    try:
        payload= jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        verify_blacklist =  await check_blacklist(payload.get('parent'))
        if verify_blacklist == True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token is not a good one')
        token_data = TokenData(id=id,jti=payload.get('parent'))
    except InvalidSignatureError:
        raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Token is expired")
    return token_data

async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate credentials', headers={"WWW-Authenticate": "Bearer"})

    return await verify_access_token(token,credentials_exception)

def verify_refresh_token(request: Request,standard_refresh_token: Annotated[str|None , Cookie()] = None):
    refresh_token = request.cookies.get("refresh_token")
    if  not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= 'refresh token not provided')
    payload = {}
    try:
        decoded_token = jwt.decode(refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
        jti = decoded_token.get("jti")
        payload['user_id'] = decoded_token.get("user_id")
        payload['username'] = decoded_token.get("username")
        return payload,jti
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='invalid Token')
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail= 'expired token')