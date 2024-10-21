### src/crypto_crew/tools/get_tokenomic_links.py

from crewai_tools import BaseTool
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

class GetDropstabTokenomicLinks(BaseTool):
    name: str = 'get dropstab tokenomic links'
    description: str = 'Get dropstab tokenomic links'

    def _run(self, token_name: str) -> str:
        """
        Get dropstab tokenomic links
        args:
            token_name: str - the name of the token, can be a simple string or JSON string
        output:
            str - the search results
        """

        url = "https://google.serper.dev/search"

        payload = json.dumps({
        "q": f"dropstab  {token_name}"
        })
        headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_data = response.json()

        # Извлечение данных из 'organic'
        tech_data = response_data.get('organic', [])

        # Извлечение названия токена из первой ссылки
        first_link = tech_data[0].get('link')
        token_drop_url = first_link.split('/')[-1]  # Извлекаем 'apecoin-1' из ссылки

        print('Token drop URL in dropstab:', token_drop_url)
        return token_drop_url

    def get_tokenomic_links(self, token_name: str) -> dict:
        """
        Get links to tokenomic data on dropstab and cryptorank
        Args:
            token_name: str - the name of the token, can be a simple string
        Returns:
            dict - the links to tokenomic data on dropstab and cryptorank

        Example of return:
            {'dropstab': 'avalanche-2', 'cryptorank': 'avalanche'}
        """
        # Создайте экземпляр инструмента
        get_dropstab_tokenomic_links = GetDropstabTokenomicLinks()
        get_cryptorank_tokenomic_links = GetCryptorankTokenomicLinks()

        try:
            # Вызовите метод _run инструмента
            result_dropstab = get_dropstab_tokenomic_links._run(token_name)
            result_cryptorank = get_cryptorank_tokenomic_links._run(token_name)

            result = {
                "dropstab": result_dropstab,
                "cryptorank": result_cryptorank
            }
            print("Result of GetDropstabTokenomicLinks:")
            print(result)
            return result  # Возвращаем результат
        except Exception as e:
            print(f"An error occurred while running GetDropstabTokenomicLinks: {e}")
            return {}

class GetCryptorankTokenomicLinks(BaseTool):
    name: str = 'get cryptorank tokenomic links'
    description: str = 'Get cryptorank tokenomic links'

    def _run(self, token_name: str) -> str:
        """
        Get cryptorank tokenomic links
        args:
            token_name: str - the name of the token, can be a simple string or JSON string
        output:
            str - the search results
        """

        url = "https://google.serper.dev/search"

        payload = json.dumps({
        "q": f"cryptorank  {token_name}"
        })
        headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_data = response.json()

        # Извлечение данных из 'organic'
        tech_data = response_data.get('organic', [])

        # Извлечение названия токена из первой ссылки
        first_link = tech_data[0].get('link')
        token_cryptorank_url = first_link.split('/')[-1]  # Извлекаем 'apecoin-1' из ссылки

        print('Token cryptorank URL:', token_cryptorank_url)
        return token_cryptorank_url

    def get_tokenomic_links(token_name: str) -> dict:
        """
        Get links to tokenomic data on dropstab and cryptorank
        Args:
            token_name: str - the name of the token, can be a simple string
        Returns:
            dict - the links to tokenomic data on dropstab and cryptorank

        Example of return:
            {'dropstab': 'avalanche-2', 'cryptorank': 'avalanche'}
        """
        # Создайте экземпляр инструмента
        get_dropstab_tokenomic_links = GetDropstabTokenomicLinks()

        get_cryptorank_tokenomic_links = GetCryptorankTokenomicLinks()

        try:
            # Вызовите метод _run инструмента
            result_dropstab = get_dropstab_tokenomic_links._run(token_name)
            result_cryptorank = get_cryptorank_tokenomic_links._run(token_name)

            result = {
                "dropstab": result_dropstab,
                "cryptorank": result_cryptorank
            }
            print("Result of GetDropstabTokenomicLinks:")
            print(result)
        except Exception as e:
            print(f"An error occurred while running GetDropstabTokenomicLinks: {e}")

    # get_dropstab_tokenomic_links()
