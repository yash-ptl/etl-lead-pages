
from datetime import datetime
from dateutil import tz

def transform_animal(animal):
    """
    Implementation of Data Transformation
    """
    animal['friends'] = animal['friends'].split(",") if animal.get('friends') else []
    if animal.get('born_at'):
        dt = datetime.utcfromtimestamp(animal['born_at'] / 1000).replace(tzinfo=tz.UTC)
        animal['born_at'] = dt.isoformat()
    return animal