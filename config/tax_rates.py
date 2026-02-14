# config/tax_rates.py

class TaxConstants:
    """
    Constantes fiscais e Tabela de ICMS 2025/2026.
    Fonte: Legislação Estadual atualizada (Jan/2026).
    """
    
    # Impostos Federais (Lucro Presumido)
    PIS_RATE = 0.0065
    COFINS_RATE = 0.0300
    
    # Alíquota Padrão (Fallback)
    ICMS_PADRAO = 0.18

    # TABELA DE ALÍQUOTAS INTERNAS POR ESTADO (2025/2026)
    # Inclui Fundo de Pobreza (FECP/FECOEP) quando aplicável na regra geral
    ICMS_INTERNO_ESTADOS = {
        "AC": 0.19,  "AL": 0.19,  "AP": 0.18,  "AM": 0.20,
        "BA": 0.205, "CE": 0.20,  "DF": 0.20,  "ES": 0.17,
        "GO": 0.19,  "MA": 0.23,  "MT": 0.17,  "MS": 0.17,
        "MG": 0.18,  "PA": 0.19,  "PB": 0.20,  "PR": 0.195,
        "PE": 0.205, "PI": 0.225, "RJ": 0.22,  "RN": 0.20,
        "RS": 0.17,  "RO": 0.195, "RR": 0.20,  "SC": 0.17,
        "SP": 0.18,  "SE": 0.19,  "TO": 0.20
    }
    
    # Lista de siglas para o menu
    ESTADOS = sorted(list(ICMS_INTERNO_ESTADOS.keys()))

    @staticmethod
    def get_interstate_rate(origin_uf: str, dest_uf: str) -> float:
        """
        Define a alíquota interestadual (4%, 7% ou 12%).
        Regra: Sul/Sudeste (exceto ES) vendendo para Norte/Nordeste/CO/ES = 7%.
        """
        if origin_uf == dest_uf:
            return 0.0 # Venda Interna
            
        # Estados de Origem "Ricos" (Sul e Sudeste exceto ES)
        sul_sudeste_origem = ["MG", "PR", "RJ", "RS", "SC", "SP"]
        
        # Se sai do Sul/Sudeste e vai para fora dessa região (ou para o ES)
        if origin_uf in sul_sudeste_origem and dest_uf not in sul_sudeste_origem:
            return 0.07 # 7%
        
        return 0.12 # 12% Regra Geral