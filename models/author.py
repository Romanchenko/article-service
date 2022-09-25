import uuid
import datetime


class Author:
    def __init__(self, surname, name=''):
        self._id = uuid.uuid4()
        self.surname = surname
        self.name = name
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
