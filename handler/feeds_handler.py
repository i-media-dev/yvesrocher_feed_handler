import logging
import xml.etree.ElementTree as ET

from handler.constants import (ADDRESS_FTP_IMAGES, FEEDS_FOLDER,
                               NEW_FEEDS_FOLDER, NEW_IMAGE_FOLDER)
from handler.decorators import time_of_function, try_except
from handler.feeds import FEEDS
from handler.logging_config import setup_logging
from handler.mixins import FileMixin

setup_logging()
logger = logging.getLogger(__name__)


class FeedHandler(FileMixin):
    """
    Класс, предоставляющий интерфейс
    для обработки xml-файлов.
    """

    def __init__(
        self,
        filename: str,
        feeds_folder: str = FEEDS_FOLDER,
        new_feeds_folder: str = NEW_FEEDS_FOLDER,
        new_image_folder: str = NEW_IMAGE_FOLDER,
        feeds_list: tuple[str, ...] = FEEDS
    ) -> None:
        self.filename = filename
        self.feeds_folder = feeds_folder
        self.new_feeds_folder = new_feeds_folder
        self.feeds_list = feeds_list
        self.new_image_folder = new_image_folder
        self._root = None
        self._is_modified = False

    @property
    def root(self):
        """Ленивая загрузка корневого элемента."""
        if self._root is None:
            self._root = self._get_root(self.filename, self.feeds_folder)
        return self._root

    @time_of_function
    def replace_images(self):
        """Метод, подставляющий в фиды новые изображения."""
        deleted_images = 0
        input_images = 0
        try:
            image_dict = self._get_files_dict(self.new_image_folder)

            offers = self.root.findall('.//offer')
            for offer in offers:
                offer_id = offer.get('id')
                if not offer_id:
                    continue

                if offer_id in image_dict:
                    pictures = offer.findall('picture')
                    for picture in pictures:
                        offer.remove(picture)
                    deleted_images += len(pictures)

                    picture_tag = ET.SubElement(offer, 'picture')
                    picture_tag.text = (
                        f'{ADDRESS_FTP_IMAGES}/{image_dict[offer_id]}'
                    )
                    input_images += 1
                    self._is_modified = True
            logging.info(
                '\nКоличество удаленных изображений - %s'
                '\nКоличество добавленных изображений - %s',
                deleted_images,
                input_images
            )
            return self
        except Exception as error:
            logging.error('Ошибка в image_replacement: %s', error)
            raise

    def delete_offers(self):
        deleted_offers = 0
        to_remove = []
        try:
            offers_parent = self.root.find('.//offers')
            if offers_parent is None:
                logging.error('Не найден родительский элемент offers')
                return self
            offers = offers_parent.findall('offer')
            for offer in offers:
                category_id = int(offer.findtext('categoryId'))
                if category_id == 0:
                    to_remove.append(offer)
                    deleted_offers += 1
            for offer in to_remove:
                offers_parent.remove(offer)
            logging.info(
                'Удалено %s офферов с categoryId == 0',
                deleted_offers
            )
            return self
        except Exception as error:
            logging.error('Неизвестная ошибка в delete_offers: %s', error)
            raise

    def save(self, prefix: str = 'new'):
        """Метод сохраняет файл, если были изменения."""
        try:
            new_filename = f'{prefix}_{self.filename}'

            if not self._is_modified:
                self._save_xml(self.root, self.new_feeds_folder, new_filename)
                logger.info('Файл обновлен без изменений')
                return self

            self._save_xml(self.root, self.new_feeds_folder, new_filename)
            logger.info('Файл сохранён как %s', new_filename)

            self._is_modified = False
            return self
        except Exception as error:
            logging.error(
                'Неожиданная ошибка при сохранении файла %s: %s',
                self.filename,
                error
            )
            raise
