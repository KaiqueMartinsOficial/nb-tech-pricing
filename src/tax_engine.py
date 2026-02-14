# src/tax_engine.py
from src.models import ProductInput, CustomerContext
from config.tax_rates import TaxConstants

class TaxEngine:
    @staticmethod
    def calculate_taxes(product: ProductInput, customer: CustomerContext, base_price: float):
        taxes = {}
        
        # 1. PIS/COFINS
        taxes['pis_cofins'] = base_price * (TaxConstants.PIS_RATE + TaxConstants.COFINS_RATE)
        
        # 2. IPI
        ipi_value = base_price * product.ipi_rate
        taxes['ipi'] = ipi_value
        price_with_ipi = base_price + ipi_value

        # 3. ICMS Próprio (Origem)
        if product.origin_uf == customer.uf:
            icms_rate = TaxConstants.ICMS_PADRAO
        else:
            icms_rate = TaxConstants.get_interstate_rate(product.origin_uf, customer.uf)
            
        taxes['icms_own'] = base_price * icms_rate
        
        # 4. DIFAL (Apenas venda interestadual para Não Contribuinte)
        taxes['difal'] = 0.0
        if customer.type == "Nao_Contribuinte" and product.origin_uf != customer.uf:
            # Base do DIFAL é o valor da operação (Simples Nacional/Lucro Presumido regra geral)
            # Diferença entre Alíquota Interna do Destino e Interestadual
            difal_rate = max(0, customer.internal_icms_dest - icms_rate)
            taxes['difal'] = base_price * difal_rate

        # 5. ICMS-ST (Apenas Contribuinte com MVA)
        taxes['icms_st'] = 0.0
        if product.mva_st > 0 and customer.type == "Contribuinte":
            # Base ST = (Valor + IPI) * (1 + MVA)
            base_st = price_with_ipi * (1 + product.mva_st)
            icms_st_total = base_st * customer.internal_icms_dest
            # ST a recolher = ICMS ST Total - ICMS Próprio
            st_value = icms_st_total - taxes['icms_own']
            taxes['icms_st'] = max(0, st_value)

        return taxes