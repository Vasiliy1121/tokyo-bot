from peewee import SqliteDatabase, Model, IntegerField, TextField, DateTimeField
from config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(unique=True)


class Route(BaseModel):
    user  = IntegerField()          # id пользователя
    name  = TextField()
    itinerary = TextField()
    created_at = DateTimeField()


def init_db() -> None:
    db.connect(reuse_if_open=True)
    db.create_tables([User, Route])
    db.close()
