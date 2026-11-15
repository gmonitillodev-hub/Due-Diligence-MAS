

import html
from datetime import datetime
import requests
from crewai.tools import tool

from due_diligence_mas.mas_definition.classes import CurrentContext, Location

@tool
def get_current_context() -> CurrentContext:
    """
    Retrieves the current context of the conversation or interaction.
    It returns a information object, which can be used to provide 
    additional information to the prompt like location and timestamp.

    Returns:
        location (Location): The location of the current context
        date_time (Date): The date and time of the current context
    """
    
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        resp = requests.get("https://ipinfo.io/json")
        data = resp.json()
        location = Location(
            city=data.get("city"),
            timezone=data.get("timezone"),
            country=data.get("country"),
            region=data.get("region")
        )
    
    except Exception as e:
        location = "Unknown"

    return CurrentContext(
        location=location,
        date_time=current_date_time
        )

if __name__ == "__main__":
    
    print(get_current_context())