### src/crypto_crew/tools/get_fundraising.py

import os
import json
import requests
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
from src.crypto_crew.tools.get_tokenomic_links import GetDropstabTokenomicLinks
from src.crypto_crew.tools.get_cryptorank_fundraising import CryptorankFundraisingTool
from src.crypto_crew.tools.get_cryptorank_vesting import CryptoRankVestingFetcher
import pandas as pd

class FundraisingFetcher:
    def __init__(self, base_url: str = "http://212.113.117.33:8080"):
        self.base_url = base_url

    def get_html(self, token_drop_url: str) -> str:
        """
        Отправляет POST-запрос и возвращает HTML-контент.

        Args:
            token_drop_url (str): URL токена на dropstab.com.

        Returns:
            str: HTML содержимое.
        """
        url = f"https://dropstab.com/coins/{token_drop_url}/fundraising"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "goto": url,
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
        print(f"Status code (Fundraising): {response.status_code}")
        response.raise_for_status()
        response_data = response.json()
        html_content = html.unescape(response_data.get('data', ''))
        return html_content

    def parse_fundraising_rounds(self, soup: BeautifulSoup) -> list:
        """
        Извлекает и форматирует информацию о раундах инвестирования.

        Args:
            soup (BeautifulSoup): HTML контент.

        Returns:
            list: Отформатированные раунды финансирования.
        """
        rounds = []
        for div in soup.find_all('div', class_="group relative flex flex-col gap-y-4 rounded-2xl p-4 shadow-md hover:bg-gray-100 active:bg-gray-200 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-600"):
            round_name = div.find('h2').get_text(strip=True)
            date = div.find('span', class_="text-gray-900 dark:text-white").get_text(strip=True)
            funds_raised = div.find_all('span', class_="text-gray-900 dark:text-white")[-1].get_text(strip=True)

            rounds.append(f"Раунд: {round_name}, Дата: {date}, Собрано средств: {funds_raised}")
        
        return rounds

    def parse_investors(self, soup: BeautifulSoup) -> list:
        """
        Извлекает и форматирует информацию об инвесторах.

        Args:
            soup (BeautifulSoup): HTML контент.

        Returns:
            list: Отформатированные инвесторы.
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

    def get_fundraising(self, token_drop_url: str) -> str:
        """
        Основной метод для получения данных и форматирования результата.

        Args:
            token_drop_url (str): URL токена на dropstab.com.

        Returns:
            str: Отформатированные данные о финансировании.
        """
        try:
            html_content = self.get_html(token_drop_url)
            soup = BeautifulSoup(html_content, "html.parser")

            rounds = self.parse_fundraising_rounds(soup)
            investors = self.parse_investors(soup)

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
    def __init__(self, base_url: str = "http://212.113.117.33:8080"):
        self.base_url = base_url

    def get_html(self, token: str) -> str:
        """
        Отправляет POST-запрос и возвращает HTML-контент.

        Args:
            token (str): Название токена на dropstab.com.

        Returns:
            str: HTML содержимое.
        """
        payload = {
            "goto": f"https://dropstab.com/coins/{token}/vesting",
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        try:
            response = requests.post(self.base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            print(f"Status code (Vesting): {response.status_code}")
            response.raise_for_status()
            response_data = response.json()
            html_content = html.unescape(response_data.get('data', ''))
            return html_content
        except Exception as e:
            print(f"Произошла ошибка при получении Vesting данных: {e}")
            return ""

    def parse_vesting_data(self, soup: BeautifulSoup) -> list:
        """
        Извлекает и форматирует информацию о Vesting.

        Args:
            soup (BeautifulSoup): HTML контент.

        Returns:
            list: Список с информацией о Vesting.
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

    def get_vesting_lock(self, token: str) -> str:
        """
        Основной метод для получения данных о вестинге и их форматирования.

        Args:
            token (str): Название токена на dropstab.com.

        Returns:
            str: Отформатированные данные о вестинге.
        """
        try:
            html_content = self.get_html(token)
            if not html_content:
                return "Данные о вестинге не найдены."
            
            soup = BeautifulSoup(html_content, "html.parser")
            vesting_info = self.parse_vesting_data(soup)

            if not vesting_info:
                return "Данные о вестинге не найдены."

            vesting_df = pd.DataFrame(vesting_info)
            vesting_table = vesting_df.to_markdown(index=False)

            return f"\n# Vesting Information:\n{vesting_table}"
        except Exception as e:
            print(f"Произошла ошибка при обработке данных для токена {token}: {e}")
            return f"Ошибка при получении данных о вестинге для токена {token}: {e}"

class DropstabFundraisingTool(BaseTool):
    name: str = "dropstab_fundraising_tool"
    description: str = ("Получает информацию о раундах финансирования, инвесторах и вестингах "
                       "из Dropstab и Cryptorank для указанного токена криптовалюты.")

    def _run(self, token: str) -> str:
        """
        Получает информацию о раундах финансирования, инвесторах и вестингах.

        Args:
            token (str): Имя токена.

        Returns:
            str: Объединенные отформатированные данные.
        """
        try:
            tokenomic_links_tool = GetDropstabTokenomicLinks()
            tokenomic_links = tokenomic_links_tool.get_tokenomic_links(token)

            print('Tokenomic links:', tokenomic_links)

            token_dropstab = tokenomic_links.get('dropstab')

            fundraising_fetcher = FundraisingFetcher()
            fundraising_data = fundraising_fetcher.get_fundraising(token_dropstab)

            vesting_fetcher = VestingFetcher()
            vesting_data = vesting_fetcher.get_vesting_lock(token_dropstab)

            cryptorank_vesting_fetcher = CryptoRankVestingFetcher()
            cryptorank_vesting_data = cryptorank_vesting_fetcher.get_vesting_cryptorank(tokenomic_links.get('cryptorank'))

            cryptorank_tool = CryptorankFundraisingTool()
            cryptorank_data = cryptorank_tool._run(tokenomic_links.get('cryptorank'))

            combined_result = (
                "Source: Dropstab\n\n"
                f"{fundraising_data}\n\n"
                f"{vesting_data}\n\n"
                "Source: Cryptorank\n\n"
                f"{cryptorank_data}\n\n"
                "Source: Cryptorank Vesting\n\n" +
                "\n".join([
                    f"Тип: {item['Тип']}, Процент: {item['Процент']}, "
                    f"Количество токенов: {item['Количество токенов']}, "
                    f"Долларовый эквивалент: {item['Долларовый эквивалент']}"
                    for item in cryptorank_vesting_data.get('distribution_progress', [])
                ])
            )
            
            allocation_data = "Данные об аллокации:\n"
            allocation_data += "| Name                        | Total  | Unlocked | Locked |\n"
            allocation_data += "|-----------------------------|--------|----------|--------|\n"
            for item in cryptorank_vesting_data.get('allocation_data', []):
                name = item.get('Name', 'N/A')
                total = item.get('Total', 'N/A')
                unlocked = item.get('Unlocked', 'N/A')
                locked = item.get('Locked', 'N/A')
                allocation_data += f"| {name:<27} | {total:<6} | {unlocked:<8} | {locked:<6} |\n"
            
            combined_result += "\n" + allocation_data
            return combined_result

        except Exception as e:
            return f"Ошибка при выполнении DropstabFundraisingTool: {e}"
