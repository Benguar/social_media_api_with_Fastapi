# sql imports
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from social.db.settings import settings


url = settings.url
engine = create_async_engine(url)


#A session is a buffer that holds all the information input by the client(user) each request creates a special session and when we commit we are telling the session to handover the data to the database

AsyncSessionLocal = async_sessionmaker(bind=engine, #this connects the session to the database remember our engine is te database connection
                            autoflush=False, 
                            autocommit=False #This ensures the session does not send data to our database unless we are ready
                            )


# This is the "Supplier" function. This handles creating and closing sessions asynchronously
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
