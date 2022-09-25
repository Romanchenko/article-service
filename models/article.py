import datetime
import uuid
from typing import List


class Article:
    def __init__(self, title: str, authors: List[uuid.UUID], year, conference='',
                 abstract='', references: List[uuid.UUID] = []):
        self._id = uuid.uuid4()
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.conference = conference
        self.year = year
        self.references = references
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
