import backoff
from bot.handlers.loggers import backoff_loger

logger = backoff_loger()

"""
Base_method - арифметическая прогрессия 
RandomJitter_method - арифметическая прогрессия
                    с добавлением случайного числа милисекунд
FullJitter_method - алгоритм «Full Jitter», определенный в публикации
        «Экспоненциальное отставание и джиттер» в блоге об архитектуре AWS.
"""
JITTER = {
    "Base_method": None,
    "RandomJitter_method": backoff.random_jitter,
    "FullJitter_method": backoff.full_jitter
}


def backoff_hdlr(details):
    tries = details.get("tries")
    wait = float('{:.3f}'.format(details.get("wait")))
    elapsed = float('{:.3f}'.format(details.get("elapsed")))
    logger.error(f'\nDatabase crash:\n'
                 f'{tries} attempt to connect to base\n'
                 f'Wait time {wait}\n'
                 f'Total waiting time {elapsed} seconds'
                 )
