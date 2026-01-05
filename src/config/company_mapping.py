"""
Mapeamento de códigos de empresa para CNPJ.
Este arquivo é usado para converter o código da empresa extraído do email
para o CNPJ que deve ser enviado no campo 'user' da API MinasTaxi.
"""

# Dicionário de mapeamento: código_empresa -> CNPJ (apenas números)
COMPANY_CODE_TO_CNPJ = {
    "284": "17161936000873",   # DELP ENGENHARIA MECANICA S.A
    "225": "21470224000137",   # SIMPLEX EQUIPAMENTOS LTDA
    "320": "19378769000176",   # INSTITUTO HERMES PARDINI S/A
    "6010": "66429895000192",  # CLAMPER INDUSTRIA E COMERCIO S.A.
    "6017": "02572696000156",  # KOCH DO BRASIL PROJETOS INDUSTRIAIS LTDA
    "1011": "32592616000195",  # SUPORTE INFORMATICA
}

# CNPJ padrão caso não encontre o código da empresa (CSN/Koch)
DEFAULT_CNPJ = "02572696000156"


def get_cnpj_from_company_code(company_code: str) -> str:
    """
    Retorna o CNPJ correspondente ao código da empresa.
    
    Args:
        company_code: Código da empresa extraído do email (ex: "284").
        
    Returns:
        CNPJ da empresa ou CNPJ padrão se não encontrar.
    """
    if not company_code:
        return DEFAULT_CNPJ
    
    # Remove espaços em branco
    company_code = company_code.strip()
    
    return COMPANY_CODE_TO_CNPJ.get(company_code, DEFAULT_CNPJ)


def add_company_mapping(company_code: str, cnpj: str):
    """
    Adiciona um novo mapeamento dinamicamente.
    
    Args:
        company_code: Código da empresa.
        cnpj: CNPJ da empresa (apenas números).
    """
    COMPANY_CODE_TO_CNPJ[company_code] = cnpj


def list_all_companies() -> dict:
    """
    Retorna todos os mapeamentos disponíveis.
    
    Returns:
        Dicionário com código -> CNPJ.
    """
    return COMPANY_CODE_TO_CNPJ.copy()
