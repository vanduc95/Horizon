import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


def create_database():
    engine = create_engine('sqlite:///'+FOLDER_PATH+'/data.db', echo=True)
    Base.metadata.create_all(engine)


class DockerHost(Base):
    __tablename__ = 'DOCKER_HOST'
    id = Column(Integer, primary_key=True)
    host_name = Column(String)
    host_url = Column(String, unique=True)


class DataService:
    def __init__(self):
        engine = create_engine('sqlite:///' + FOLDER_PATH + '/data.db', echo=True)
        self.session = scoped_session(sessionmaker(bind=engine))

    def add_host(self, host):
        self.session.add(host)
        self.session.commit()

    def query_host_by_name(self, host_name):
        return self.session.query(DockerHost).filter_by(host_name=host_name).first()


create_database()
# new_host = DockerHost(host_name="host-manager_1", host_url="192.168.50.1")
# db_service = DataService()
# db_service.add_host(new_host)
# db_service = DataService()
# query_host = db_service.query_host_by_name("dds")
# print (query_host)
