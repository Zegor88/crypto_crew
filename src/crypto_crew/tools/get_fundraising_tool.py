# src/crypto_crew/tools/get_fundraising_tool.py

from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks
import json
import html
import requests
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DropstabFundraisingFetcher:
    """
    Класс для получения и парсинга данных о финансировании из Dropstab.
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
        url = f"https://dropstab.com/coins/{token_drop_url}/fundraising"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "goto": url,
            "sel": '#coin-tabs > div > section > div',
            "timeout": 30000
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload)
            )
            logger.info(f"Dropstab Fundraising, status: {response.status_code}")
            response.raise_for_status()
            response_data = response.json()
            html_content = html.unescape(response_data.get('data', ''))
            return html_content
        except requests.HTTPError:
            logger.error("Информация о Fundraising из Dropstab не получена из-за HTTP ошибки.")
            raise Exception("Информация о Fundraising из Dropstab не получена")
        except Exception as e:
            logger.error(f"Ошибка при получении Fundraising данных: {e}")
            raise Exception(f"Ошибка при получении данных для токена URL: {token_drop_url}: {e}")

    def parse_fundraising_rounds(self, soup: BeautifulSoup) -> list:
        """
        Извлекает и форматирует информацию о раундах инвестирования.

        Args:
            soup (BeautifulSoup): HTML контент.

        Returns:
            list: Отформатированные раунды финансирования.
        """
        rounds = []
        for div in soup.find_all(
            'div',
            class_="group relative flex flex-col gap-y-4 rounded-2xl p-4 shadow-md hover:bg-gray-100 active:bg-gray-200 dark:bg-zinc-800 dark:shadow-black dark:hover:bg-zinc-700 dark:active:bg-zinc-600"
        ):
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
                investors.append(
                    f"{investor_number:<5} {name:<30} {tier:<10} {investor_type:<20} {stage:<10}"
                )
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

            result = "========== Fundraising ============\n"
            result += "## Source: Dropstab ##\n"
            result += "# Инвесторы\n"
            result += "#     Имя                            Tier       Тип                  Стадия    \n"
            result += "---------------------------------------------------------------------------\n"
            if investors:
                result += "\n".join(investors) + "\n\n"
            else:
                result += "Инвесторы не найдены.\n\n"

            result += "# Раунды финансирования:\n"
            if rounds:
                result += "\n".join(rounds) + "\n\n"
            else:
                result += "Раунды финансирования не найдены.\n\n"

            logger.info("Финансирование из Dropstab успешно получено и отформатировано.")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении данных из Dropstab: {e}")
            return f"Ошибка при получении данных из Dropstab: {e}"


class CryptoRankFundraisingFetcher:
    """
    Класс для получения и парсинга данных о финансировании из CryptoRank.
    """

    def __init__(self, base_url: str = "http://212.113.117.33:8080"):
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
        lines = ["## Source: Cryptorank ##\n\n"]

        if investors:
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
        else:
            lines.append("Инвесторы не найдены.\n")

        lines.append("\n**Финансовые раунды, IEO и Launchpools**\n")
        for idx, item in enumerate(funding_rounds, 1):
            lines.append(
                f"{idx}. **{item['Тип']} на платформе {item['Платформа']}**\n"
                f"   - **Дата:** {item['Дата']}\n"
                f"   - **Собранная сумма:** {item['Собрано']}\n"
                f"   - **Цена токена:** {item['Цена']}\n"
                f"   - **ROI:** {item['ROI']}\n"
                f"   - **ATH ROI:** {item['ATH ROI']}\n"
            )

        return ''.join(lines)


class GetFundraisingTool(BaseTool):
    """
    Инструмент для получения информации о финансировании из Dropstab и Cryptorank.
    """

    name: str = "get_fundraising_tool"
    description: str = (
        "Извлекает информацию о финансировании из Dropstab и Cryptorank "
        "для указанного токена криптовалюты."
    )

    def _run(self, token: str) -> str:
        """
        Выполняет инструмент для получения и форматирования данных.

        Args:
            token (str): Идентификатор токена.

        Returns:
            str: Объединенные отформатированные данные о финансировании.
        """
        try:
            tokenomic_links_tool = GetTokenomicLinks()
            tokenomic_links = tokenomic_links_tool._run(token)

            logger.info('Tokenomic links:', tokenomic_links)

            token_dropstab = tokenomic_links.get('dropstab')
            token_cryptorank = tokenomic_links.get('cryptorank')

            fundraising_fetcher_dropstab = DropstabFundraisingFetcher()
            fundraising_fetcher_cryptorank = CryptoRankFundraisingFetcher()

            combined_result = ""

            # Получение Dropstab Fundraising
            try:
                fundraising_data_dropstab = fundraising_fetcher_dropstab.get_fundraising(token_dropstab)
                combined_result += fundraising_data_dropstab + "\n"
            except Exception as e:
                logger.error(f"Не удалось получить Dropstab Fundraising: {e}")
                combined_result += "Не удалось получить данные о Dropstab Fundraising.\n\n"

            # Получение Cryptorank Fundraising
            try:
                fundraising_data_cryptorank = fundraising_fetcher_cryptorank.scrape(token_cryptorank)
                combined_result += fundraising_data_cryptorank + "\n"
            except Exception as e:
                logger.error(f"Не удалось получить Cryptorank Fundraising: {e}")
                combined_result += "Не удалось получить данные о Cryptorank Fundraising.\n\n"

            return combined_result
        except Exception as e:
            logger.error(f"Ошибка при выполнении GetFundraisingTool: {e}")
            return f"Ошибка при выполнении GetFundraisingTool: {e}"


# Не забудьте определить класс GetTokenomicLinks или импортировать его, если он находится в другом модуле.
# Например:
# from src.crypto_crew.tools.get_tokenomic_links import GetTokenomicLinks
