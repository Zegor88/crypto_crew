### src/cryptocrew/main.py

import sys
from crypto_crew.crew import CryptocrewCrew
from crypto_crew.tools.get_metadata import GetCoinMetadata
import os
from dotenv import load_dotenv
import logging
logging.getLogger('sagemaker').setLevel(logging.WARNING)

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

get_coin_metadata = GetCoinMetadata()


def run():
    """
    Run the crew.
    """

    coin_symbol = input("Введите символ или название криптовалюты (например, BTC, ETH, TON): ")

    metadata = GetCoinMetadata.save_dataset.invoke(coin_symbol)

    inputs = {
        'coin_symbol': coin_symbol,
        'metadata': metadata
    }

    CryptocrewCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()