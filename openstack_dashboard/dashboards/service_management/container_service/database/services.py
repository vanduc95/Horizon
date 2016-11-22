from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import sessionmaker, scoped_session
import os.path

Base = declarative_base()
CURRENT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


class Service(Base):
    __tablename__ = 'Service'

    id = Column(Integer, primary_key=True)
    container_id = Column(String)
    service_id = Column(String)

    def __repr__(self):
        return self.id


engine = create_engine('sqlite:///' + CURRENT_FOLDER_PATH + '/database/service.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

# class DatabaseService:
#     def __init__(self):
#         self.session = Session()
#
#     def get_list_service(self):
#         list_service = self.session.query(Service.service_id)
#         return list_service
#
#     def close(self):
#         self.session.close()
