import functools
import json
import logging
import random
import time
from datetime import datetime as dt
from http.client import IncompleteRead

import requests

from handler.constants import (ATTEMPTION_LOAD_FEED, DATE_FORMAT,
                               DELAY_FOR_RETRY, TIME_FORMAT)
from handler.exceptions import (DirectoryCreationError, EmptyFeedsListError,
                                GetTreeError, StructureXMLError)
from handler.logging_config import setup_logging

setup_logging()


def time_of_script(func):
    """Универсальный декоратор для логирования выполнения."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_ts = time.time()
        date_str = dt.now().strftime(DATE_FORMAT)

        print(
            f'Функция {func.__name__} начала работу '
            f'{date_str} в {dt.now().strftime(TIME_FORMAT)}'
        )

        status = 'SUCCESS'
        error_type = error_message = None

        try:
            return func(*args, **kwargs)

        except Exception as error:
            status = 'ERROR'
            error_type = type(error).__name__
            error_message = str(error)
            raise

        finally:
            exec_time_sec = round(time.time() - start_ts, 3)

            print(
                f'Функция {func.__name__} завершила работу '
                f'в {dt.now().strftime(TIME_FORMAT)}. '
                f'Время выполнения — {round(exec_time_sec / 60, 2)} мин.'
            )

            log_record = {
                "DATE": date_str,
                "STATUS": status,
                "FUNCTION_NAME": func.__name__,
                "EXECUTION_TIME": exec_time_sec,
                "ERROR_TYPE": error_type,
                "ERROR_MESSAGE": error_message,
                "ENDLOGGING": 1
            }

            logging.info(json.dumps(log_record, ensure_ascii=False))

    return wrapper


def time_of_function(func):
    """
    Декоратор для измерения времени выполнения функции.

    Замеряет время выполнения декорируемой функции и логирует результат
    в секундах и минутах. Время округляется до 3 знаков после запятой
    для секунд и до 2 знаков для минут.

    Args:
        func (callable): Декорируемая функция, время выполнения которой
        нужно измерить.

    Returns:
        callable: Обёрнутая функция с добавленной функциональностью
        замера времени.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = round(time.time() - start_time, 3)
        logging.info(
            f'Функция {func.__name__} завершила работу. '
            f'Время выполнения - {execution_time} сек. '
            f'или {round(execution_time / 60, 2)} мин.'
        )
        return result
    return wrapper


def retry_on_network_error(
    max_attempts=ATTEMPTION_LOAD_FEED,
    delays=DELAY_FOR_RETRY
):
    """Декоратор для повторных попыток скачивания при сетевых ошибках."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt < max_attempts:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except (
                    IncompleteRead,
                    ConnectionResetError,
                    ConnectionError,
                    ConnectionAbortedError,
                    ConnectionRefusedError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.RequestException
                ) as error:
                    last_exception = error
                    if attempt < max_attempts:
                        delay = delays[attempt - 1] if attempt - \
                            1 < len(delays) else delays[-1]
                        logging.warning(
                            'Попытка %s/%s неудачна, повтор через %s сек: %s',
                            attempt,
                            max_attempts,
                            delay,
                            error
                        )
                        time.sleep(delay)
                    else:
                        logging.error('Все %s попыток неудачны', max_attempts)
                        raise last_exception
            return None
        return wrapper
    return decorator


def try_except(func):
    """Декоратор для обработки исключений."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StructureXMLError:
            logging.warning(
                'Тег пуст или структура фида не соответствует ожидаемой.'
            )
            if func.__annotations__.get('return') == bool:
                return False
            raise
        except (EmptyFeedsListError, GetTreeError, DirectoryCreationError):
            logging.error(f'Критическая ошибка в методе {func.__name__}')
            raise
        except Exception as e:
            logging.error(f'Возникла ошибка в методе {func.__name__}: {e}')
            if func.__annotations__.get('return') == bool:
                return False
            raise
    return wrapper


def retry_photoroom(
    max_attempts: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
):
    """
    Retry специально для PhotoRoom API:
    - retry при сетевых ошибках
    - retry при HTTP 429 и 5xx
    - exponential backoff + jitter
    """

    retry_http_codes = {429, 500, 502, 503, 504}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except requests.exceptions.HTTPError as error:
                    status = error.response.status_code

                    if status not in retry_http_codes:
                        raise

                    reason = f'HTTP {status}'

                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    ConnectionResetError,
                    ConnectionAbortedError,
                ) as error:
                    reason = type(error).__name__

                if attempt == max_attempts:
                    logging.error(
                        'PhotoRoom так и не ответил после %s попыток',
                        max_attempts,
                    )
                    raise

                delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                jitter = random.uniform(0.5, 1.5)
                delay *= jitter

                logging.warning(
                    'PhotoRoom ошибка (%s). '
                    'Попытка %s/%s с задержкой %.1f сек',
                    reason,
                    attempt,
                    max_attempts,
                    delay,
                )

                time.sleep(delay)

        return wrapper
    return decorator
