### src/crypto_crew/tools/get_tokenomic_links.py

from crewai_tools import BaseTool
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

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

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        response_data = response.json()

        organic = response_data.get('organic', [])
        if not organic:
            raise ValueError("Нет результатов в секции 'organic'")

        first_link = organic[0].get('link', '')
        if not first_link:
            raise ValueError("Первая ссылка отсутствует в результатах поиска")

        token_drop_url = first_link.rstrip('/').split('/')[-1]
        print('Token drop URL in dropstab:', token_drop_url)
        return token_drop_url

    def get_tokenomic_links(self, token_name: str) -> dict:
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
            return result
        except Exception as e:
            print(f"Ошибка при получении tokenomic ссылок: {e}")
            return {}

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
        print('Token cryptorank URL:', token_cryptorank_url)
        return token_cryptorank_url

    @staticmethod
    def get_tokenomic_links(token_name: str) -> dict:
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
            return result
        except Exception as e:
            print(f"Ошибка при получении tokenomic ссылок: {e}")
            return {}
