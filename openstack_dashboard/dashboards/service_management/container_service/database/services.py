from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import os.path

Base = declarative_base()
CURRENT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    service_name = Column(String(50))
    container = relationship("Container", back_populates="service",
                             cascade="all, delete, delete-orphan", )

    def __repr__(self):
        return self.id


class Container(Base):
    __tablename__ = 'container'

    id = Column(Integer, primary_key=True)
    container_id = Column(String(50))
    service_id = Column(Integer, ForeignKey('service.id'))

    service = relationship("Service", back_populates="container")

    def __repr__(self):
        return self.id

<<<<<<< HEAD

# Base.metadata.create_all(engine)

=======
>>>>>>> 1b14515af9b233a71a0a2cc0dde2abac4c3591de

engine = create_engine(
    'sqlite:///' + CURRENT_FOLDER_PATH + '/service.sqlite', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.metadata.create_all(engine)


def get_service_list():
    service_list = db_session.query(Service).all()
    return service_list


class DatabaseService:
    def __init__(self):
        self.session = db_session

    def add_service(self, obj):
        self.session.add(obj)
        self.session.commit()

    def get_service_list(self):
        service_list = self.session.query(Service).all()
        return service_list

    def get_containers_in_service(self, service_id):
        container_list = self.session.query(Service). \
            filter(Service.id == service_id).one().container
        return container_list

    def close(self):
        pass
<<<<<<< HEAD

=======
>>>>>>> 1b14515af9b233a71a0a2cc0dde2abac4c3591de

new_db = DatabaseService()
