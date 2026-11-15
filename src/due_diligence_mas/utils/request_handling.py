
from due_diligence_mas.classes import CompanyInfo


def print_welcome_message():
    """ 
        Function useful to print basic information of Due diligence MAS
    """
    print("=" * 80)
    print(f"{'Due Diligence Flow':^80}")
    print("\n   Welcome to the Due Diligence Flow. \n   This flow will guide you through the process of analyzing a target company,\n   reviewing its technology, commercial aspects, and team dynamics, and\n   generating a comprehensive report.\n")
    print("=" * 80)
    print("\n")

def request_company_info():
    
    return CompanyInfo(
        company_name= input("Enter the target company name: "),
        company_site= input("Enter the target company website (optional): "),
        company_sector= input("Enter the target company sector (optional): "),
        additional_info= input("Enter additional informations related to the target company (optional): ")  
    )
    
         
     