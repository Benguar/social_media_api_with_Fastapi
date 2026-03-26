from fastapi import FastAPI
from social.src import users,posts,auth,like
from contextlib import asynccontextmanager
from social.db.models import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
version = "v1"

app = FastAPI(
    version= version,
    lifespan=lifespan
)

app.include_router(users.route, prefix= f"/social/users/{version}",tags=["Users"])
app.include_router(posts.route, prefix= f"/social/posts/{version}",tags=["Posts"])
app.include_router(auth.route,prefix=f"/social",tags=["login"])
app.include_router(like.route,prefix=f'/social/like/{version}', tags=["like"])

# pip install pyJWT -> library used to create JWT tokens
#pip install argon2-cffi -> for argon2