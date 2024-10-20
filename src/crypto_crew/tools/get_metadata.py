### src/crypto_crew/tools/get_metadata.py

import requests
import os
from langchain.tools import tool
import pandas as pd

class GetCoinMetadata:

    @tool('save_dataset')
    @staticmethod
    def save_dataset(query: str) -> str:
        """
        Retrieves all static metadata for a cryptocurrency.
        This tool returns the dataset of the metadata for the crypto project.

        Arguments:
            query (str): The symbol of the cryptocurrency (e.g., 'BTC' for Bitcoin').

        Returns:
            str: A message indicating the success of the operation.
        """
        print('save_dataset:', query)
        coin_data = GetCoinMetadata.get_coin_metadata_v2(query)

        # Конвертируем словарь данных монеты в DataFrame pandas
        df = pd.json_normalize(coin_data)

        # Убеждаемся, что директория вывода существует
        output_dir = './tmp'
        os.makedirs(output_dir, exist_ok=True)
        
        # Определяем путь к выходному CSV файлу
        csv_file_path = os.path.join(output_dir, 'metadata_df.csv')
        csv_file_path = os.path.abspath(csv_file_path)  # Получаем абсолютный путь

        # Сохраняем DataFrame в CSV файл
        df.to_csv(csv_file_path, index=False)

        return df.to_dict() #.to_string()

    @staticmethod
    def get_coin_metadata_v2(query) -> dict:
        """
        Retrieves all static metadata for a cryptocurrency using the CoinMarketCap API.

        Arguments:
            query (str): The symbol of the cryptocurrency (e.g., 'BTC' for Bitcoin').

        Returns:
            dict: A dictionary containing the cryptocurrency metadata.
        """
        import json
        # Конструируем URL API с указанным символом монеты
        print('get_coin_metadata_v2:', query)

        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/info?symbol={query}"

        payload = {}
        
        headers = {
            'X-CMC_PRO_API_KEY': os.getenv("COINMARKETCAP_API_KEY"),
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json_object = response.json()

        # Проверяем, есть ли данные по указанному символу
        if 'data' not in json_object or query not in json_object['data']:
            print(f"No data found")
            return {}

        # Поскольку символы могут быть не уникальными, API возвращает список монет с данным символом
        coin_data_list = json_object['data'][query]

        # Выбираем первые данные монеты из списка
        if coin_data_list:
            coin_data = coin_data_list[0]
            return coin_data
        else:
            print(f"No coin data available")
            return {}
