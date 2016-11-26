from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import os.path

Base = declarative_base()
CURRENT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    service_name = Column(String(50))
    container = relationship("Container", back_populates="service",
                             cascade="all, delete, delete-orphan",)

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

# Service.container = relationship(
#     "Container", order_by=Container.id, back_populates="service")

engine = create_engine(
    'sqlite:///' + CURRENT_FOLDER_PATH + '/service.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


class DatabaseService:

    def __init__(self):
        self.session = Session()

    def add_service(self, obj):
        self.session.add(obj)
        self.session.commit()

    def get_service_list(self):
        service_list = self.session.query(Service).all()
        return service_list

    def get_containers_in_service(self, service_id):
        container_list = self.session.query(Service).\
            filter(Service.id == service_id).one().container
        return container_list

    def close(self):
        self.session.close()


# new_db = DatabaseService()
# service_list = new_db.get_service_list()
# for service in service_list:
#     container_list = new_db.get_containers_in_service(service.id)
#     for container in container_list:
#         print(container.container_id)
