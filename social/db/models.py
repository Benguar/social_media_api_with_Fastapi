from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship #mapped helps us to specify columns in our table and their datatype Mapped_column helps us add extra attribute to our table column such as Primary key nullable etc.
from sqlalchemy import ForeignKey,func,DateTime
from social.db.connection import engine
from datetime import datetime
import asyncio
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_table"
    id:Mapped[int] = mapped_column(primary_key= True,nullable= False)
    username:Mapped[str] = mapped_column(nullable=False,unique=True)
    email: Mapped[str] = mapped_column(nullable=False,unique=True)
    password:Mapped[str] = mapped_column(nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


    #this is a one to many relationship with Posts that is one user to many posts
    posts:Mapped[list["Posts"]] = relationship(back_populates='user')
    likes:Mapped[list["Likes"]] = relationship(back_populates="user") 
    # The Posts class is wrapped inside a list because it is a one to many relationship we are going to be having many posts. back populates helps complete the handshake between both tables it goes to the posts table to check for the variable user if it does exist to complete the synchronization both tables needs to be synchronized on can not be backpopulated without the other 

    # def __repr__(self) -> str:
    #     return f'user: Username={self.username}'

class Posts(Base):
    __tablename__ = "posts_table"
    id:Mapped[int] = mapped_column(primary_key=True, nullable=False)
    posts:Mapped[str] = mapped_column(nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey('user_table.id', ondelete= "CASCADE"), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())



    #this is a many to one relationship with users  that is many posts to one user
    user:Mapped["User"] = relationship(back_populates='posts')
    likes: Mapped[list["Likes"]] =  relationship(back_populates="post")
    # back populates helps complete the handshake between both tables it goes to the users table to check for the variable user if it does exist to complete the synchronization both tables needs to be synchronized on can not be backpopulated without the other 

    # def __repr__(self) -> str:
    #     return f'Post  Content= {self.posts} by {self.user.username}'

class Likes(Base):
    __tablename__ = "likes_table"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts_table.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key= True)


    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Posts"] = relationship(back_populates="likes")

class Refresh(Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id", ondelete="CASCADE"),nullable=False)
    refresh_jti: Mapped[str] = mapped_column(primary_key=True,nullable=False)
    is_revoked: Mapped[bool] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    expire_at: Mapped[datetime] = mapped_column(nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    ip: Mapped[str] = mapped_column(nullable=True) #this is set to true because we cant get a real IP yet the APi is not yet deployed

#The relationship and Back populates does not affect the database it is just a way to make it easier for python to make both user and posts talk to each other well so each Posts are attached to its user and each User is attached to its post

#Foreignkey affects the database it is a way okay validating the user inputted is a valid user. it maps the id inputted in posts_table to the user ID in the user table so if the ID is not in the user_table, it throws an error. e.g if when creating a post a user ID 10 is inputted and there is no user with an ID of 10 in user_table and the user does not exist it throws an error so the user_id is not just a column it is a validator used to establish relationship with another table in same database in postgres. Also, it makes editing easier. for example if a user wit ID of 5 is deleted, it is easier to delete all the posts associated with the user's ID with just a command. NB: A relationship and back_populates can not work with a foreign key acting aa a bridge between them


#to create the Tables in Database

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Base.metadata.create_all(bind=engine) #this creates all the tables in the database the bind=engine connects the tables with the database