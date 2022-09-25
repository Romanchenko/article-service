import datetime
import hashlib
import uuid


class User:
    def __init__(self, login, password):
        self._id = uuid.uuid4()
        self.login = login
        self.password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
