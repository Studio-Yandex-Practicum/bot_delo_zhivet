import backoff
from bot.handlers.loggers import get_logger

logger = get_logger()


def backoff_hdlr(details):
    tries = details.get("tries")
    wait = float('{:.3f}'.format(details.get("wait")))
    elapsed = float('{:.3f}'.format(details.get("elapsed")))
    # logger.error("Error detected, %s attempt to connect to base", details.get("tries"))
    # logger.error(f'Error detected:\n'
    #              f'{tries} attempt to connect to base\n'
    #              f'Wait time {wait}\n'
    #              f'Total waiting time {elapsed} seconds'
    #              )
    print(f'Error detected:\n'
          f'Connection attempt number: {tries}\n'
          f'Wait time: {wait}\n'
          f'Total waiting time: {elapsed} seconds'
          )


'''  
@backoff.on_exception(backoff.expo,
                      exception=Exception,
                      on_backoff=backoff_hdlr,
                      max_tries=10,
                      max_time=60,
                      )
'''
