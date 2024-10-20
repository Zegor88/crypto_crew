### src/crypto_crew/tools/get_tokenomic_links.py

from crewai_tools import BaseTool
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

class GetTokenomicLinks(BaseTool):
    name: str = 'get tokenomic links'
    description: str = 'Get tokenomic links'

    def _run(self, token_name: str) -> str:
        """
        Get tokenomic links
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

        print('Token drop URL:', token_drop_url)
        return token_drop_url

# if __name__ == "__main__":
#     def test_web_search_tool():
#         # Создайте экземпляр инструмента
#         web_search_tool = WebSearchTool()
        
#         # Пример символа токена для тестирования
#         token_name = "strk"  # Замените на актуальный символ токена
        
#         try:
#             # Вызовите метод _run инструмента
#             result = web_search_tool._run(token_name)
#             print("Результат работы WebSearchTool:")
#             print(result)
#         except Exception as e:
#             print(f"Произошла ошибка при запуске WebSearchTool: {e}")

#     test_web_search_tool()
