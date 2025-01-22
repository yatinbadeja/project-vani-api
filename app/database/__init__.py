from app.Config import ENV_PROJECT
from app.database.connections.mongo import MongoDB

mongodb: MongoDB = MongoDB()
mongodb.init_connection(ENV_PROJECT.MONGO_URI)


class Clients:
    mongodb = mongodb.client


