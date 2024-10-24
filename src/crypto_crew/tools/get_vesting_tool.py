# src/crypto_crew/tools/get_vesting_tool.py


from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks
import json
import html
import requests
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
import pandas as pd
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DropstabVestingFetcher:
    """
    Класс для получения и парсинга данных о вестинге из Dropstab.
    """

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
        payload = {
            "goto": f"https://dropstab.com/coins/{token_drop_url}/vesting",
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        try:
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            response.raise_for_status()
            response_data = response.json()
            html_content = html.unescape(response_data.get('data', ''))
            logger.info(f"Dropstab Vesting, status: {response.status_code}")
            return html_content
        except requests.HTTPError:
            logger.error("Информация о Vesting из Dropstab не получена из-за HTTP ошибки.")
            raise Exception("Информация о Vesting из Dropstab не получена")
        except Exception as e:
            logger.error(f"Ошибка при получении Vesting данных: {e}")
            raise Exception(f"Ошибка при получении данных для токена URL: {token_drop_url}: {e}")

    def parse_vesting_data(self, soup: BeautifulSoup) -> list:
        """
        Извлекает и форматирует информацию о Vesting.

        Args:
            soup (BeautifulSoup): HTML контент.

        Returns:
            list: Список с информацией о Vesting.
        """
        vesting_info = []

        for div in soup.find_all(
            'div',
            class_="group space-y-4 rounded-2xl shadow-md hover:bg-gray-100 active:bg-gray-300/50 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-500/50"
        ):
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

    def get_vesting_lock(self, token_drop_url: str) -> str:
        """
        Основной метод для получения данных о вестинге и их форматирования.

        Args:
            token_drop_url (str): URL токена на dropstab.com.

        Returns:
            str: Отформатированные данные о вестинге.
        """
        try:
            html_content = self.get_html(token_drop_url)
            if not html_content:
                return "Данные о вестинге не найдены."

            soup = BeautifulSoup(html_content, "html.parser")
            vesting_info = self.parse_vesting_data(soup)

            if not vesting_info:
                return "Данные о вестинге не найдены."

            vesting_df = pd.DataFrame(vesting_info)
            vesting_table = vesting_df.to_markdown(index=False)

            result = "========== Vesting ============\n"
            result += "## Source: Dropstab ##\n"
            result += "# Vesting Information:\n"
            result += f"{vesting_table}\n\n"

            logger.info("Вестинг из Dropstab успешно получен и отформатирован.")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении данных из Dropstab Vesting: {e}")
            return f"Ошибка при получении данных из Dropstab Vesting: {e}"


class CryptoRankVestingFetcher:
    """
    Класс для получения и парсинга данных о вестинге из CryptoRank.
    """

    def __init__(self, base_url: str = "http://212.113.117.33:8080"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_vesting_cryptorank(self, token: str) -> dict:
        """
        Получает данные о вестинге из Cryptorank для заданного токена.

        Args:
            token (str): Имя токена.

        Returns:
            dict: Содержит информацию о распределении и аллокации.
        """
        payload = {
            "goto": f"https://cryptorank.io/price/{token}/vesting",
            "sel": '#root-container > section',
            "timeout": 30000
        }

        try:
            response = self.session.post(
                self.base_url,
                data=json.dumps(payload)
            )
            logger.info(f"Cryptorank Vesting, status: {response.status_code}")
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

    def _format_results(self, distribution_progress: list, allocation_data: list) -> str:
        """
        Форматирует результаты в строку.

        Args:
            distribution_progress (list): Данные о распределении.
            allocation_data (list): Данные об аллокации.

        Returns:
            str: Отформатированная строка с результатами.
        """
        lines = []
        for item in distribution_progress:
            lines.append(
                f"Тип: {item['Тип']}, Процент: {item['Процент']}, "
                f"Количество токенов: {item['Количество токенов']}, "
                f"Долларовый эквивалент: {item['Долларовый эквивалент']}"
            )
        lines.append("\nДанные об аллокации:\n")
        lines.append(
            "| Name                        | Total  | Unlocked | Locked |\n"
            "|-----------------------------|--------|----------|--------|\n"
        )
        for item in allocation_data:
            name = item.get('Name', 'N/A')
            total = item.get('Total', 'N/A')
            unlocked = item.get('Unlocked', 'N/A')
            locked = item.get('Locked', 'N/A')
            lines.append(f"| {name:<27} | {total:<6} | {unlocked:<8} | {locked:<6} |\n")

        return ''.join(lines)


class CryptoRankVestingTool(BaseTool):
    """
    Инструмент для получения информации о вестинге из CryptoRank.
    """

    name: str = "cryptorank_vesting_tool"
    description: str = "Получает информацию о вестинге из Cryptorank для указанного токена криптовалюты."

    def _run(self, token: str) -> str:
        """
        Выполняет инструмент для получения и форматирования данных.

        Args:
            token (str): Имя токена.

        Returns:
            str: Отформатированные данные о вестинге или сообщение об ошибке.
        """
        try:
            fetcher = CryptoRankVestingFetcher()
            vesting_data = fetcher.get_vesting_cryptorank(token)
            result = fetcher._format_results(
                vesting_data.get('distribution_progress', []),
                vesting_data.get('allocation_data', [])
            )
            return result
        except requests.HTTPError as http_err:
            return f"HTTP ошибка при выполнении CryptoRankVestingTool: {http_err}"
        except Exception as err:
            return f"Неизвестная ошибка при выполнении CryptoRankVestingTool: {err}"


class GetVestingTool(BaseTool):
    """
    Инструмент для получения информации о вестинге из Dropstab и Cryptorank.
    """

    name: str = "get_vesting_tool"
    description: str = (
        "Извлекает информацию о вестинге из Dropstab и Cryptorank "
        "для указанного токена криптовалюты."
    )

    def _run(self, token: str) -> str:
        """
        Выполняет инструмент для получения и форматирования данных о вестинге.

        Args:
            token (str): Идентификатор токена.

        Returns:
            str: Объединенные отформатированные данные о вестинге.
        """
        try:
            tokenomic_links_tool = GetTokenomicLinks()
            tokenomic_links = tokenomic_links_tool._run(token)

            logger.info('Tokenomic links:', tokenomic_links)

            token_dropstab = tokenomic_links.get('dropstab')
            token_cryptorank = tokenomic_links.get('cryptorank')

            vesting_fetcher_dropstab = DropstabVestingFetcher()
            vesting_fetcher_cryptorank = CryptoRankVestingFetcher()

            combined_result = ""

            # Получение Dropstab Vesting
            try:
                vesting_data_dropstab = vesting_fetcher_dropstab.get_vesting_lock(token_dropstab)
                combined_result += vesting_data_dropstab + "\n\n"
            except Exception as e:
                logger.error(f"Не удалось получить Dropstab Vesting: {e}")
                combined_result += "Не удалось получить данные о Dropstab Vesting.\n\n"

            # Получение Cryptorank Vesting
            try:
                vesting_data_cryptorank = vesting_fetcher_cryptorank.get_vesting_cryptorank(token_cryptorank)
                distribution_progress = "\n".join([
                    f"Тип: {item['Тип']}, Процент: {item['Процент']}, "
                    f"Количество токенов: {item['Количество токенов']}, "
                    f"Долларовый эквивалент: {item['Долларовый эквивалент']}"
                    for item in vesting_data_cryptorank.get('distribution_progress', [])
                ])
                allocation_data = "Данные об аллокации:\n"
                allocation_data += "| Name                        | Total  | Unlocked | Locked |\n"
                allocation_data += "|-----------------------------|--------|----------|--------|\n"
                for item in vesting_data_cryptorank.get('allocation_data', []):
                    name = item.get('Name', 'N/A')
                    total = item.get('Total', 'N/A')
                    unlocked = item.get('Unlocked', 'N/A')
                    locked = item.get('Locked', 'N/A')
                    allocation_data += f"| {name:<27} | {total:<6} | {unlocked:<8} | {locked:<6} |\n"

                combined_result += f"{distribution_progress}\n{allocation_data}\n"
            except Exception as e:
                logger.error(f"Не удалось получить Cryptorank Vesting: {e}")
                combined_result += "Не удалось получить данные о Cryptorank Vesting.\n"

            return combined_result
        except Exception as e:
            logger.error(f"Ошибка при выполнении GetVestingTool: {e}")
            return f"Ошибка при выполнении GetVestingTool: {e}"


# Не забудьте определить класс GetTokenomicLinks или импортировать его, если он находится в другом модуле.
# Например:
# from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks
