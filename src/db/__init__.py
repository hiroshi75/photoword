from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Create the SQLAlchemy base class
Base = declarative_base()

# Create engine and session factory
engine = create_engine("sqlite:///photoword.db")
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
