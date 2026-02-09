import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://api.ba-la.ru/'
"""Домен API для удаления фона."""

ADDRESS_FTP_IMAGES = 'https://feeds.i-media.ru/projects/yvesrocher/new_images'
"""Адрес директории на ftp для изображений."""

ATTEMPTION_LOAD_FEED = 3
"""Попытки для скачивания фида."""

DELAY_FOR_RETRY = (5, 15, 30)
"""Задержки между переподключениями."""

DATE_FORMAT = '%Y-%m-%d'
"""Формат даты по умолчанию."""

TIME_FORMAT = '%H:%M:%S'
"""Формат времени по умолчанию."""

PROTOCOL = 'https'
"""Протокол запроса."""

ADDRESS = 'projects/uvi/new_images'
"""Путь к файлу."""

DOMEN_FTP = 'feeds.i-media.ru'
"""Домен FTP-сервера."""

RGB_COLOR_SETTINGS = (255, 255, 255)
"""Цвет RGB холста."""

RGBA_COLOR_SETTINGS = (0, 0, 0, 0)
"""Цвет RGBA холста."""

NUMBER_PIXELS_CANVAS = 40
"""Количество пикселей для подгонки холста."""

NUMBER_PIXELS_IMAGE = 200
"""Количество пикселей для подгонки изображения."""

NAME_OF_SHOP = 'furure'
"""Константа названия магазина."""

NAME_OF_FRAME = 'canvas.png'

FRAME_FOLDER = os.getenv('FRAME_FOLDER', 'frame')
"""Константа стокового названия директории c рамкой"""

FEEDS_FOLDER = os.getenv('FEEDS_FOLDER', 'temp_feeds')
"""Константа стокового названия директории с фидами."""

NEW_FEEDS_FOLDER = os.getenv('NEW_FEEDS_FOLDER', 'new_feeds')
"""Константа стокового названия директории с измененными фидами."""

IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', 'old_images')
"""Константа стокового названия директории с изображениями."""

NEW_IMAGE_FOLDER = os.getenv('NEW_IMAGE_FOLDER', 'new_images')
"""Константа стокового названия директории измененных изображений."""

ENCODING = 'utf-8'
"""Кодировка по умолчанию."""

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.yves-rocher.ru/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}
