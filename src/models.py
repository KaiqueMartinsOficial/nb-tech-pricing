from pydantic import BaseModel, Field
from typing import Literal, Optional

class ProductInput(BaseModel):
    name: str
    ncm: str
    cost_price: float = Field(..., gt=0)
    ipi_rate: float = 0.0
    mva_st: float = 0.0
    origin_uf: str = "SP"

class ServiceInput(BaseModel):
    # Tipos de Serviço/Contrato
    service_type: Literal[
        "Serviço Pontual (Avulso)", 
        "Contrato Manutenção (Preventiva + Corretiva)", 
        "Locação (UPS Estoque)",
        "Locação (Compra UPS Nova)"
    ]
    
    # Detalhes do Equipamento
    ups_power: str  # Ex: "1-3 kVA", "10 kVA"
    ups_type: str   # Ex: "Monofásico", "Trifásico"
    ups_quantity: int = 1
    
    # Detalhes Operacionais
    technical_hours_per_visit: float
    distance_km_round_trip: float # Ida e Volta
    num_locations: int = 1 # Quantos locais físicos diferentes
    
    # Mudança aqui: Visitas por ANO
    visits_per_year: int = 12 
    
    # Financeiro
    equipment_capex_unit: float = 0.0 # Valor unitário do equipamento
    contract_duration_months: int = 1 
    parts_cost_estimation_monthly: float = 0.0 

class CustomerContext(BaseModel):
    uf: str
    type: Literal["Contribuinte", "Nao_Contribuinte"]
    internal_icms_dest: float = 0.18

class PricingScenario(BaseModel):
    commission_rate: float = 0.03
    admin_cost_rate: float = 0.1165
    target_margin: float = 0.25