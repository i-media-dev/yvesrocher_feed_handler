import logging
from pathlib import Path

from handler.exceptions import DirectoryCreationError, EmptyFeedsListError
from handler.logging_config import setup_logging

# from handler.feeds_handler import FeedHandler
# from handler.feeds_save import FeedSaver

setup_logging()


def get_filenames_list(folder_name: str) -> list[str]:
    """Функция, возвращает список названий фидов."""
    folder_path = Path(__file__).parent.parent / folder_name
    if not folder_path.exists():
        logging.error('Папка %s не существует', folder_name)
        raise DirectoryCreationError('Папка %s не найдена', folder_name)
    files_names = [
        file.name for file in folder_path.iterdir() if file.is_file()
    ]
    if not files_names:
        logging.error('В папке нет файлов')
        raise EmptyFeedsListError('Нет скачанных файлов')
    logging.debug('Найдены файлы: %s', files_names)
    return files_names
