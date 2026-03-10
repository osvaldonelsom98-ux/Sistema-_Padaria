import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MGKMJ - Gestão de Panificação", layout="wide", page_icon="🥖")

# --- DESIGN PROFISSIONAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #FFFDF5; }
    div.stButton > button:first-child {
        background-color: #D2691E; color: white; border-radius: 10px; border: none; font-weight: bold; height: 3em; transition: 0.3s;
    }
    div.stButton > button:first-child:hover { background-color: #8B4513; transform: scale(1.02); }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); border-left: 5px solid #D2691E; }
    .ticket { background: #fff; padding: 20px; border: 2px dashed #333; font-family: 'Courier New', monospace; color: #000; line-height: 1.2; }
    .header-style { background: linear-gradient(90deg, #8B4513 0%, #D2691E 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DATOS ---
def init_db():
    conn = sqlite3.connect('mgkmj_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS estoque_insumos (item TEXT PRIMARY KEY, qtd REAL, unidade TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS producao (produto TEXT, qtd_feita INTEGER, data DATE)')
    c.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY, produto TEXT, qtd INTEGER, total REAL, tipo TEXT, responsavel TEXT, data DATE, hora TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS despesas (id INTEGER PRIMARY KEY, descricao TEXT, valor REAL, data DATE)')
    
    # Insumos Iniciais
    insumos = [('Trigo', 500, 'kg'), ('Fermento Pão', 50, 'kg'), ('Fermento Bolo Keke', 20, 'kg'), ('Mortadela', 30, 'kg'), ('Asfia', 20, 'kg'), ('Coco', 15, 'kg')]
    for i, q, u in insumos:
        c.execute("INSERT OR IGNORE INTO estoque_insumos VALUES (?,?,?)", (i, q, u))
    conn.commit()
    return conn

conn = init_db()

# --- LISTAS DE PRODUTOS MGKMJ ---
PAES_SAL = {"Pão 20kz": 20, "Pão 25kz": 25, "Pão 40kz": 40, "Pão 50kz": 50, "Pão 90kz": 90, "Pão 100kz": 100, "Pão Flor (Mortadela)": 150, "Pão Jacaré": 300, "Pão Guardanapo Simples": 100}
PAES_DOCES = {"Pão Guardanapo Coco": 150, "Bolo Keke": 200, "Asfia": 150, "Bola de Berlim": 200, "Charutos de Bolinho": 100}
BEBIDAS = {"Coca-Cola": 500, "Fanta": 500, "Água Mineral": 250, "Cerveja": 600}

# --- LOGIN ---
if 'perfil' not in st.session_state: st.session_state['perfil'] = None
if 'user' not in st.session_state: st.session_state['user'] = ""

def login_screen():
    st.markdown('<div class="header-style"><h1>🥖 MGKMJ - Panificadora & Pastelaria</h1><p>Sistema de Gestão Profissional</p></div>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3014/3014534.png", width=120)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        perfil = st.selectbox("Escolha seu Cargo", ["Gerente", "Produção", "Balconista"])
        nome = st.text_input("Seu Nome")
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("ENTRAR NO SISTEMA"):
            if (perfil == "Gerente" and senha == "admin") or (perfil == "Produção" and senha == "pao") or (perfil == "Balconista" and senha == "venda"):
                st.session_state['perfil'] = perfil
                st.session_state['user'] = nome
                st.rerun()
            else: st.error("Acesso Negado: Verifique a senha.")

if not st.session_state['perfil']:
    login_screen()
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/992/992743.png", width=80)
    st.write(f"Sessão: **{st.session_state['user']}**")
    
    if st.session_state['perfil'] == "Gerente":
        menu = option_menu("Gestão MGKMJ", ["Dashboard", "Estoque & Insumos", "Despesas Fixas"], 
            icons=['graph-up-arrow', 'box-seam', 'cash-coin'], menu_icon="shield-lock", default_index=0)
    elif st.session_state['perfil'] == "Produção":
        menu = option_menu("Produção", ["Lançar Fornada", "Uso de Trigo/Insumos", "Venda Grosso"], 
            icons=['fire', 'basket2', 'truck'], menu_icon="tools", default_index=0)
    else:
        menu = option_menu("Balcão", ["Receber Pães", "Vender (PDV)", "Final de Turno"], 
            icons=['arrow-down-circle', 'cart-check', 'clock-history'], menu_icon="shop", default_index=0)

    if st.button("🚪 Sair"):
        st.session_state['perfil'] = None
        st.rerun()

# --- LÓGICA DAS TELAS ---

# 1. GERENTE (DASHBOARD E DESPESAS)
if menu == "Dashboard":
    st.markdown("### 📊 Visão Geral do Negócio")
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    df_d = pd.read_sql("SELECT * FROM despesas", conn)
    
    col1, col2, col3, col4 = st.columns(4)
    receita = df_v['total'].sum() if not df_v.empty else 0
    custo = df_d['valor'].sum() if not df_d.empty else 0
    
    col1.metric("Receita Total", f"{receita:,.2f} Kz")
    col2.metric("Despesas Totais", f"{custo:,.2f} Kz", delta_color="inverse")
    col3.metric("Lucro Líquido", f"{(receita - custo):,.2f} Kz")
    col4.metric("Vendas Realizadas", len(df_v))

    st.subheader("Vendas por Produto (Top 5)")
    if not df_v.empty:
        fig = px.bar(df_v.groupby('produto')['total'].sum().reset_index().sort_values('total', ascending=False).head(5), 
                     x='produto', y='total', color='total', color_continuous_scale='Oranges')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Despesas Fixas":
    st.markdown("### 💸 Gestão de Custos (Água, Luz, Aluguel)")
    with st.form("form_despesa"):
        desc = st.selectbox("Tipo de Despesa", ["Água", "Energia Elétrica", "Aluguel", "Salários", "Manutenção", "Outros"])
        val = st.number_input("Valor Pago (Kz)", min_value=0.0)
        if st.form_submit_button("Registrar Pagamento"):
            conn.execute("INSERT INTO despesas (descricao, valor, data) VALUES (?,?,?)", (desc, val, datetime.now().date()))
            conn.commit()
            st.success("Despesa registrada!")
    
    st.table(pd.read_sql("SELECT * FROM despesas ORDER BY data DESC", conn))

# 2. PRODUÇÃO
elif menu == "Lançar Fornada":
    st.markdown("### 🔥 Registro de Produção Diária")
    with st.form("prod"):
        item_p = st.selectbox("Produto Fabricado", list(PAES_SAL.keys()) + list(PAES_DOCES.keys()))
        qtd_p = st.number_input("Quantidade Produzida", min_value=1)
        if st.form_submit_button("Confirmar Fornada"):
            conn.execute("INSERT INTO producao VALUES (?,?,?)", (item_p, qtd_p, datetime.now().date()))
            conn.commit()
            st.success(f"Fornada de {qtd_p} {item_p} pronta!")

elif menu == "Uso de Trigo/Insumos":
    st.markdown("### 🌾 Consumo de Matéria-Prima")
    insumo = st.selectbox("O que foi usado hoje?", ["Trigo", "Fermento Pão", "Fermento Bolo Keke", "Mortadela", "Asfia", "Coco"])
    qtd_u = st.number_input("Quantidade (kg)", min_value=0.1)
    if st.button("Confirmar Uso"):
        conn.execute("UPDATE estoque_insumos SET qtd = qtd - ? WHERE item = ?", (qtd_u, insumo))
        conn.commit()
        st.warning(f"Baixa de {qtd_u}kg de {insumo} realizada.")

# 3. BALCONISTA
elif menu == "Vender (PDV)":
    st.markdown("### 🛒 Ponto de Venda MGKMJ")
    colA, colB = st.columns([2,1])
    with colA:
        cat = st.radio("Escolha a Categoria", ["Pão Sal", "Pão Doce", "Bebidas"], horizontal=True)
        lista = PAES_SAL if cat == "Pão Sal" else (PAES_DOCES if cat == "Pão Doce" else BEBIDAS)
        p_sel = st.selectbox("Produto", list(lista.keys()))
        q_sel = st.number_input("Quantidade", min_value=1, value=1)
        total = lista[p_sel] * q_sel
        st.markdown(f"## Total: **{total:,.2f} Kz**")
        
    with colB:
        st.image("https://cdn-icons-png.flaticon.com/512/1611/1611733.png", width=150)
        if st.button("📥 FINALIZAR E IMPRIMIR"):
            data_v = datetime.now().date()
            hora_v = datetime.now().strftime("%H:%M:%S")
            conn.execute("INSERT INTO vendas (produto, qtd, total, tipo, responsavel, data, hora) VALUES (?,?,?,?,?,?,?)",
                         (p_sel, q_sel, total, 'Varejo', st.session_state['user'], data_v, hora_v))
            conn.commit()
            st.success("Venda Concluída!")
            
            # TICKET DE IMPRESSÃO
            st.markdown(f"""
            <div class="ticket">
                <center><b>MGKMJ PANIFICADORA</b><br>TICKET DE VENDA</center><br>
                DATA: {data_v}  HORA: {hora_v}<br>
                VENDEDOR: {st.session_state['user']}<br>
                --------------------------<br>
                PROD: {p_sel}<br>
                QTD:  {q_sel}<br>
                VALOR UN: {lista[p_sel]:,.2f} Kz<br>
                --------------------------<br>
                <b>TOTAL: {total:,.2f} Kz</b><br><br>
                <center>OBRIGADO E VOLTE SEMPRE!</center>
            </div>
            <p style='text-align:center'>Use <b>Ctrl+P</b> para imprimir o recibo.</p>
            """, unsafe_allow_html=True)

elif menu == "Final de Turno":
    st.markdown("### 📝 Fechamento de Caixa e Restantes")
    prod_r = st.selectbox("Produto que Sobrou", list(PAES_SAL.keys()) + list(PAES_DOCES.keys()))
    qtd_r = st.number_input("Quantidade na Vitrine", min_value=0)
    if st.button("Salvar Sobra Diária"):
        st.success(f"Registrado: {qtd_r} unidades de {prod_r} em estoque no balcão.")

elif menu == "Estoque & Insumos":
    st.markdown("### 📦 Controle de Armazém")
    df_e = pd.read_sql("SELECT * FROM estoque_insumos", conn)
    st.table(df_e)
    with st.expander("Repor Matéria-Prima"):
        item_repo = st.selectbox("Item", df_e['item'])
        qtd_repo = st.number_input("Qtd Adicionada (kg)", min_value=1.0)
        if st.button("Adicionar ao Estoque"):
            conn.execute("UPDATE estoque_insumos SET qtd = qtd + ? WHERE item = ?", (qtd_repo, item_repo))
            conn.commit()
            st.rerun()
