import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

HOST = os.environ.get("REDIS_HOST")
PORT = os.environ.get("REDIS_PORT")
DB_ID = os.environ.get("REDIS_DB")
