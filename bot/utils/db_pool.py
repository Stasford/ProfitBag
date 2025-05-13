import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self.session_factory = None
        self.initialized = False

    def initialize(self, session_factory):
        """Инициализация фабрики сессий."""
        self.session_factory = session_factory
        self.initialized = True
        logger.info("DatabasePool has been initialized successfully")

    def get_session(self):
        """Возвращает фабрику сессий для создания новых сессий."""
        if not self.initialized:
            logger.error("DatabasePool is not initialized!")
            return None
        return self.session_factory

# Создаем глобальный экземпляр класса
db = DatabasePool()
