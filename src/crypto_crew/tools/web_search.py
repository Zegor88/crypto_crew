from crewai_tools import BaseTool
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

class WebSearchTool(BaseTool):
    name: str = 'search technology'
    description: str = 'Search for information on the internet about the technology used by the project'

    def _run(self, token_name: str) -> str:
        """
        Search for information on the internet about the technology used by the project
        args:
            token_name: str - the name of the token, can be a simple string or JSON string
        output:
            str - the search results
        """
        print('WebSearchTool input:', token_name)

        # Check if token_name is in JSON format and extract the 'name' field if so
        try:
            # Attempt to parse token_name as JSON
            parsed_token = json.loads(token_name)
            if isinstance(parsed_token, dict) and 'name' in parsed_token:
                token_name = parsed_token['name']
        except (json.JSONDecodeError, TypeError):
            # If parsing fails, assume token_name is a regular string
            pass

        print('Parsed token name:', token_name)

        url = "https://google.serper.dev/search"

        # Correctly format the query string
        payload = json.dumps({
            "q": f"Crypto innovations {token_name}",
            "num": 20,
            "autocorrect": False,
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_data = response.json()

        tech_data = response_data.get('organic', [])

        return json.dumps(tech_data, indent=2)
