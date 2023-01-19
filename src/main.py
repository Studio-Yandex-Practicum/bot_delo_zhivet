import logging

from bot.application import start_bot

# Logging бота активируется при инициализации logger в main.py
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    start_bot()
