### src/crypto_crew/tools/get_fundraising.py

import os
import json
import requests
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks

class FundraisingFetcher:
    def __init__(self, base_url="http://212.113.117.33:8080"):
        self.base_url = base_url

    def get_html(self, token_drop_url):
        """Отправляет POST-запрос и возвращает HTML-контент."""
        url = f"https://dropstab.com/coins/{token_drop_url}/fundraising"  # Формируем URL с использованием token_drop_url
        headers = {
            "Content-Type": "application/json"
        }

        # Данные для POST-запроса
        data = {
            "goto": url,
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        # Отправляем POST-запрос
        response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            # Парсим JSON ответ, извлекаем HTML-контент
            response_data = json.loads(response.text)
            html_content = html.unescape(response_data['data'])
            return html_content
        else:
            raise Exception(f"Failed to fetch data for URL: {url}, status code: {response.status_code}")

    def parse_fundraising_rounds(self, soup):
        """Извлекает и форматирует информацию о раундах инвестирования."""
        rounds = []
        for div in soup.find_all('div', class_="group relative flex flex-col gap-y-4 rounded-2xl p-4 shadow-md hover:bg-gray-100 active:bg-gray-200 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-600"):
            round_name = div.find('h2').get_text(strip=True)
            date = div.find('span', class_="text-gray-900 dark:text-white").get_text(strip=True)
            funds_raised = div.find_all('span', class_="text-gray-900 dark:text-white")[-1].get_text(strip=True)

            rounds.append(f"Round: {round_name}, Date: {date}, Funds Raised: {funds_raised}")
        
        return rounds

    def parse_investors(self, soup):
        """Извлекает и форматирует информацию об инвесторах."""
        investors = []
        for row in soup.find_all('tr', class_="group tableRow"):
            cells = row.find_all('td')
            if len(cells) == 5:
                investor_number = cells[0].get_text(strip=True)
                name = cells[1].get_text(strip=True)
                tier = cells[2].get_text(strip=True)
                investor_type = cells[3].get_text(strip=True)
                stage = cells[4].get_text(strip=True)
                investors.append(f"{investor_number:<5} {name:<30} {tier:<10} {investor_type:<20} {stage:<10}")
        return investors

    def get_fundraising(self, token_drop_url):
        """Основной метод для получения данных и форматирования результата."""
        try:
            html_content = self.get_html(token_drop_url)
            soup = BeautifulSoup(html_content, "html.parser")

            # Извлекаем раунды финансирования
            rounds = self.parse_fundraising_rounds(soup)

            # Извлекаем информацию об инвесторах
            investors = self.parse_investors(soup)

            # Форматируем текстовый вывод
            result = "# Fundraising Rounds:\n"
            if rounds:
                result += "\n".join(rounds) + "\n\n"
            else:
                result += "No fundraising rounds found.\n\n"
            
            result += "# Investors\n"
            result += f"#     {'Name':<30} {'Tier':<10} {'Type':<20} {'Stage':<10}\n"
            result += "-" * 75 + "\n"
            if investors:
                result += "\n".join(investors)
            else:
                result += "No investors found."

            return result
        except Exception as e:
            return f"Error fetching data for token URL: {token_drop_url}: {e}"

class FundraisingTool(BaseTool):
    name: str = "fundraising_fetcher"
    description: str = "Получает информацию о раундах финансирования и инвесторах для указанного токена криптовалюты."

    def _run(self, token: str) -> str:
        """
        Получает информацию о раундах финансирования и инвесторах для заданного токена.
        """
        # Создаем экземпляр GetTokenomicLinks
        tokenomic_links_tool = GetTokenomicLinks()
        # Получаем название токена
        token_drop_url = tokenomic_links_tool._run(token)

        fetcher = FundraisingFetcher()
        return fetcher.get_fundraising(token_drop_url)
