import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="NB Tech | Pricing Core", layout="wide", page_icon="⚡")

# CSS BLINDADO (Corrigido para forçar caixas brancas)
st.markdown("""
    <style>
    /* 1. FUNDO GERAL BRANCO */
    .stApp { background-color: #FFFFFF; }
    
    /* 2. FORÇAR TEXTOS ESCUROS NA ÁREA PRINCIPAL */
    .main .block-container p, 
    .main .block-container label, 
    .main .block-container span, 
    .main .block-container div { 
        color: #151515 !important; 
    }

    /* 3. CORREÇÃO CRÍTICA DOS INPUTS (CAIXAS DE TEXTO) */
    /* Isso força o fundo das caixas a ser branco e borda cinza, ignorando o tema escuro */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC !important;
        color: #151515 !important;
    }
    input[type="text"], input[type="number"] {
        color: #151515 !important;
    }
    
    /* Corrigir a cor do texto dentro dos selects (Dropdowns) */
    div[data-baseweb="select"] span {
        color: #151515 !important;
    }
    
    /* Corrigir cor do item selecionado no Dropdown */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background-color: #FFFFFF !important;
        color: #151515 !important;
    }

    /* 4. SIDEBAR (MENU LATERAL) - PRETO */
    section[data-testid="stSidebar"] {
        background-color: #151515 !important;
    }
    /* Textos da Sidebar Brancos */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] div { 
        color: #FFFFFF !important; 
    }
    /* Títulos da Sidebar Vermelhos */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 { 
        color: #E20A14 !important; 
    }

    /* 5. TÍTULOS GERAIS */
    h1, h2, h3, h4, h5 { 
        color: #E20A14 !important; 
        font-family: 'Helvetica', 'Arial', sans-serif; 
        font-weight: 700; 
    }
    
    /* 6. BOTÕES */
    div.stButton > button { 
        background-color: #E20A14; 
        color: white !important; 
        border-radius: 6px; 
        border: none; 
        font-weight: bold; 
    }
    div.stButton > button:hover { 
        background-color: #b30000; 
    }
    
    /* 7. SLIDERS E VÁRIOS */
    div[data-testid="stSliderTickBarMin"], 
    div[data-testid="stSliderTickBarMax"], 
    div[data-testid="stThumbValue"] { 
        color: #151515 !important; 
    }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 5px solid #E20A14; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
    }
    div[data-testid="stMetricLabel"] { color: #555555 !important; }
    div[data-testid="stMetricValue"] { color: #151515 !important; }
    </style>
""", unsafe_allow_html=True)

# Importações
try:
    from src.models import ProductInput, CustomerContext, PricingScenario, ServiceInput
    from src.pricing_engine import ProductPricer
    from src.service_engine import ServicePricer
    from config.tax_rates import TaxConstants
except ImportError as e:
    st.error(f"Erro de Importação: {e}. Verifique arquivos.")
    st.stop()

# --- OPÇÕES PADRÃO ---
IPI_OPTIONS = {"Nobreak (9.75%)": 0.0975, "Bateria (15.00%)": 0.15, "Placas (5.00%)": 0.05, "Isento (0.00%)": 0.00, "Outros (Manual)": -1}
MVA_OPTIONS = {"Nobreak (46%)": 0.46, "Placas (58%)": 0.58, "Bateria (S/ ST)": 0.00, "Outros (Manual)": -1}

# --- CABEÇALHO ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=140)
    else: st.markdown("<div style='background-color:#E20A14; color:white; padding:10px; text-align:center;'>NB Tech</div>", unsafe_allow_html=True)
with col_title:
    st.title("Sistema Integrado de Precificação")
    st.caption("v3.5 Stable | Matriz Tributária 2025/2026")

# --- MENU ---
st.sidebar.header("NAVEGAÇÃO")
page = st.sidebar.radio("Selecione a Ferramenta:", ["Precificador de Produtos", "Precificador de Serviços (Pontual)", "Precificador de Contratos (Recorrência)", "Tabelas Oficiais"])
st.sidebar.markdown("---")
st.sidebar.info("NB Tech Pricing Core")

