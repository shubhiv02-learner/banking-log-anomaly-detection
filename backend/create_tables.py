from backend.database import engine
from backend.db_models import Base
from backend.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

Base.metadata.create_all(bind=engine)

logger.info("Database tables created (create_all)")
