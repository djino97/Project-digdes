"""
Query module is designed to retrieve data from the database using queries to it.
"""

from sqlalchemy import create_engine
from models import  NextPoint
from sqlalchemy.orm import Session


class QueryPoints(object):
    def go_points(self, session):
        query = session.query(NextPoint.Name_point, NextPoint.Next_name_point, NextPoint.Distance).all()
        return query


def session_create():
    engine = create_engine('sqlite:///database/Logistics.db')
    session = Session(bind=engine)
    try:
        points = QueryPoints().go_points(session)

        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return points
