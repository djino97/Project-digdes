"""
Models module contains a declarative description of the tables
contained in the database SQLite.
"""

from sqlalchemy import *
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlite3 import Connection


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Foreign key support is included at compile time and enabled at run time.
    """

    if isinstance(dbapi_connection, Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# Create,engine and get the metadata
Base = declarative_base()
engine = create_engine('sqlite:///Logistics.db')
metadata = MetaData(bind=engine)


class Supply(Base):
    """
    The "Supply" model contains
    data related to the feature of taking the cargo.
    """

    __tablename__ = 'Supply'
    num_party = Column(Integer, ForeignKey('PartyCargo.num_party'), nullable=False)
    num_truck_departure = Column(Integer, ForeignKey('Truck.num_truck'), primary_key=True)
    id_point = Column(Integer, ForeignKey('Point.id_point'), nullable=False)
    date_departure = Column(DATETIME, nullable=False)
    id_loading = Column(Integer, ForeignKey('Loading.id_loading'), nullable=False)

    num_party_supply = relationship("PartyCargo", backref="num_party_cargo")
    truck_id_supply = relationship("Truck", backref="truck_id_supply")
    id_point_supply = relationship("Point", backref="id_point_supply")
    id_loading_supply = relationship("Loading", backref="id_loading_supply")


class Warehouse(Base):
    """
    The "Warehouse" model contains data related to the storage of the cargo.
    """

    __tablename__ = 'Warehouse'
    id_point = Column(Integer, ForeignKey('Point.id_point'), primary_key=True)
    id_point_warehouse = relationship("Point", backref="id_point_warehouse")


class WarehouseParty(Base):
    """
    If the route passes through the warehouse, then the data for the warehouse is entered.
    """

    __tablename__ = 'WarehouseParty'
    id_point = Column(Integer, ForeignKey('Warehouse.id_point'))
    num_party = Column(Integer, ForeignKey('PartyCargo.num_party'))
    data_arrival = Column(DATETIME, nullable=False)
    data_departure = Column(DATETIME, nullable=False)
    id_loading = Column(Integer, ForeignKey('Loading.id_loading'))
    id_unloading = Column(Integer, ForeignKey('Unloading.id_unloading'))

    id_warehouse = relationship("Warehouse", backref="id_warehouse")
    id_party = relationship("PartyCargo", backref="id_party")
    loading = relationship("Loading", backref="loading")
    unloading = relationship("Unloading", backref="unloading")

    __table_args__ = (PrimaryKeyConstraint(id_point, num_party),)


class Consumption(Base):
    """
    The "Consumption" model contains data related to the
    feature of the transfer of cargo to the consumer
    """

    __tablename__ = 'Consumption'
    num_party = Column(Integer, ForeignKey('PartyCargo.num_party'), nullable=False)
    num_truck_arrival = Column(Integer, ForeignKey('Truck.num_truck'), primary_key=True)
    id_point = Column(Integer, ForeignKey('Point.id_point'), nullable=False)
    date_supply = Column(DATETIME, nullable=False)
    id_unloading = Column(Integer, ForeignKey('Unloading.id_unloading'), nullable=False)

    num_party_consumption = relationship("PartyCargo", backref="num_party_consumption")
    truck_id_consumption = relationship("Truck", backref="truck_id_consumption")
    id_point_consumption = relationship("Point", backref="id_point_consumption")
    id_unloading_consumption = relationship("Unloading", backref="id_unloading_consumption")


class PartyCargo(Base):
    """
    The "PartyCargo" model contains data about the number and weight of cargo.
    """

    __tablename__ = 'PartyCargo'
    num_party = Column(Integer, primary_key=True)
    weight_party = Column(Integer, nullable=False)

    __table_args__ = {'sqlite_autoincrement': True}


class Truck(Base):
    """
    The model "Truck" contains data on all trucks and their tonnage.
    """

    __tablename__ = 'Truck'
    num_truck = Column(Integer, primary_key=True)
    tonnage = Column(Integer, nullable=False)

    __table_args__ = ({'sqlite_autoincrement': True})


class Point(Base):
    """
    The "Point" model contains data on all items shown on the graph.
    """

    __tablename__ = 'Point'
    id_point = Column(Integer, primary_key=True)
    name_point = Column(String(15), nullable=False)
    pos_x_and_y = Column(String(10), nullable=True)

    __table_args__ = ({'sqlite_autoincrement': True})


class NextPoint(Base):
    """
    The "NextPoint" model contains data distance from one point to other points.
    """

    __tablename__ = 'NextPoint'
    id_agent = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    id_point = Column(Integer, ForeignKey('Point.id_point'), nullable=False, )
    id_next_point = Column(Integer, nullable=False)

    id_point_point = relationship("Point", backref="id_point_point", foreign_keys=[id_point])
    __table_args__ = (PrimaryKeyConstraint(id_agent, distance),)


class Route(Base):
    """
    The "Route" model contains a list of points through which the cargo will pass.
    """

    __tablename__ = 'Route'
    id_agent = Column(Integer, primary_key=True)
    distance = Column(Integer, nullable=False)
    num_route = Column(Integer, primary_key=True)
    num_party = Column(Integer, ForeignKey('PartyCargo.num_party'), nullable=False)

    num_party_route = relationship("PartyCargo", backref="num_party_route")

    __table_args__ = (ForeignKeyConstraint(["id_agent", "distance"],
                                           ["NextPoint.id_agent", "NextPoint.distance"], name="fk_route"),)
    entries = relationship(NextPoint, primaryjoin=
                           id_agent == NextPoint.id_agent,
                           foreign_keys=NextPoint.id_agent)
    favorite_entry = relationship(NextPoint,
                                  primaryjoin=
                                  distance == NextPoint.distance,
                                  foreign_keys=NextPoint.distance,
                                  post_update=True)


class Loading(Base):
    """
     The "Loading" model contains information about the time required for loading into the truck
    """

    __tablename__ = 'Loading'
    id_loading = Column(Integer, primary_key=True)
    loading_time = Column(Integer, nullable=False)

    __table_args__ = ({'sqlite_autoincrement': True})


class Unloading(Base):
    """
    The "Unloading" model contains information about the time required for unloading into the truck
    """

    __tablename__ = 'Unloading'
    id_unloading = Column(Integer, primary_key=True)
    unloading_time = Column(Integer, nullable=False)

    __table_args__ = ({'sqlite_autoincrement': True})


Base.metadata.create_all(engine)
