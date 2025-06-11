from peewee import *

db = SqliteDatabase('routes.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)

class Route(BaseModel):
    user = ForeignKeyField(User, backref='routes')
    name = CharField()
    itinerary = TextField()
    created_at = DateTimeField()

def initialize_db():
    db.connect()
    db.create_tables([User, Route])
    db.close()
