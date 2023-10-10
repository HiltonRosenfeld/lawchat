from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection

import os
from dotenv import load_dotenv

load_dotenv()

ASTRA_DB_KEYSPACE = os.environ['ASTRA_DB_KEYSPACE']
ASTRA_DB_SECURE_BUNDLE_PATH = os.environ['ASTRA_DB_SECURE_BUNDLE_PATH']
ASTRA_DB_APPLICATION_TOKEN = os.environ['ASTRA_DB_APPLICATION_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']


def getCluster():
    # Create a Cluster instance to connect to Astra DB.
    # Uses the secure-connect-bundle and the connection secrets.
    cloud_config = {"secure_connect_bundle": ASTRA_DB_SECURE_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider("token", ASTRA_DB_APPLICATION_TOKEN)
    return Cluster(cloud=cloud_config, auth_provider=auth_provider)


def get_astra():
    cluster = getCluster()
    astraSession = cluster.connect()
    return astraSession, ASTRA_DB_KEYSPACE


def initSession():
    """
    Create the DB session and return it to the caller.
    Most important, the session is also set as default and made available
    to the object mapper through global settings. I.e., no need to actually
    do anything with the return value of this function.
    """
    cluster = getCluster()
    session = cluster.connect()
    session.set_keyspace("lawchat")
    connection.register_connection("my-astra-session", session=session)
    connection.set_default_connection("my-astra-session")
    return connection


#if __name__ == "__main__":
#    initSession()


