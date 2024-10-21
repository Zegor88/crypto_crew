import requests
import json
import html
from bs4 import BeautifulSoup
from crewai_tools import BaseTool

class CryptoRankVestingFetcher(BaseTool):
    name: str = "cryptorank_vesting_tool"
    description: str = "Получает информацию о вестинге из Cryptorank для указанного токена криптовалюты."

    def get_vesting_cryptorank(self, token):
        url = "http://212.113.117.33:8080"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Формируем данные для POST-запроса, подставляя имя токена в URL
        data = {
            "goto": f"https://cryptorank.io/price/{token}/vesting",
            "sel": '#root-container > section',
            "timeout": 30000
        }
        
        # Отправляем POST-запрос и получаем ответ
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            decoded_html = html.unescape(response.json()['data'])
            soup = BeautifulSoup(decoded_html, 'html.parser')
        else:
            raise Exception(f"Не удалось получить данные. Код состояния: {response.status_code}")

        # Вспомогательная функция для извлечения данных о распределении
        def extract_distribution_progress(soup):
            distribution_data = []
            section = soup.find('h2', string=lambda x: x and 'Total Distribution Progress' in x)
            if section:
                parent_div = section.find_parent('div', class_='sc-2328569c-0')
                if parent_div:
                    entries = parent_div.find_all('div', class_='sc-2ecfa897-0')
                    for entry in entries:
                        type_elem = entry.find('p', class_='sc-56567222-0')
                        if type_elem:
                            dist_type = type_elem.get_text().split()[0]
                            percentage_elem = entry.find('span', class_='sc-56567222-0 sc-92cddc74-0')
                            percentage = percentage_elem.text.strip() if percentage_elem else 'N/A'
                            amount_elem = entry.find('p', class_='sc-56567222-0 ebjuzh')
                            if amount_elem:
                                amount_text = amount_elem.text.strip()
                                if ' ~ ' in amount_text:
                                    token_amount, usd_amount = amount_text.split(' ~ ')
                                else:
                                    token_amount = amount_text
                                    usd_amount = 'N/A'
                            else:
                                token_amount = usd_amount = 'N/A'
                            distribution_data.append({
                                'Тип': dist_type,
                                'Процент': percentage,
                                'Количество токенов': token_amount,
                                'Долларовый эквивалент': usd_amount
                            })
            return distribution_data

        # Вспомогательная функция для извлечения данных об аллокации
        def extract_allocation_data(soup):
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

        # Извлекаем данные о распределении и аллокации
        distribution_progress = extract_distribution_progress(soup)
        allocation = extract_allocation_data(soup)

        return {
            'distribution_progress': distribution_progress,
            'allocation_data': allocation
        }

    def _run(self, token: str) -> str:
        """
        Получает информацию о вестинге из Cryptorank для заданного токена.
        Args:
            token: str - имя токена
        Returns:
            str - отформатированные данные о вестинге
        """
        try:
            vesting_data = self.get_vesting_cryptorank(token)
            # Форматируем вывод данных
            result = "Данные о распределении:\n"
            for item in vesting_data['distribution_progress']:
                result += f"Тип: {item['Тип']}, Процент: {item['Процент']}, Количество токенов: {item['Количество токенов']}, Долларовый эквивалент: {item['Долларовый эквивалент']}\n"
            result += "\nДанные об аллокации:\n"
            for item in vesting_data['allocation_data']:
                result += f"| {item['Name']} | {item['Total']} | {item['Unlocked']} | {item['Locked']} |\n"
            return result
        except Exception as e:
            return f"Ошибка при выполнении CryptoRankVestingFetcher: {e}"
