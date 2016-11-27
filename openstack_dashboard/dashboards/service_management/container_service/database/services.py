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


# Base.metadata.create_all(engine)


engine = create_engine(
    'sqlite:///' + CURRENT_FOLDER_PATH + '/service.sqlite', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


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


new_db = DatabaseService()
# service_list = new_db.get_service_list()
# for service in service_list:
#     container_list = new_db.get_containers_in_service(service.id)
#     for container in container_list:
#         print(container.container_id)

# new_db = DatabaseService()
# new_service = Service(service_name='4123')
# new_db.session.add(new_service)
# new_db.session.commit()
# new_ctn_1 = Container(container_id='21321')
# new_ctn_2 = Container(container_id='12313')
# new_service.container = [new_ctn_1, new_ctn_2]
# new_db.session.commit()
# print(new_service.id)
# delete_service = new_db.session.query(
#     Service).filter(Service.id == '3').first()
# container_delete_list = delete_service.container

# new_db.session.delete(delete_service)
# for container in container_delete_list:
#     new_db.session.delete(container)
# new_db.session.commit()
