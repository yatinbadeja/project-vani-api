from motor.motor_asyncio import AsyncIOMotorClient

from app.database.connections.db_abs import Database


class MongoDB(Database):
    client: AsyncIOMotorClient = None  # type: ignore

    def init_connection(self, uri):
        self.client = AsyncIOMotorClient(
            str(uri),
        )
        return self.client
