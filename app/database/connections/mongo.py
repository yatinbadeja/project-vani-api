from motor.motor_asyncio import AsyncIOMotorClient

from app.database.connections.db_abs import Database
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MongoDB(Database):
    client: AsyncIOMotorClient = None  # type: ignore

    def init_connection(self, uri):
        try:
            logger.info(f"Attempting to connect to MongoDB at {uri}...")
            self.client = AsyncIOMotorClient(
                str(uri),
            )

            # Test connection by pinging the database
            logger.info("Ping MongoDB to verify connection...")
            self.client.admin.command('ping')
            logger.info("MongoDB connection successful!")
            
            return self.client
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise e  # Re-raise the exception for further handling
