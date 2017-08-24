from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from plugins.generic import GenericTable
from env import logger
import json

engine = create_engine('sqlite:///main.db', echo=True)

session = sessionmaker(bind=engine)
session = session()

for instance in session.query(GenericTable):
    print(json.dumps(instance.sourceIP))
