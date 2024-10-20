### src/cryptocrew/crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool
from src.crypto_crew.tools.web_search import WebSearchTool
from src.crypto_crew.tools.get_fundraising import FundraisingTool

@CrewBase
class CryptocrewCrew():
	"""Cryptocrew crew"""

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True
			)

	@agent
	def technology_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['technology_analyst'],
			verbose=True,
			tools=[ScrapeWebsiteTool(), WebSearchTool()]
		)

	@agent
	def crypto_tokenomics_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['crypto_tokenomics_analyst'],
			verbose=True,
			tools=[FundraisingTool()]
		)
	
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			output_file = './reports/1. Metadata.md'
		)

	@task
	def technology_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['technology_analyst_task'],
			output_file = './reports/2. Technology.md'
		)

	@task
	def crypto_tokenomics_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['crypto_tokenomics_analysis_task'],
			output_file = './reports/3. Tokenomics.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Cryptocrew crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)
