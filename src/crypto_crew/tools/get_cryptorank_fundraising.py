### src/crypto_crew/tools/get_cryptorank_fundraising.py

import os
import json
import requests
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
import pandas as pd

class CryptoRankScraper:
    def __init__(self, base_url="http://212.113.117.33:8080"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    def get_fundraising_cryptorank(self, token):
        # Формируем данные для POST-запроса
        data = {
            "goto": f"https://cryptorank.io/ico/{token}",
            "sel": '#root-container > section > div.sc-42c5ae26-4.hvBTer',
            "timeout": 30000
        }
        
        # Отправляем POST-запрос
        response = requests.post(self.base_url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data, status code: {response.status_code}")
        
        # Возвращаем текст ответа
        return response.text

    def extract_funding_rounds(self, soup):
        funding_data = []
        section = soup.find('h2', string=lambda x: x and 'Funding Rounds' in x)
        if section:
            parent_div = section.find_parent('div', class_=lambda x: x and 'cards' in x)
            if parent_div:
                entries = parent_div.find_all('div', class_=lambda x: x and 'kDrqot' in x)
                for entry in entries:
                    type_elem = entry.find('p', class_=lambda x: x and 'eqjvBs' in x)
                    funding_type = type_elem.text.strip() if type_elem and type_elem.text else 'N/A'

                    date_elem = entry.find('p', class_=lambda x: x and 'fxIPVd' in x)
                    date = date_elem.text.strip() if date_elem and date_elem.text else 'N/A'

                    raised_elem = entry.find('p', class_=lambda x: x and 'bYpygy' in x)
                    raised = raised_elem.text.strip() if raised_elem and raised_elem.text else 'N/A'

                    price_elem = entry.find('div', class_=lambda x: x and 'price' in x)
                    if price_elem:
                        price_p = price_elem.find('p', class_=lambda x: x and 'jvlrjM' in x)
                        price = price_p.text.strip() if price_p and price_p.text else 'N/A'
                    else:
                        price = 'N/A'

                    roi_elem = entry.find('div', class_=lambda x: x and 'roi' in x)
                    if roi_elem:
                        roi_p = roi_elem.find('p', class_=lambda x: x and 'jvlrjM' in x)
                        roi = roi_p.text.strip() if roi_p and roi_p.text else 'N/A'
                    else:
                        roi = 'N/A'

                    ath_roi_elem = entry.find('div', class_=lambda x: x and 'athRoi' in x)
                    if ath_roi_elem:
                        ath_roi_p = ath_roi_elem.find('p', class_=lambda x: x and 'jvlrjM' in x)
                        ath_roi = ath_roi_p.text.strip() if ath_roi_p and ath_roi_p.text else 'N/A'
                    else:
                        ath_roi = 'N/A'

                    platform_elem = entry.find('div', class_=lambda x: x and 'platform' in x)
                    if platform_elem:
                        platform_p = platform_elem.find('p', class_=lambda x: x and 'jvlrjM' in x)
                        platform = platform_p.text.strip() if platform_p and platform_p.text else 'N/A'
                    else:
                        platform = 'N/A'

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

    def extract_investors(self, soup):
        investors = []
        section = soup.find('h2', string=lambda x: x and 'Investors and Backers' in x)
        if section:
            table = section.find_next('table')
            if table:
                rows = table.find('tbody').find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        name_elem = cols[0].find('p', class_=lambda x: x and 'ktClAm' in x)
                        name = name_elem.text.strip() if name_elem and name_elem.text else 'N/A'

                        tier_elem = cols[1].find('p', class_=lambda x: x and 'ktClAm' in x)
                        tier = tier_elem.text.strip() if tier_elem and tier_elem.text else 'N/A'

                        type_elem = cols[2].find('p', class_=lambda x: x and 'ktClAm' in x)
                        inv_type = type_elem.text.strip() if type_elem and type_elem.text else 'N/A'

                        stages_elem = cols[3].find_all('button')
                        stages = [btn.text.strip() for btn in stages_elem]

                        investors.append({
                            'Название': name,
                            'Уровень': tier,
                            'Тип': inv_type,
                            'Этапы инвестирования': ', '.join(stages)
                        })
        return investors

    def scrape(self, token):
        # Получаем HTML-контент для токена
        html_content = self.get_fundraising_cryptorank(token)

        # Раскодируем HTML-сущности
        decoded_html = html.unescape(html_content)

        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(decoded_html, 'html.parser')

        # Извлекаем финансовые раунды и инвесторов
        funding_rounds = self.extract_funding_rounds(soup)
        investors = self.extract_investors(soup)

        # Форматированный вывод данных
        result = "**Финансовые раунды, IEO и Launchpools**\n\n"
        for idx, item in enumerate(funding_rounds, 1):
            result += f"{idx}. **{item['Тип']} на платформе {item['Платформа']}**\n"
            result += f"   - **Дата:** {item['Дата']}\n"
            result += f"   - **Собранная сумма:** {item['Собрано']}\n"
            result += f"   - **Цена токена:** {item['Цена']}\n"
            result += f"   - **ROI:** {item['ROI']}\n"
            result += f"   - **ATH ROI:** {item['ATH ROI']}\n\n"

        result += "---\n\n"
        result += "**Инвесторы и партнеры**\n\n"
        result += "| Название                         | Уровень | Тип          | Этапы инвестирования    |\n"
        result += "|----------------------------------|---------|--------------|-------------------------|\n"
        for inv in investors:
            result += f"| {inv['Название']:<32} | {inv['Уровень']:<7} | {inv['Тип']:<12} | {inv['Этапы инвестирования']:<23} |\n"

        return result

class CryptorankFundraisingTool(BaseTool):
    name: str = "cryptorank_fundraising_tool"
    description: str = "Получает информацию о раундах финансирования и инвесторах из Cryptorank для указанного токена криптовалюты."

    def _run(self, token: str) -> str:
        """
        Получает информацию о раундах финансирования и инвесторах из Cryptorank для заданного токена.
        Args:
            token: str - идентификатор токена на Cryptorank
        Returns:
            str - отформатированные данные о финансировании
        """
        try:
            scraper = CryptoRankScraper()
            result = scraper.scrape(token)
            return result
        except Exception as e:
            return f"Ошибка при выполнении CryptorankFundraisingTool: {e}"
