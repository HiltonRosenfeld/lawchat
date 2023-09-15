import os
from dotenv import load_dotenv


class Settings():
    load_dotenv()
    ASTRA_DB_KEYSPACE = os.environ['ASTRA_DB_KEYSPACE']
    ASTRA_DB_SECURE_BUNDLE_PATH = os.environ['ASTRA_DB_SECURE_BUNDLE_PATH']
    ASTRA_DB_APPLICATION_TOKEN = os.environ['ASTRA_DB_APPLICATION_TOKEN']
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
