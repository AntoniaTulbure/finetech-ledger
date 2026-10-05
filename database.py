from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#path to SQL databse file
SQLALCHEMY_DATABASE_URL="sqlite:///./ledger.db"

#database engine
engine= create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

 #SessionLocal class for database sessions
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

#base class for defining SQL models
Base= declarative_base()

#helper function  for getting a database session for API requests
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
