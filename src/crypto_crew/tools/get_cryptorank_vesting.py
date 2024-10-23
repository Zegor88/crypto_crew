import requests
import json
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
import logging  # Добавлено импортирование logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoRankVestingFetcher(BaseTool):
    name: str = "cryptorank_vesting_tool"
    description: str = "Получает информацию о вестинге из Cryptorank для указанного токена криптовалюты."

    def get_vesting_cryptorank(self, token: str) -> dict:
        """
        Получает данные о вестинге из Cryptorank для заданного токена.

        Args:
            token (str): Имя токена.

        Returns:
            dict: Содержит информацию о распределении и аллокации.
        """
        url = "http://212.113.117.33:8080"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Формируем данные для POST-запроса
        payload = {
            "goto": f"https://cryptorank.io/price/{token}/vesting",
            "sel": '#root-container > section',
            "timeout": 30000
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            logger.info(f"Запрос к {url} для токена {token}. Статус: {response.status_code}")
            response.raise_for_status()
            
            decoded_html = html.unescape(response.json().get('data', ''))
            soup = BeautifulSoup(decoded_html, 'html.parser')

            distribution_progress = self.extract_distribution_progress(soup)
            allocation = self.extract_allocation_data(soup)

            return {
                'distribution_progress': distribution_progress,
                'allocation_data': allocation
            }
        except requests.HTTPError:
            logger.error("Информация о Vesting из Cryptorank не получена из-за HTTP ошибки.")
            raise Exception("Информация о Vesting из Cryptorank не получена")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
            raise Exception("Информация о Vesting из Cryptorank не получена")

    @staticmethod
    def extract_distribution_progress(soup: BeautifulSoup) -> list:
        """
        Извлекает данные о распределении из HTML.

        Args:
            soup (BeautifulSoup): Парсенный HTML.

        Returns:
            list: Список словарей с данными о распределении.
        """
        distribution_data = []
        section = soup.find('h2', string=lambda x: x and 'Total Distribution Progress' in x)
        if section:
            parent_div = section.find_parent('div', class_='sc-2328569c-0')
            if parent_div:
                entries = parent_div.find_all('div', class_='sc-2ecfa897-0')
                for entry in entries:
                    dist_type = entry.find('p', class_='sc-56567222-0').get_text().split()[0] if entry.find('p', class_='sc-56567222-0') else 'N/A'
                    percentage = entry.find('span', class_='sc-56567222-0 sc-92cddc74-0').text.strip() if entry.find('span', class_='sc-56567222-0 sc-92cddc74-0') else 'N/A'
                    amount_elem = entry.find('p', class_='sc-56567222-0 ebjuzh')
                    if amount_elem:
                        amount_text = amount_elem.text.strip()
                        token_amount, usd_amount = amount_text.split(' ~ ') if ' ~ ' in amount_text else (amount_text, 'N/A')
                    else:
                        token_amount = usd_amount = 'N/A'
                    distribution_data.append({
                        'Тип': dist_type,
                        'Процент': percentage,
                        'Количество токенов': token_amount,
                        'Долларовый эквивалент': usd_amount
                    })
        return distribution_data

    @staticmethod
    def extract_allocation_data(soup: BeautifulSoup) -> list:
        """
        Извлекает данные об аллокации из HTML.

        Args:
            soup (BeautifulSoup): Парсенный HTML.

        Returns:
            list: Список словарей с данными об аллокации.
        """
        allocation_data = []
        section = soup.find('h2', string=lambda x: x and 'Allocation' in x)
        if section:
            parent_div = section.find_parent('div', class_='sc-2328569c-0')
            if parent_div:
                table = parent_div.find('table')
                if table:
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 4:
                                name = cols[0].get_text(strip=True)
                                total = cols[1].get_text(strip=True)
                                unlocked = cols[2].get_text(strip=True)
                                locked = cols[3].get_text(strip=True)
                                allocation_data.append({
                                    'Name': name,
                                    'Total': total,
                                    'Unlocked': unlocked,
                                    'Locked': locked
                                })
        return allocation_data

    def _run(self, token: str) -> str:
        """
        Получает и форматирует информацию о вестинге.

        Args:
            token (str): Имя токена.

        Returns:
            str: Отформатированные данные о вестинге.
        """
        try:
            vesting_data = self.get_vesting_cryptorank(token)
            result = "Данные о распределении:\n"
            for item in vesting_data['distribution_progress']:
                result += f"Тип: {item['Тип']}, Процент: {item['Процент']}, Количество токенов: {item['Количество токенов']}, Долларовый эквивалент: {item['Долларовый эквивалент']}\n"
            result += "\nДанные об аллокации:\n"
            for item in vesting_data['allocation_data']:
                result += f"| {item['Name']} | {item['Total']} | {item['Unlocked']} | {item['Locked']} |\n"
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении CryptoRankVestingFetcher: {e}")
            return "Информация о Vesting из Cryptorank не получена"
