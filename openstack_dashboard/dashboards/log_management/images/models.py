


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import sessionmaker
import os.path


Base = declarative_base()
CURRENT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_FOLDER_PATH, os.pardir))
GRANDER_PARENT_PATH = os.path.abspath(os.path.join(PARENT_PATH, os.pardir))
# print CURRENT_FOLDER_PATH


class DockerHost(Base):
    __tablename__ = 'DockerHost'

    id=Column(Integer,primary_key=True)
    host_url = Column(String)
    host_port = Column(String)

    def __repr__(self):
        return self.id


class DockerFile(Base):
    __tablename__ = "DockerFile"

    id = Column(Integer,primary_key=True)
    content = Column(String)

    def __repr__(self):
        return self.id


engine = create_engine('sqlite:///'+GRANDER_PARENT_PATH+'/docker_management/database/image.db',echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def create_session():
    session = Session()
    return session

