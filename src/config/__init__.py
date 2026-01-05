"""
Configuration module for taxi automation system.
"""
from .company_mapping import (
    get_cnpj_from_company_code,
    add_company_mapping,
    list_all_companies,
    COMPANY_CODE_TO_CNPJ,
    DEFAULT_CNPJ
)

__all__ = [
    'get_cnpj_from_company_code',
    'add_company_mapping',
    'list_all_companies',
    'COMPANY_CODE_TO_CNPJ',
    'DEFAULT_CNPJ'
]
