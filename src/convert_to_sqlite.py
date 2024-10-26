from typing import Any, Dict
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session
from pandas import read_csv, DataFrame

from geolocator.models.city import City, Base

SQL_FILE = "geolocator.db"
CSV_FILE = "uscities.csv"


def create_database_file() -> Engine:
    """Create a new SQLite database file if it doesn't exist"""
    engine = create_engine(f"sqlite:///{SQL_FILE}")
    Base.metadata.create_all(engine)
    return engine


def load_csv_data() -> DataFrame:
    """Load the city data from the CSV file

    Returns:
        DataFrame: The city data from the CSV file
    """
    return read_csv(CSV_FILE)


def format_csv_data(data: DataFrame) -> DataFrame:
    """Format the city data from the CSV file. This function will rename
    the city and city_ascii columns and convert the lat, lng, ranking, and population
    columns to the correct data types.

    Args:
        data (DataFrame): _description_

    Returns:
        DataFrame: _description_
    """
    column_names_to_change = [
        ("city", "name"),
        ("city_ascii", "name_ascii"),
    ]

    values_to_change = {
        "lat": lambda x: float(x),
        "lng": lambda x: float(x),
        "ranking": lambda x: int(x),
        "population": lambda x: int(x),
        "density": lambda x: float(x),
    }

    # Rename columns
    data = data.rename(columns=dict(column_names_to_change))

    # Change values
    for column, func in values_to_change.items():
        data[column] = data[column].apply(func)

    return data


def create_or_update_city(city: Dict[str, Any]) -> City:
    """Create or update a City object from the given dictionary

    Args:
        city (Dict[str, Any]): The city data

    Returns:
        City: The City object
    """
    city_obj = City(
        id=city["id"],
        name=city["name"],
        name_ascii=city["name_ascii"],
        state_id=city["state_id"],
        state_name=city["state_name"],
        county_fips=city["county_fips"],
        county_name=city["county_name"],
        lat=city["lat"],
        lng=city["lng"],
        incorporated=city["incorporated"],
        timezone=city["timezone"],
        ranking=city["ranking"],
    )

    return city_obj


def main():
    """Main function to convert the CSV data containing all
    the GPS data for all cities in the US to an SQLite database
    """
    engine = create_database_file()
    data = load_csv_data()
    data = format_csv_data(data)

    with Session(engine) as session:
        for _, city in data.iterrows():
            db_city = create_or_update_city(city)

            if not db_city.incorporated:
                continue

            session.merge(db_city)

        session.commit()


if __name__ == "__main__":
    main()
