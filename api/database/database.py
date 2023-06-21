from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from api import fastapi_config

# Create a connection to the database
db_url = fastapi_config.SQLALCHEMY_DATABASE_URI
engine = create_engine(db_url, echo=True)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Creating a base class of models
Base = declarative_base()
