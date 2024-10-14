from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class City(Base):
    __tablename__ = 'cities'

    name = Column(String)
    name_ascii = Column(String)
    state_id = Column(String)
    state_name = Column(String)
    county_fips = Column(String)
    county_name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    incorporated = Column(Boolean)
    timezone = Column(String)
    ranking = Column(Integer)
    id = Column(String, primary_key=True)

    def __repr__(self):
        return f"<City(name='{self.name}', state='{self.state_id}', latitude={self.lat}, longitude={self.lng})>"
