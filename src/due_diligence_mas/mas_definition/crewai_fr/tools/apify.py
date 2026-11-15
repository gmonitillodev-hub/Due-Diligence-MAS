from crewai_tools import ApifyActorsTool
from dotenv import load_dotenv

load_dotenv()

def get_linkedin_tool():
  
    return ApifyActorsTool(
        actor_name="dev_fusion/linkedin-profile-scraper"
    )
            


    