# =========================================================
# 1. PRODUTOS (HARDWARE)
# =========================================================
if page == "Precificador de Produtos":
    st.header("📦 Precificador de Produtos")
    st.markdown("Cálculo de revenda com automação de ICMS por Estado.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados do Produto")
        prod_name = st.text_input("Descrição", "Nobreak 3kVA Online")
        ncm_code = st.text_input("NCM", "8504.40.40")
        cost_price = st.number_input("Custo de Aquisição (R$)", value=1000.00, step=10.0)
        
        c1, c2 = st.columns(2)
        ipi_sel = c1.selectbox("Selecione IPI", list(IPI_OPTIONS.keys()))
        ipi_rate = c1.number_input("Digite IPI (%)", value=0.0)/100 if ipi_sel == "Outros (Manual)" else IPI_OPTIONS[ipi_sel]

        mva_sel = c2.selectbox("Selecione MVA ST", list(MVA_OPTIONS.keys()))
        mva_st = c2.number_input("Digite MVA (%)", value=0.0)/100 if mva_sel == "Outros (Manual)" else MVA_OPTIONS[mva_sel]

        origin_uf = st.selectbox("UF Origem", TaxConstants.ESTADOS, index=TaxConstants.ESTADOS.index("SP"))

    with col2:
        st.subheader("Dados da Venda")
        dest_uf = st.selectbox("UF Destino", TaxConstants.ESTADOS, index=TaxConstants.ESTADOS.index("BA"))
        
        icms_real_state = TaxConstants.ICMS_INTERNO_ESTADOS.get(dest_uf, 0.18)
        
        icms_dest = st.number_input(
            f"ICMS Interno {dest_uf} (%)", 
            value=float(icms_real_state * 100), 
            step=0.5,
            help="Alíquota interna padrão de 2025/2026."
        ) / 100
        
        client_type = st.radio("Tipo Cliente", ["Contribuinte", "Nao_Contribuinte"])
        target_margin = st.slider("Margem Líquida (%)", 5, 50, 25) / 100

    if st.button("CALCULAR VENDA"):
        prod = ProductInput(name=prod_name, ncm=ncm_code, cost_price=cost_price, ipi_rate=ipi_rate, mva_st=mva_st, origin_uf=origin_uf)
        cli = CustomerContext(uf=dest_uf, type=client_type, internal_icms_dest=icms_dest)
        cen = PricingScenario(target_margin=target_margin)
        
        engine = ProductPricer(prod, cli, cen)
        res = engine.calculate_selling_price()
        
        st.divider()
        k1, k2, k3 = st.columns(3)
        k1.metric("Preço Sugerido", f"R$ {res['selling_price_suggested']:,.2f}")
        k2.metric("Lucro Líquido", f"R$ {res['financials']['net_profit']:,.2f}")
        k3.metric("Margem Real", f"{res['financials']['net_margin_pct']}%")
        
        with st.expander("Ver Detalhes dos Impostos (DIFAL/ST)"):
            st.write("Valores em Reais (R$):")
            st.json(res['taxes'])

# =========================================================
# 2. SERVIÇOS PONTUAIS
# =========================================================
elif page == "Precificador de Serviços (Pontual)":
    st.header("🛠️ Precificador de Serviços (Avulsos)")
    col1, col2 = st.columns(2)
    with col1:
        ups_type = st.selectbox("Equipamento", ["Monofásico (Até 3kVA)", "Monofásico (3-10kVA)", "Trifásico (10-40kVA)", "Trifásico (>40kVA)"])
        hours = st.number_input("Horas Técnicas", value=2.0)
        km = st.number_input("Distância Total (KM)", value=50.0)
    with col2:
        margin = st.slider("Margem Alvo (%)", 10, 60, 35) / 100
    if st.button("CALCULAR SERVIÇO"):
        srv = ServiceInput(service_type="Serviço Pontual (Avulso)", ups_power=ups_type, ups_type=ups_type, technical_hours_per_visit=hours, distance_km_round_trip=km, contract_duration_months=1, visits_per_year=1)
        cen = PricingScenario(target_margin=margin)
        res = ServicePricer(srv, cen).calculate_contract_price()
        st.success(f"Valor do Serviço: R$ {res['monthly_price']:,.2f}")
        st.json(res['breakdown'])

