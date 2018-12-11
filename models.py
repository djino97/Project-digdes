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


class Suplly(Base):
    """
    The "Suplly" model contains
    data related to the feature of taking the cargo.
    """

    __tablename__ = 'Suplly'
    Num_party = Column(Integer, ForeignKey('PartyCargo.Num_party'), nullable=False)
    Num_truck_departure = Column(Integer, ForeignKey('Truck.Num_truck'), primary_key=True)
    Name_Point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    Data_departure = Column(DATETIME, nullable=False)
    Id_loading = Column(Integer, ForeignKey('Loading.Id_loading'), nullable=False)
    NumPartySuplly = relationship("PartyCargo", backref="NumPartySuplly")
    TruckIdSuplly = relationship("Truck", backref="TruckIdSuplly")
    NamePointSuplly = relationship("Point", backref="NamePointSuplly")
    IdLoadingSuplly = relationship("Loading", backref="IdLoadingSuplly")


class Warehouse(Base):
    """
    The "Warehouse" model contains data related to the storage of the cargo.
    """

    __tablename__ = 'Warehouse'
    Name_Point = Column(String(15), ForeignKey('Point.Name_point'), primary_key=True)
    Id_loading = Column(Integer, ForeignKey('Loading.Id_loading'), nullable=False)
    Id_unloading = Column(Integer, ForeignKey('Unloading.Id_unloading'), nullable=False)
    NamePointWarehouse = relationship("Point", backref="NamePointWarehouse")
    IdLoadingWarehouse = relationship("Loading", backref="IdLoadingWarehouse")
    IdUnloadingWarehouse = relationship("Unloading", backref="IdUnloadingWarehouse")


class Consumption(Base):
    """
    The "Consumption" model contains data related to the
    feature of the transfer of cargo to the consumer
    """

    __tablename__ = 'Consumption'
    Num_party = Column(Integer, ForeignKey('PartyCargo.Num_party'), nullable=False)
    Num_truck_arrival = Column(Integer, ForeignKey('Truck.Num_truck'), primary_key=True)
    Name_Point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    Data_suplly = Column(DATETIME, nullable=False)
    Id_unloading = Column(Integer, ForeignKey('Unloading.Id_unloading'), nullable=False)
    NumPartyConsumption = relationship("PartyCargo", backref="NumPartyConsumption")
    TruckIdConsumption = relationship("Truck", backref="TruckIdConsumption")
    NamePointConsumption = relationship("Point", backref="NamePointConsumption")
    IdUnloadingConsumption = relationship("Unloading", backref="IdUnloadingConsumption")


class PartyCargo(Base):
    """
    The "PartyCargo" model contains data about the number and weight of cargo.
    """

    __tablename__ = 'PartyCargo'
    Num_party = Column(Integer, primary_key=True)
    Weight_party = Column(Integer, nullable=False)
    NumPartySuplly = relationship("Suplly", backref="NumPartySuplly")
    NumPartyConsumption = relationship("Consumption", backref="NumPartyConsumption")


class Truck(Base):
    """
    The model "Truck" contains data on all trucks and their tonnage.
    """

    __tablename__ = 'Truck'
    Num_truck = Column(Integer, primary_key=True)
    Tonnage = Column(Integer, nullable=False)
    NumTruckSuplly = relationship("Supply", backref="TruckIdSuplly")
    TruckIdConsumption = relationship("Consumption", backref="TruckIdConsumption")


class Point(Base):
    """
    The "Point" model contains data on all items shown on the graph.
    """

    __tablename__ = 'Point'
    Name_point = Column(String(15), primary_key=True)
    NamePointSuplly = relationship("Suplly", backref="NamePointSuplly")
    NamePointWarehouse = relationship("Warehouse", backref="NamePointWarehouse")
    NamePointConsumption = relationship("Consumption", backref="NamePointConsumption")
    NameNamePoint = relationship("NextPoint", backref="NameNamePoint")
    LoadingNamePoint = relationship("Loading", backref="LoadingNamePoint")
    UnloadingNamePoint = relationship("Unloading", backref="UnloadingNamePoint")
    RouteNamePoint = relationship("Route", backref="RouteNamePoint")


class NextPoint(Base):
    """
    The "NextPoint" model contains data distance from one point to other points.
    """

    __tablename__ = 'NextPoint'
    Id_next_point = Column(Integer, nullable=False)
    Distance = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint("Id_next_point", "Distance"),
    )
    Name_point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    Next_name_point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    NamePoint = relationship("Point", backref="NamePoint")
    NextNamePoint = relationship("Point", backref="NextNamePoint")


class Route(Base):
    """
    The "Route" model contains a list of points through which the cargo will pass.
    """

    __tablename__ = 'Route'
    Id_next_point = Column(Integer, nullable=False)
    Distance = Column(Integer, nullable=False)
    Num_cut = Column(Integer, primary_key=True)
    Num_party = Column(Integer, ForeignKey('PartyCargo.Num_party'), primary_key=True)
    __table_args__ = (ForeignKeyConstraint(["Id_next_point", "Distance"],
                                           ["NextPoint.Id_next_point", "NextPoint.Distance"], name="fk_route"),)
    RouteNamePoint = relationship("Point", backref="RouteNamePoint")
    entries = relationship(NextPoint, primaryjoin=
                           Id_next_point == NextPoint.Id_next_point,
                           foreign_keys=NextPoint.Id_next_point)
    favorite_entry = relationship(NextPoint,
                                  primaryjoin=
                                  Distance == NextPoint.Distance,
                                  foreign_keys=NextPoint.Distance,
                                  post_update=True)


class Loading(Base):
    """
     The "Loading" model contains information about the time required for loading into the truck
    """

    __tablename__ = 'Loading'
    Id_loading = Column(Integer, primary_key=True)
    Name_point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    Loading_time = Column(Integer, nullable=False)
    LoadingNamePoint = relationship("Point", backref="LoadingNamePoint")
    IdLoadingSuplly = relationship("Suplly", backref="IdLoadingSuplly")
    IdLoadingWarehouse = relationship("Warehouse", backref="IdLoadingWarehouse")


class Unloading(Base):
    """
    The "Unloading" model contains information about the time required for unloading into the truck
    """

    __tablename__ = 'Unloading'
    Id_unloading = Column(Integer, primary_key=True)
    Name_point = Column(String(15), ForeignKey('Point.Name_point'), nullable=False)
    Unloading_time = Column(Integer, nullable=False)
    UnloadingNamePoint = relationship("Point", backref="UnloadingNamePoint")
    IdUnloadingWarehouse = relationship("Warehouse", backref="IdUnloadingWarehouse")
    IdUnloadingConsumption = relationship("Consumption", backref="IdUnloadingConsumption")


Base.metadata.create_all(engine)
