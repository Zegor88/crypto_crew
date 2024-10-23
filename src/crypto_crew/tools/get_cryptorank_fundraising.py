### src/crypto_crew/tools/get_cryptorank_fundraising.py

import json
import html
import requests
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
import logging  # Добавлено импортирование logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoRankScraper:
    """
    Класс для скрапинга данных о финансировании и инвесторах с CryptoRank.
    """

    def __init__(self, base_url: str = "http://212.113.117.33:8080"):
        """
        Инициализирует скрапер с базовым URL и заголовками.
        
        Args:
            base_url (str): Базовый URL для POST-запросов.
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_fundraising_page(self, token: str) -> str:
        """
        Отправляет POST-запрос для получения страницы финансирования.

        Args:
            token (str): Идентификатор токена на CryptoRank.

        Returns:
            str: HTML-содержимое страницы.
        
        Raises:
            requests.HTTPError: Если запрос завершился с ошибкой.
        """
        payload = {
            "goto": f"https://cryptorank.io/ico/{token}",
            "sel": '#root-container > section > div.sc-42c5ae26-4.hvBTer',
            "timeout": 30000
        }

        try:
            response = self.session.post(self.base_url, data=json.dumps(payload))
            logger.info(f"Cryptorank Fundraising, status: {response.status_code}")
            response.raise_for_status()
            return response.text
        except requests.HTTPError:
            logger.error("Информация о Fundraising из Cryptorank не получена из-за HTTP ошибки.")
            raise Exception("Информация о Fundraising из Cryptorank не получена")
        except Exception as e:
            logger.error(f"Ошибка при получении Fundraising данных: {e}")
            raise Exception("Информация о Fundraising из Cryptorank не получена")

    def extract_funding_rounds(self, soup: BeautifulSoup) -> list:
        """
        Извлекает информацию о раундах финансирования из BeautifulSoup объекта.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup с HTML-контентом.

        Returns:
            list of dict: Список словарей с данными о раундах финансирования.
        """
        funding_data = []
        funding_header = soup.find(
            'h2',
            string=lambda text: text and 'Funding Rounds' in text
        )

        if not funding_header:
            return funding_data

        parent_div = funding_header.find_parent('div', class_=lambda x: x and 'cards' in x)
        if not parent_div:
            return funding_data

        entries = parent_div.find_all('div', class_=lambda x: x and 'kDrqot' in x)
        for entry in entries:
            funding_type = self._get_text(entry, 'p', 'eqjvBs')
            date = self._get_text(entry, 'p', 'fxIPVd')
            raised = self._get_text(entry, 'p', 'bYpygy')
            price = self._get_nested_text(entry, 'div', 'price', 'p', 'jvlrjM')
            roi = self._get_nested_text(entry, 'div', 'roi', 'p', 'jvlrjM')
            ath_roi = self._get_nested_text(entry, 'div', 'athRoi', 'p', 'jvlrjM')
            platform = self._get_nested_text(entry, 'div', 'platform', 'p', 'jvlrjM')

            funding_data.append({
                'Тип': funding_type,
                'Дата': date,
                'Собрано': raised,
                'Цена': price,
                'ROI': roi,
                'ATH ROI': ath_roi,
                'Платформа': platform
            })

        return funding_data

    def extract_investors(self, soup: BeautifulSoup) -> list:
        """
        Извлекает информацию об инвесторах из BeautifulSoup объекта.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup с HTML-контентом.

        Returns:
            list of dict: Список словарей с данными об инвесторах.
        """
        investors = []
        investors_header = soup.find(
            'h2',
            string=lambda text: text and 'Investors and Backers' in text
        )

        if not investors_header:
            return investors

        table = investors_header.find_next('table')
        if not table:
            return investors

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue

            name = self._get_text(cols[0], 'p', 'ktClAm')
            tier = self._get_text(cols[1], 'p', 'ktClAm')
            inv_type = self._get_text(cols[2], 'p', 'ktClAm')
            stages = [btn.text.strip() for btn in cols[3].find_all('button')]

            investors.append({
                'Название': name,
                'Уровень': tier,
                'Тип': inv_type,
                'Этапы инвестирования': ', '.join(stages) if stages else 'N/A'
            })

        return investors

    @staticmethod
    def _get_text(parent: BeautifulSoup, tag: str, class_name: str) -> str:
        """
        Извлекает текст из указанного тега и класса.

        Args:
            parent (BeautifulSoup): Родительский тег.
            tag (str): Имя тега для поиска.
            class_name (str): Класс тега.

        Returns:
            str: Извлеченный текст или 'N/A', если не найдено.
        """
        element = parent.find(tag, class_=lambda x: x and class_name in x)
        return element.text.strip() if element and element.text else 'N/A'

    @staticmethod
    def _get_nested_text(parent: BeautifulSoup, div_tag: str, div_class: str, target_tag: str, target_class: str) -> str:
        """
        Извлекает вложенный текст из дочернего тега.

        Args:
            parent (BeautifulSoup): Родительский тег.
            div_tag (str): Имя дочернего div тега.
            div_class (str): Класс дочернего div тега.
            target_tag (str): Имя целевого тега для извлечения текста.
            target_class (str): Класс целевого тега.

        Returns:
            str: Извлеченный текст или 'N/A', если не найдено.
        """
        div_element = parent.find(div_tag, class_=lambda x: x and div_class in x)
        if not div_element:
            return 'N/A'
        target_element = div_element.find(target_tag, class_=lambda x: x and target_class in x)
        return target_element.text.strip() if target_element and target_element.text else 'N/A'

    def scrape(self, token: str) -> str:
        """
        Основной метод для скрапинга данных.

        Args:
            token (str): Идентификатор токена на CryptoRank.

        Returns:
            str: Отформатированные данные о финансировании и инвесторах.
        """
        try:
            html_content = self.fetch_fundraising_page(token)
            decoded_html = html.unescape(html_content)
            soup = BeautifulSoup(decoded_html, 'html.parser')

            funding_rounds = self.extract_funding_rounds(soup)
            investors = self.extract_investors(soup)

            return self._format_results(funding_rounds, investors)
        except Exception as e:
            logger.error(f"Ошибка при скрапинге данных из Cryptorank: {e}")
            raise Exception("Информация о Fundraising из Cryptorank не получена")

    @staticmethod
    def _format_results(funding_rounds: list, investors: list) -> str:
        """
        Форматирует результаты в строку.

        Args:
            funding_rounds (list): Данные о раундах финансирования.
            investors (list): Данные об инвесторах.

        Returns:
            str: Отформатированная строка с результатами.
        """
        lines = ["**Финансовые раунды, IEO и Launchpools**\n"]

        for idx, item in enumerate(funding_rounds, 1):
            lines.append(
                f"{idx}. **{item['Тип']} на платформе {item['Платформа']}**\n"
                f"   - **Дата:** {item['Дата']}\n"
                f"   - **Собранная сумма:** {item['Собрано']}\n"
                f"   - **Цена токена:** {item['Цена']}\n"
                f"   - **ROI:** {item['ROI']}\n"
                f"   - **ATH ROI:** {item['ATH ROI']}\n"
            )
        lines.append("\n---\n\n")
        lines.append("**Инвесторы и партнеры**\n")
        lines.append(
            "| Название                         | Уровень | Тип          | Этапы инвестирования    |\n"
            "|----------------------------------|---------|--------------|-------------------------|\n"
        )

        for inv in investors:
            lines.append(
                f"| {inv['Название']:<32} | {inv['Уровень']:<7} | "
                f"{inv['Тип']:<12} | {inv['Этапы инвестирования']:<23} |\n"
            )

        return ''.join(lines)

class CryptorankFundraisingTool(BaseTool):
    """
    Инструмент для получения информации о финансировании и инвесторах из CryptoRank.
    """

    name: str = "cryptorank_fundraising_tool"
    description: str = (
        "Получает информацию о раундах финансирования и инвесторах "
        "из CryptoRank для указанного токена криптовалюты."
    )

    def _run(self, token: str) -> str:
        """
        Выполняет инструмент для получения и форматирования данных.

        Args:
            token (str): Идентификатор токена на CryptoRank.

        Returns:
            str: Отформатированные данные о финансировании или сообщение об ошибке.
        """
        try:
            scraper = CryptoRankScraper()
            result = scraper.scrape(token)
            return result
        except requests.HTTPError as http_err:
            return f"HTTP ошибка при выполнении CryptorankFundraisingTool: {http_err}"
        except Exception as err:
            return f"Неизвестная ошибка при выполнении CryptorankFundraisingTool: {err}"

