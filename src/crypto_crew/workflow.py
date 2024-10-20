### src/crypto_crew/workflow.py

import asyncio
import pandas as pd
from crewai.flow.flow import Flow, listen, router, start
from src.crypto_crew.crew import CryptocrewCrew
from src.crypto_crew.tools.get_metadata import GetCoinMetadata
from pydantic import BaseModel
from datetime import datetime
from crewai import Crew 
from io import StringIO
from langchain_openai import ChatOpenAI

llm=ChatOpenAI(model_name="gpt-4o")

# Define the current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Define the state model
class UserState(BaseModel):
    name: str
    token: str
    date: str = current_date
    metadata: dict

# Define the WorkFlow class
class WorkFlow(Flow):

    def __init__(self):
        super().__init__()
        self._state = UserState(name="", token="", metadata={})
        self.fa_crew = CryptocrewCrew()

    @property
    def state(self):
        return self._state

    @start()
    def get_coin_metadata(self):
        # Get cryptocurrency symbol from input
        coin_symbol = input("Введите символ или название криптовалюты (например, BTC, ETH, TON): ")
        print("\n", "="*20, "Retrieving metadata", "="*20, "\n")
        # Simulate fetching metadata (replace with actual logic)
        metadata = GetCoinMetadata.save_dataset.invoke(coin_symbol)

        # Check if metadata is a dictionary
        if isinstance(metadata, dict):
            # Update the state
            self._state.token = coin_symbol
            self._state.name = metadata.get('name', "")
            self._state.metadata = metadata
        else:
            print("Ошибка: Полученные метаданные не являются словарем.")
            self._state.metadata = {"error": "Invalid metadata format"}

        return metadata

    @router(get_coin_metadata)
    def check_status(self):
        # Проверяем наличие данных в метаданных
        if self.state.metadata and "Empty DataFrame" not in self.state.metadata:
            return "proceed_to_analysis"  # Переход к анализу метаданных
        else:
            return "retry_get_metadata"  # Запрос на повторный ввод символа

    @listen("retry_get_metadata")
    def handle_retry(self):
        print("Данные не найдены. Пожалуйста, скорректируйте название токена.")
        # Retry the coin metadata fetch
        self.get_coin_metadata()

    @listen("proceed_to_analysis")
    def metadata_analysis(self):
        # Analyze the retrieved metadata
        print("\n", "="*23, "Metadata analysis", "="*23, "\n")
        
        
        inputs = {
            "metadata": self.state.metadata,
            "coin_symbol": self.state.token,
        }

        # Get the agent and task
        agent = self.fa_crew.researcher()
        task = self.fa_crew.research_task()

        # Create a crew with only this agent and task
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process='sequential',
            verbose=True,
        )
        result = crew.kickoff(inputs=inputs)

    @listen("proceed_to_analysis")
    def technology_analysis(self):
        # Analyze the technology
        print("\n", "="*23, "Technology analysis", "="*23, "\n")

        token_name = self.state.metadata.get('name', "")
        if isinstance(token_name, dict):
            token_name = token_name.get(0, "")
        
        inputs = {
            "token_name": token_name,
            "website": self.state.metadata.get('urls.website', ""),
            "whitepaper": self.state.metadata.get('urls.technical_doc', ""),
        }

        print("Inputs for technology analysis:", inputs)
        # Get the agent and task
        agent = self.fa_crew.technology_analyst()
        task = self.fa_crew.technology_analyst_task()

        # Create a crew with only this agent and task
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process='sequential',
            verbose=True,
        )

        result = crew.kickoff(inputs=inputs)
        # Add additional metadata analysis logic here

    @listen("proceed_to_analysis")
    def tokenomics_analysis(self):
        # Analyze the tokenomics
        print("\n", "="*23, "Tokenomics analysis", "="*23, "\n")

        inputs = {
            "token_name": self.state.metadata.get('name', ""),
            'coin_symbol': self.state.token,
            'coin_metadata': self.state.metadata,
        }

        # Get the agent and task
        agent = self.fa_crew.crypto_tokenomics_analyst()
        task = self.fa_crew.crypto_tokenomics_analysis_task()

        # Create a crew with only this agent and task
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process='sequential',
            verbose=True,
        )
        result = crew.kickoff(inputs=inputs)

# Define the async run function
async def run():
    """
    Run the flow.
    """
    # Initialize the workflow
    workflow = WorkFlow()
    # Start the workflow process
    await workflow.kickoff()

# Define the main function to run the flow
def main():
    asyncio.run(run())