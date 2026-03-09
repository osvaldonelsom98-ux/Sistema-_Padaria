import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Padaria Master - Gestão", layout="wide")

# --- BANCO DE DATOS ---
def init_db():
    conn = sqlite3.connect('padaria_sistema.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela de Balconistas
    c.execute('CREATE TABLE IF NOT EXISTS balconistas (id INTEGER PRIMARY KEY, nome TEXT UNIQUE)')
    # Tabela de Produtos
    c.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT UNIQUE, preco REAL)')
    # Tabela de Vendas
    c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY, produto TEXT, qtd INTEGER, total REAL, balconista TEXT, data DATE)''')
    
    # Inserção inicial se estiver vazio
    c.execute("SELECT COUNT(*) FROM balconistas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO balconistas (nome) VALUES ('Balconista 1'), ('Balconista 2')")
        c.execute("INSERT INTO produtos (nome, preco) VALUES ('Pão Francês', 1.00), ('Pão de Queijo', 4.50)")
    conn.commit()
    return conn

conn = init_db()

# --- SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("🔐 Acesso ao Sistema")
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and pw == "1234": # Altere aqui sua senha inicial
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if not st.session_state['logged_in']:
    login()
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.sidebar.title("🍞 Padaria Master")
menu = st.sidebar.selectbox("Navegação", ["Dashboard", "Vendas (PDV)", "Gerenciamento", "Relatório Diário"])

if st.sidebar.button("Sair"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- MÓDULO: DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Painel de Controle")
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    
    if not df_vendas.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Total", f"R$ {df_vendas['total'].sum():.2f}")
        col2.metric("Vendas Realizadas", len(df_vendas))
        col3.metric("Média por Venda", f"R$ {df_vendas['total'].mean():.2f}")
        
        st.subheader("Desempenho por Balconista")
        st.bar_chart(df_vendas.groupby('balconista')['total'].sum())
    else:
        st.info("Aguardando primeiras vendas do dia.")

# --- MÓDULO: VENDAS (PDV) ---
elif menu == "Vendas (PDV)":
    st.title("🛒 Frente de Caixa")
    
    # Busca dados atualizados do banco
    prods_df = pd.read_sql("SELECT nome, preco FROM produtos", conn)
    balcs_df = pd.read_sql("SELECT nome FROM balconistas", conn)
    
    with st.form("venda_rapida"):
        c1, c2, c3 = st.columns(3)
        p_nome = c1.selectbox("Produto", prods_df['nome'])
        p_qtd = c2.number_input("Qtd", min_value=1, value=1)
        p_balc = c3.selectbox("Vendido por", balcs_df['nome'])
        
        if st.form_submit_button("CONCLUIR VENDA"):
            preco_un = prods_df[prods_df['nome'] == p_nome]['preco'].values[0]
            total = preco_un * p_qtd
            data = datetime.now().strftime("%Y-%m-%d")
            
            conn.execute("INSERT INTO vendas (produto, qtd, total, balconista, data) VALUES (?,?,?,?,?)",
                         (p_nome, p_qtd, total, p_balc, data))
            conn.commit()
            st.success("Venda salva!")

# --- MÓDULO: GERENCIAMENTO (ONDE VOCÊ ALTERA TUDO) ---
elif menu == "Gerenciamento":
    st.title("⚙️ Gerenciar Recursos")
    st.info("Aqui você altera balconistas e produtos sem mexer no código.")
    
    tab1, tab2 = st.tabs(["Funcionários (Balconistas)", "Produtos e Preços"])
    
    with tab1:
        st.subheader("Lista de Balconistas")
        df_balc = pd.read_sql("SELECT * FROM balconistas", conn)
        # Tabela editável: você pode clicar e mudar o nome, ou adicionar linha
        edit_balc = st.data_editor(df_balc, num_rows="dynamic", key="edit_balc")
        
        if st.button("Salvar Alterações de Balconistas"):
            conn.execute("DELETE FROM balconistas") # Limpa para atualizar
            for _, row in edit_balc.iterrows():
                if row['nome']:
                    conn.execute("INSERT INTO balconistas (nome) VALUES (?)", (row['nome'],))
            conn.commit()
            st.success("Lista de funcionários atualizada!")

    with tab2:
        st.subheader("Catálogo de Produtos")
        df_prod = pd.read_sql("SELECT * FROM produtos", conn)
        edit_prod = st.data_editor(df_prod, num_rows="dynamic", key="edit_prod")
        
        if st.button("Salvar Alterações de Produtos"):
            conn.execute("DELETE FROM produtos")
            for _, row in edit_prod.iterrows():
                if row['nome']:
                    conn.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (row['nome'], row['preco']))
            conn.commit()
            st.success("Catálogo e preços atualizados!")

# --- MÓDULO: RELATÓRIO DIÁRIO ---
elif menu == "Relatório Diário":
    st.title("🖨️ Relatório Diário")
    data_sel = st.date_input("Escolha a data", datetime.now())
    df_dia = pd.read_sql(f"SELECT * FROM vendas WHERE data = '{data_sel}'", conn)
    
    if not df_dia.empty:
        st.write(f"### Vendas de {data_sel}")
        st.table(df_dia[['balconista', 'produto', 'qtd', 'total']])
        st.metric("Total do Dia", f"R$ {df_dia['total'].sum():.2f}")
        st.write("Dica: Use Ctrl+P para imprimir esta página.")
    else:
        st.warning("Nenhuma venda nesta data.")