# =========================================================
# 3. CONTRATOS
# =========================================================
elif page == "Precificador de Contratos (Recorrência)":
    st.header("📜 Precificador de Contratos")
    c1, c2 = st.columns(2)
    with c1: contract_type = st.selectbox("Modalidade", ["Contrato Manutenção (Preventiva + Corretiva)", "Locação (UPS Estoque)", "Locação (Compra UPS Nova)"])
    with c2: months = st.slider("Vigência (Meses)", 1, 48, 24)
    st.divider()
    col_a, col_b, col_c, col_d = st.columns(4)
    qty_ups = col_a.number_input("Qtd. Equipamentos", min_value=1, value=1)
    qty_locais = col_b.number_input("Qtd. de Locais", min_value=1, value=1)
    ups_power = col_c.selectbox("Potência", ["1-3 kVA", "3-6 kVA", "6-10 kVA", "10-20 kVA", "20-80 kVA"])
    ups_tech = col_d.selectbox("Tecnologia", ["Shortbreak", "Senoidal", "Dupla Conversão"])
    st.subheader("Custos Operacionais")
    c_op1, c_op2, c_op3 = st.columns(3)
    hours_unit = c_op1.number_input("Horas Técnicas (por Máq/Visita)", value=1.0, step=0.5)
    km_total = c_op2.number_input("KM Total (Ida/Volta Roteiro)", value=40.0)
    visits_year = c_op3.number_input("Visitas no ANO (Total)", value=12)
    capex = 0.0
    parts = 0.0
    if "Locação" in contract_type: capex = st.number_input("Valor Unitário Compra UPS (R$)", value=5000.00)
    parts = st.number_input("Estimativa Peças (R$/Mês/Máq)", value=0.0)
    margin = st.slider("Margem Desejada (%)", 10, 50, 30) / 100
    if st.button("CALCULAR MENSALIDADE TOTAL", type="primary"):
        srv_input = ServiceInput(service_type=contract_type, ups_power=ups_power, ups_type=ups_tech, ups_quantity=qty_ups, num_locations=qty_locais, visits_per_year=visits_year, technical_hours_per_visit=hours_unit, distance_km_round_trip=km_total, equipment_capex_unit=capex, contract_duration_months=months, parts_cost_estimation_monthly=parts)
        cenario = PricingScenario(target_margin=margin)
        res = ServicePricer(srv_input, cenario).calculate_contract_price()
        st.divider()
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Mensalidade TOTAL", f"R$ {res['monthly_price']:,.2f}")
        col_res2.metric("Valor por Máquina", f"R$ {res['monthly_price']/qty_ups:,.2f}")
        col_res3.metric("Valor Global Contrato", f"R$ {res['total_contract_value']:,.2f}")
        st.bar_chart(res['breakdown'])

# =========================================================
# 4. TABELAS (COMPLETAS)
# =========================================================
elif page == "Tabelas Oficiais":
    st.header("📋 Tabelas Oficiais - Jan/2026")
    tab_lab, tab_onsite = st.tabs(["Laboratório (Balcão)", "On-Site (Visita)"])
    with tab_lab:
        st.subheader("Manutenção em Laboratório")
        df_lab = pd.DataFrame([
            {"Produto": "Shortbreak até 1kVA", "Troca Bateria": "R$ 75,00", "Com Reparo": "R$ 90,00"},
            {"Produto": "Shortbreak > 1kVA", "Troca Bateria": "R$ 90,00", "Com Reparo": "R$ 250,00"},
            {"Produto": "Shortbreak até 1kVA (Senoidal)", "Troca Bateria": "R$ 90,00", "Com Reparo": "R$ 150,00"},
            {"Produto": "Shortbreak > 1kVA (Senoidal)", "Troca Bateria": "R$ 120,00", "Com Reparo": "R$ 360,00"},
            {"Produto": "Dupla Conv. até 3kVA", "Troca Bateria": "R$ 150,00", "Com Reparo": "R$ 750,00"},
            {"Produto": "Dupla Conv. 5-10kVA", "Troca Bateria": "R$ 350,00", "Com Reparo": "R$ 1.600,00"},
            {"Produto": "Dupla Conv. > 10kVA", "Troca Bateria": "R$ 550,00", "Com Reparo": "R$ 2.200,00"},
            {"Produto": "Estabilizador até 3kVA", "Troca Bateria": "-", "Com Reparo": "R$ 90,00"}
        ])
        st.table(df_lab)
    with tab_onsite:
        st.subheader("Atendimento On-Site (Comercial)")
        df_onsite = pd.DataFrame([
            {"Nobreak": "Até 3kVA", "Preventiva": "R$ 220,00", "Corretiva": "R$ 280,00"},
            {"Nobreak": "3.1 a 6kVA (Mono)", "Preventiva": "R$ 380,00", "Corretiva": "R$ 460,00"},
            {"Nobreak": "6.1 a 10kVA (Mono)", "Preventiva": "R$ 450,00", "Corretiva": "R$ 540,00"},
            {"Nobreak": "10.1 a 20kVA (Mono)", "Preventiva": "R$ 600,00", "Corretiva": "R$ 720,00"},
            {"Nobreak": "Trifásico até 10kVA", "Preventiva": "R$ 550,00", "Corretiva": "R$ 660,00"},
            {"Nobreak": "Trifásico 10-20kVA", "Preventiva": "R$ 650,00", "Corretiva": "R$ 780,00"},
            {"Nobreak": "Trifásico 20-40kVA", "Preventiva": "R$ 900,00", "Corretiva": "R$ 1.100,00"},
            {"Nobreak": "Trifásico 40-80kVA", "Preventiva": "R$ 1.400,00", "Corretiva": "R$ 1.680,00"}
        ])
        st.table(df_onsite)
