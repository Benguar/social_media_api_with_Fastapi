import redis.asyncio as aioredis
from social.db.settings import settings


#token_blacklist is for access tokens when logged out
#token_active is for refresh tokens that has not been used
token_blacklist = aioredis.StrictRedis(
    host= settings.redis_host,
    port= settings.redis_port,
    db=0,
    decode_responses= True
)
token_active = aioredis.StrictRedis(
    host= settings.redis_host,
    port= settings.redis_port,
    db=1,
    decode_responses=True
)

async def add_blacklist(jti: str) -> None:
    await token_blacklist.set(
        name=jti,
        value="blacklisted",
        ex= 600
    )

async def check_blacklist(jti: str):
    jti = await token_blacklist.get(name=jti)
    return jti

async def add_active(jti: str):
    await token_active.set(
        name= jti,
        value= "active",
        ex= 604800
    )
async def remove_active(jti: str):
    exists = await token_active.delete(jti)
    return exists