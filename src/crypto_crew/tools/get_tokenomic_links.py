### src/crypto_crew/tools/get_tokenomic_links.py

from crewai_tools import BaseTool
import os
import requests
import json
from dotenv import load_dotenv
import logging  # Добавлено импортирование logging
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GetDropstabTokenomicLinks(BaseTool):
    name: str = 'get dropstab tokenomic links'
    description: str = 'Получает ссылки на tokenomic данные Dropstab'

    def _run(self, token_name: str) -> str:
        """
        Получает ссылку на tokenomic данные Dropstab.

        Args:
            token_name (str): Название токена.

        Returns:
            str: Ссылка на Dropstab.
        """
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": f"dropstab {token_name}"})
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            logger.info(f"Запрос к {url} с параметрами: {payload}")
            response.raise_for_status()
            response_data = response.json()

            organic = response_data.get('organic', [])
            if not organic:
                logger.warning("Нет результатов в секции 'organic'")
                raise ValueError("Нет результатов в секции 'organic'")

            first_link = organic[0].get('link', '')
            if not first_link:
                logger.warning("Первая ссылка отсутствует в результатах поиска")
                raise ValueError("Первая ссылка отсутствует в результатах поиска")

            token_drop_url = first_link.rstrip('/').split('/')[-1]
            logger.info(f"Token drop URL в Dropstab: {token_drop_url}")
            return token_drop_url
        except Exception as e:
            logger.error(f"Ошибка при получении ссылки Dropstab: {e}")
            raise Exception("Не удалось получить ссылку Dropstab")

class GetCryptorankTokenomicLinks(BaseTool):
    name: str = 'get cryptorank tokenomic links'
    description: str = 'Получает ссылки на tokenomic данные Cryptorank'

    def _run(self, token_name: str) -> str:
        """
        Получает ссылку на tokenomic данные Cryptorank.

        Args:
            token_name (str): Название токена.

        Returns:
            str: Ссылка на Cryptorank.
        """
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": f"cryptorank {token_name}"})
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        response_data = response.json()

        organic = response_data.get('organic', [])
        if not organic:
            raise ValueError("Нет результатов в секции 'organic'")

        first_link = organic[0].get('link', '')
        if not first_link:
            raise ValueError("Первая ссылка отсутствует в результатах поиска")

        token_cryptorank_url = first_link.rstrip('/').split('/')[-1]
        logger.info(f"Token cryptorank URL: {token_cryptorank_url}")
        return token_cryptorank_url

class GetTokenomicLinks(BaseTool):  
    name: str = 'get tokenomic links'
    description: str = 'Получает ссылки на tokenomic данные Dropstab и Cryptorank'

    def _run(self, token_name: str) -> dict:
        """
        Получает ссылки на tokenomic данные Dropstab и Cryptorank.

        Args:
            token_name (str): Название токена.

        Returns:
            dict: Ссылки на Dropstab и Cryptorank.
        """
        get_dropstab = GetDropstabTokenomicLinks()
        get_cryptorank = GetCryptorankTokenomicLinks()

        try:
            dropstab_link = get_dropstab._run(token_name)
            cryptorank_link = get_cryptorank._run(token_name)

            result = {
                "dropstab": dropstab_link,
                "cryptorank": cryptorank_link
            }
            logger.info(f"Полученные ссылки GetTokenomicLinks: {result}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении tokenomic ссылок: {e}")
            return {}