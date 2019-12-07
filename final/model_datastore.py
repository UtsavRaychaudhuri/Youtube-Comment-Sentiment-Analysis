from .Model import Model
from datetime import datetime
from google.cloud import datastore

def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        [ name, address, city, state, zipcode, message ]
    where name, address, city, state, zipcode, and message are Python strings
    and where date is a Python datetime
    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()
    return [entity['name'],entity['blob_name'],entity['image_public_url'],entity['angry'],entity['joy'],entity['suprise'],entity['timestamp']]

class model(Model):
    def __init__(self):
        self.client = datastore.Client('cs430-nishna-aleti')

    def select(self):
        query = self.client.query(kind = 'faces')
        entities = list(map(from_datastore,query.fetch()))
        return entities

    def insert(self, name, address, city, state, zipcode, message):
        key = self.client.key('view')
        rev = datastore.Entity(key)
        rev.update( {
            'name': name,
            'image_public_url' : image_public_url,
			'blob_name' : blob_name,
			'state': state,
			'zipcode':zipcode,
			'signed_on':date.today(),
            'message' : message
            })
        self.client.put(rev)
        return True

