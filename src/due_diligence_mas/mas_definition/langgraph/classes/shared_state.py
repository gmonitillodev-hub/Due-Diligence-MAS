from due_diligence_mas.mas_definition.classes.company import ProfiledCompany
from typing import  Annotated, Optional
import operator

class DueDiligence_State(ProfiledCompany):
    
    messages: Optional[Annotated[list, operator.add]] = None
    