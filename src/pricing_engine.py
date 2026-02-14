# src/pricing_engine.py
from src.models import ProductInput, CustomerContext, PricingScenario
from src.tax_engine import TaxEngine
from config.tax_rates import TaxConstants

class ProductPricer:
    def __init__(self, product: ProductInput, context: CustomerContext, scenario: PricingScenario):
        self.product = product
        self.context = context
        self.scenario = scenario
        self.tax_engine = TaxEngine()

    def calculate_selling_price(self) -> dict:
        pis_cofins_pct = TaxConstants.PIS_RATE + TaxConstants.COFINS_RATE
        
        # 1. Definição das Cargas Tributárias
        icms_load = 0.0
        difal_load = 0.0 # Custo extra para a NB Tech (Não Contribuinte)
        
        if self.product.origin_uf == self.context.uf:
            # Venda Interna: Usa alíquota cheia do estado
            icms_load = TaxConstants.ICMS_INTERNO_ESTADOS.get(self.context.uf, TaxConstants.ICMS_PADRAO)
        else:
            # Venda Interestadual
            interstate_rate = TaxConstants.get_interstate_rate(self.product.origin_uf, self.context.uf)
            icms_load = interstate_rate
            
            # SE for Não Contribuinte: NB Tech paga o DIFAL.
            # O DIFAL entra no cálculo do preço para não comer a margem.
            if self.context.type == "Nao_Contribuinte":
                internal_dest = self.context.internal_icms_dest
                # DIFAL = Interna Destino - Interestadual
                difal_load = max(0, internal_dest - interstate_rate)

        # 2. Markup (Formação de Preço)
        # Preço = Custo / (1 - Deduções)
        # Deduções = ICMS + DIFAL(se houver) + PIS/COFINS + Comissão + Adm + Lucro
        total_deductions = (
            icms_load + 
            difal_load + 
            pis_cofins_pct + 
            self.scenario.commission_rate + 
            self.scenario.admin_cost_rate + 
            self.scenario.target_margin
        )
        
        # Trava de Segurança
        if total_deductions >= 0.95:
            raise ValueError(f"Impossível precificar: Impostos e Margens somam {total_deductions*100:.1f}%")

        calculated_price = self.product.cost_price / (1.0 - total_deductions)
        
        # 3. Validação Final (R$)
        taxes = self.tax_engine.calculate_taxes(self.product, self.context, calculated_price)
        
        gross_revenue = calculated_price
        
        # Lucro Líquido Real = Receita - Todos os Impostos Pagos - Custos
        net_profit = (
            gross_revenue 
            - taxes['icms_own'] 
            - taxes['pis_cofins'] 
            - taxes['difal']  # Deduz DIFAL pago
            - taxes['icms_st']
            - (gross_revenue * self.scenario.commission_rate) 
            - (gross_revenue * self.scenario.admin_cost_rate) 
            - self.product.cost_price
        )

        return {
            "selling_price_suggested": round(calculated_price, 2),
            "cost_price": self.product.cost_price,
            "taxes": taxes,
            "financials": {
                "commission": round(gross_revenue * self.scenario.commission_rate, 2),
                "admin_expenses": round(gross_revenue * self.scenario.admin_cost_rate, 2),
                "net_profit": round(net_profit, 2),
                "net_margin_pct": round((net_profit / gross_revenue) * 100, 2)
            }
        }