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
    service_name = Column(String)
    container_name = Column(String)
    service_id = Column(Integer)

    def __repr__(self):
        return self.id

    # def __unicode__(self):
    #     return u'%s' % self.container_id
    #
    # def __str__(self):
    #     return '%s' % self.container_id

engine = create_engine('sqlite:///' + CURRENT_FOLDER_PATH + '/service.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)



class Database_service:
    def __init__(self):
        self.session = Session()

    def get_service_id(self):
        max = 0
        for service in self.session.query(Service):
            if service.service_id > max:
                max = service.service_id
        max += 1
        return max

    def add_service(self,service):
        self.session.add(service)
        self.session.commit()

    def close(self):
        self.session.close()
