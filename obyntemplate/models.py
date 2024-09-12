from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base
from obynutils.setup_database import Base

class ExampleModel(Base):
    __tablename__ = 'example_model'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
class GuildModel(Base):
    __tablename__ = 'template_guild'
    
    guild_id = Column(BigInteger, primary_key=True)
    prefix = Column(String, default="!")
    welcome_channel = Column(BigInteger)
    welcome_message = Column(String)