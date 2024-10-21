### src/crypto_crew/tools/get_fundraising.py

### src/crypto_crew/tools/get_fundraising.py

import os
import json
import requests
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks
import pandas as pd

class FundraisingFetcher:
    def __init__(self, base_url="http://212.113.117.33:8080"):
        self.base_url = base_url

    def get_html(self, token_drop_url):
        """
        Отправляет POST-запрос и возвращает HTML-контент.
        Args:
            token_drop_url: str - the URL of the token on dropstab.com
        Returns:
            str - the HTML content
        """
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
        print(f"Status code (Fundraising): {response.status_code}")
        if response.status_code == 200:
            # Парсим JSON ответ, извлекаем HTML-контент
            response_data = json.loads(response.text)
            html_content = html.unescape(response_data['data'])
            return html_content
        else:
            raise Exception(f"Не удалось получить данные для URL: {url}, код состояния: {response.status_code}")

    def parse_fundraising_rounds(self, soup):
        """
        Извлекает и форматирует информацию о раундах инвестирования.
        Args:
            soup: BeautifulSoup object - the HTML content
        Returns:
            str - the formatted fundraising rounds
        """
        rounds = []
        for div in soup.find_all('div', class_="group relative flex flex-col gap-y-4 rounded-2xl p-4 shadow-md hover:bg-gray-100 active:bg-gray-200 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-600"):
            round_name = div.find('h2').get_text(strip=True)
            date = div.find('span', class_="text-gray-900 dark:text-white").get_text(strip=True)
            funds_raised = div.find_all('span', class_="text-gray-900 dark:text-white")[-1].get_text(strip=True)

            rounds.append(f"Раунд: {round_name}, Дата: {date}, Собрано средств: {funds_raised}")
        
        return rounds

    def parse_investors(self, soup):
        """
        Извлекает и форматирует информацию об инвесторах.
        Args:
            soup: BeautifulSoup object - the HTML content
        Returns:
            str - the formatted investors
        """
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
        """
        Основной метод для получения данных и форматирования результата.
        Args:
            token_drop_url: str - the URL of the token on dropstab.com
        Returns:
            str - the formatted fundraising data
        """
        try:
            html_content = self.get_html(token_drop_url)
            soup = BeautifulSoup(html_content, "html.parser")

            # Извлекаем раунды финансирования
            rounds = self.parse_fundraising_rounds(soup)

            # Извлекаем информацию об инвесторах
            investors = self.parse_investors(soup)

            # Форматируем текстовый вывод
            result = "# Раунды финансирования:\n"
            if rounds:
                result += "\n".join(rounds) + "\n\n"
            else:
                result += "Раунды финансирования не найдены.\n\n"
            
            result += "# Инвесторы\n"
            result += f"#     {'Имя':<30} {'Tier':<10} {'Тип':<20} {'Стадия':<10}\n"
            result += "-" * 75 + "\n"
            if investors:
                result += "\n".join(investors)
            else:
                result += "Инвесторы не найдены."

            return result
        except Exception as e:
            return f"Ошибка при получении данных для токена URL: {token_drop_url}: {e}"

class VestingFetcher:
    def __init__(self, base_url="http://212.113.117.33:8080"):
        self.base_url = base_url

    def get_html(self, token):
        """
        Отправляет POST-запрос и возвращает HTML-контент.
        Args:
            token: str - the URL of the token on dropstab.com
        Returns:
            str - the HTML content
        """
        url = self.base_url  # Используем базовый URL
        headers = {
            "Content-Type": "application/json"
        }

        # Данные для отправки с динамической подстановкой токена
        data = {
            "goto": f"https://dropstab.com/coins/{token}/vesting",
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        try:
            # Отправляем POST-запрос
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(f"Status code (Vesting): {response.status_code}")
            # Проверка успешности запроса
            if response.status_code != 200:
                raise Exception(f"Ошибка: Неверный код ответа {response.status_code}")
            
            # Парсим JSON ответ
            response_data = json.loads(response.text)
            html_content = html.unescape(response_data['data'])
            return html_content

        except Exception as e:
            print(f"Произошла ошибка при получении Vesting данных: {e}")
            return None

    def parse_vesting_data(self, soup):
        """
        Извлекает и форматирует информацию о Vesting.
        Args:
            soup: BeautifulSoup object - the HTML content
        Returns:
            str - the formatted vesting data
        """
        vesting_info = []

        for div in soup.find_all('div', class_="group space-y-4 rounded-2xl shadow-md hover:bg-gray-100 active:bg-gray-300/50 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-500/50"):
            title = div.find('span', class_="truncate text-left text-lg font-bold").get_text(strip=True)
            unlocked = div.find('span', class_="font-semibold").get_text(strip=True)
            total_supply = div.find_all('span', class_="font-medium text-gray-600 dark:text-zinc-300")[-1].get_text(strip=True)
            value_locked = div.find('div', class_="font-semibold").get_text(strip=True)
            
            vesting_info.append({
                "Название": title,
                "Разблокировано": unlocked,
                "Общий объем": total_supply,
                "Заблокировано": value_locked
            })

        return vesting_info

    def get_vesting_lock(self, token):
        """
        Основной метод для получения данных о вестинге и их форматирования в DataFrame.
        Args:
            token: str - the URL of the token on dropstab.com
        Returns:
            str - the formatted vesting data
        """
        try:
            # Получаем HTML-контент
            html_content = self.get_html(token)
            if html_content is None:
                return "Данные о вестинге не найдены."
            
            # Парсинг HTML с помощью BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Извлекаем данные о Vesting
            vesting_info = self.parse_vesting_data(soup)

            if not vesting_info:
                return "Данные о вестинге не найдены."

            # Форматируем данные в виде таблицы
            vesting_df = pd.DataFrame(vesting_info)
            vesting_table = vesting_df.to_markdown(index=False)

            return f"\n# Vesting Information:\n{vesting_table}"

        except Exception as e:
            print(f"Произошла ошибка при обработке данных для токена {token}: {e}")
            return f"Ошибка при получении данных о вестинге для токена {token}: {e}"

class DropstabFundraisingTool(BaseTool):
    name: str = "dropstab_fundraising_tool"
    description: str = "Получает информацию о раундах финансирования, инвесторах и вестингах для указанного токена криптовалюты."

    def _run(self, token: str) -> str:
        """
        Получает информацию о раундах финансирования, инвесторах и вестингах для заданного токена.
        Args:
            token: str - the URL of the token on dropstab.com
        Returns:
            str - the formatted fundraising data
        """
        try:
            # Создаем экземпляр GetTokenomicLinks
            tokenomic_links_tool = GetTokenomicLinks()
            # Получаем название токена
            token_drop_url = tokenomic_links_tool._run(token)

            # Получаем данные о финансировании
            fundraising_fetcher = FundraisingFetcher()
            fundraising_data = fundraising_fetcher.get_fundraising(token_drop_url)

            # Получаем данные о вестинге
            vesting_fetcher = VestingFetcher()
            vesting_data = vesting_fetcher.get_vesting_lock(token_drop_url)

            # Объединяем результаты
            combined_result = fundraising_data + vesting_data

            return combined_result

        except Exception as e:
            return f"Ошибка при выполнении FundraisingTool: {e}"
