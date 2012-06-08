import logging
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import String, MetaData, Sequence
from sqlalchemy import Table
from sqlalchemy import Integer
from sqlalchemy import types
from sqlalchemy import Column
from datetime import datetime
from sqlalchemy.orm import mapper

metadata = MetaData()

phantom_user_pass_table = Table('phantom_user_pass', metadata,
    Column('column_id', Integer, Sequence('launch_configuration_id_seq'), primary_key=True),
    Column('displayname', String(128), nullable=False, unique=True),
    Column('access_key', String(128), nullable=False, unique=True),
    Column('access_secret', String(128), nullable=False),
    Column('CreatedTime', types.TIMESTAMP(), default=datetime.now()),
    )

def phantom_get_default_key_name():
    return "phantomkey"


class PhantomUserDBObject(object):
    def __init__(self):
        pass

mapper(PhantomUserDBObject, phantom_user_pass_table)

class PhantomSQL(object):

    def __init__(self, dburl):
        self._engine = sqlalchemy.create_engine(dburl)
        metadata.create_all(self._engine)
        self._SessionX = sessionmaker(bind=self._engine)
        self._Session = self._SessionX()

    def _lookup_user(self, access_key):
        q = self._Session.query(PhantomUserDBObject)
        q = q.filter(PhantomUserDBObject.access_key==access_key)
        db_obj = q.first()
        return db_obj

    def get_user_object_by_access_id(self, access_id):
        db_obj = self._lookup_user(access_id)
        if not db_obj:
            return None
        return db_obj

    def get_user_object_by_display_name(self, display_name):
        q = self._Session.query(PhantomUserDBObject)
        q = q.filter(PhantomUserDBObject.displayname==display_name)
        db_obj = q.first()
        if not db_obj:
            return None
        return db_obj

    def add_alter_user(self, displayname, access_key, access_secret):
        db_obj = self._lookup_user(access_key)
        if not db_obj:
            db_obj = PhantomUserDBObject()
            db_obj.access_key = access_key
        db_obj.access_secret = access_secret
        db_obj.displayname = displayname
        self._Session.add(db_obj)

    def remove_user(self, access_key):
        db_obj = self._lookup_user(access_key)
        if not db_obj:
            return False
        self._Session.delete(db_obj)
        return True

    def commit(self):
        self._Session.commit()

    def add_user(self, displayname, access_id, access_secret):
        self.add_alter_user(displayname, access_id, access_secret)
        self.commit()

    def close(self):
        self._Session.close()
    
