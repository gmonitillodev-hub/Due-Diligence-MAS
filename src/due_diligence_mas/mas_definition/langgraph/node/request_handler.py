from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.utils.request_handling import print_welcome_message, request_company_info

def request_handler_node(state: DueDiligence_State):
    
    print_welcome_message()
    company_info = request_company_info()
    
    return {"company_info": company_info}