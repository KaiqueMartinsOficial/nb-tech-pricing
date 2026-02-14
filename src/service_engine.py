# src/service_engine.py
from src.models import ServiceInput, PricingScenario

class ServicePricer:
    # Custos Operacionais Base
    COST_HOUR_TECH = 141.50  # Custo H/H
    COST_KM = 1.50           # Custo Km Rodado
    
    # Impostos Específicos (Lucro Presumido)
    TAX_RATE_MAINTENANCE = 0.1718  # 17.18%
    TAX_RATE_RENTAL = 0.1157       # 11.57%

    def __init__(self, service: ServiceInput, scenario: PricingScenario):
        self.service = service
        self.scenario = scenario

    def calculate_contract_price(self) -> dict:
        """
        Calcula o preço mensal considerando escala e visitas anuais.
        """
        # 1. Definição da Carga Tributária
        if "Locação" in self.service.service_type:
            tax_rate = self.TAX_RATE_RENTAL
        else:
            tax_rate = self.TAX_RATE_MAINTENANCE

        # 2. Conversão de Frequência (Anual -> Mensal Média)
        # Se são 4 visitas no ano, a média é 0.33 visitas por mês.
        # O custo é diluído nas mensalidades.
        if "Serviço Pontual" in self.service.service_type:
            monthly_visits_avg = 1.0 # Pontual é 1 visita
        else:
            monthly_visits_avg = self.service.visits_per_year / 12.0

        # 3. Custo de Mão de Obra (OpEx Labor)
        # Horas * Qtd Máquinas * Média de Visitas Mensais
        total_tech_hours_month = self.service.technical_hours_per_visit * self.service.ups_quantity * monthly_visits_avg
        labor_cost = total_tech_hours_month * self.COST_HOUR_TECH
        
        # 4. Custo Logístico (OpEx Logistics)
        # Distância * Qtd Locais * Média de Visitas Mensais
        total_km_month = self.service.distance_km_round_trip * self.service.num_locations * monthly_visits_avg
        logistics_cost = total_km_month * self.COST_KM
        
        # 5. Custo de Peças (Risco)
        parts_risk = self.service.parts_cost_estimation_monthly * self.service.ups_quantity

        opex_total = labor_cost + logistics_cost + parts_risk
        
        # 6. Amortização do Ativo (CapEx)
        total_capex = self.service.equipment_capex_unit * self.service.ups_quantity
        asset_amortization = 0.0
        
        if "Compra UPS Nova" in self.service.service_type:
            if self.service.contract_duration_months > 0:
                asset_amortization = total_capex / self.service.contract_duration_months
        
        elif "UPS Estoque" in self.service.service_type:
            asset_amortization = total_capex * 0.025

        total_cost_base = opex_total + asset_amortization
        
        # 7. Formação de Preço (Markup)
        total_deductions = tax_rate + self.scenario.commission_rate + self.scenario.target_margin
        
        if total_deductions >= 0.95:
            total_deductions = 0.90
            
        final_price_monthly = total_cost_base / (1 - total_deductions)
        
        return {
            "monthly_price": round(final_price_monthly, 2),
            "total_contract_value": round(final_price_monthly * self.service.contract_duration_months, 2),
            "inputs": {
                "ups_qty": self.service.ups_quantity,
                "visits_year": self.service.visits_per_year,
                "tax_rate_used": tax_rate
            },
            "breakdown": {
                "Mão de Obra (Média/Mês)": round(labor_cost, 2),
                "Logística (Média/Mês)": round(logistics_cost, 2),
                "Risco Peças": round(parts_risk, 2),
                "Amortização Ativos": round(asset_amortization, 2),
                f"Impostos ({tax_rate*100:.2f}%)": round(final_price_monthly * tax_rate, 2),
                "Comissões": round(final_price_monthly * self.scenario.commission_rate, 2),
                "Lucro Líquido": round(final_price_monthly * self.scenario.target_margin, 2)
            }
        }