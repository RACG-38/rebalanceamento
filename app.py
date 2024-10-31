import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Inicializa ou carrega o DataFrame de fundos
try:
    df_fundos = pd.read_csv("fundos_cadastrados.csv")
    if "Carteira" not in df_fundos.columns:
        df_fundos["Carteira"] = ""
except FileNotFoundError:
    df_fundos = pd.DataFrame(columns=["Nome", "Valor Investido", "Valor Mínimo de Aplicação", "Valor Mínimo de Permanência", "Status", "Classe", "Categoria", "Carteira"])

# Função para salvar fundos no arquivo
def salvar_fundos():
    df_fundos.to_csv("fundos_cadastrados.csv", index=False)
    st.success("Dados salvos em fundos_cadastrados.csv")

# Função para limpar os campos do formulário
def limpar_campos():
    st.session_state.nome = ""
    st.session_state.valor_investido = 0.0
    st.session_state.valor_min_aplicacao = 0.0
    st.session_state.valor_min_permanencia = 0.0
    st.session_state.status = "ABERTO"
    st.session_state.classe = "Estabilidade"
    st.session_state.categoria = "Baunilha"
    st.session_state.carteira = "Mari"

# Interface de cadastro de fundos
st.title("Cadastro e Rebalanceamento de Fundos de Investimento")

# Sidebar para cadastro de fundos
st.sidebar.header("Cadastrar Novo Fundo")
nome = st.sidebar.text_input("Nome do Fundo", key="nome")
valor_investido = st.sidebar.number_input("Valor Investido", min_value=0.0, format="%.2f", key="valor_investido")
valor_min_aplicacao = st.sidebar.number_input("Valor Mínimo de Aplicação", min_value=0.0, format="%.2f", key="valor_min_aplicacao")
valor_min_permanencia = st.sidebar.number_input("Valor Mínimo de Permanência", min_value=0.0, format="%.2f", key="valor_min_permanencia")
status = st.sidebar.selectbox("Status", ["ABERTO", "FECHADO"], key="status")

# Seleção da classe, categoria e carteira
classe = st.sidebar.selectbox("Classe", ["Estabilidade", "Diversificação", "Valorização", "Antifragilidade"], key="classe")
categoria = st.sidebar.selectbox("Categoria", {
    "Estabilidade": ["Baunilha", "Pimentinha"],
    "Diversificação": ["Infraestrutura", "Ex-Tesoureiros", "Pimentinha", "Viés Global", "Viés Macro"],
    "Valorização": ["Pimentinha", "Qualidade", "Viés Comprado", "Perfil Global", "Fora do Radar"],
    "Antifragilidade": [""]  # Adicione categorias para Antifragilidade, se necessário
}[classe], key="categoria")
carteira = st.sidebar.selectbox("Carteira", ["Mari", "Marcio"], key="carteira")

# Botão para adicionar o fundo
if st.sidebar.button("Adicionar Fundo"):
    novo_fundo = pd.DataFrame({
        "Nome": [nome],
        "Valor Investido": [valor_investido],
        "Valor Mínimo de Aplicação": [valor_min_aplicacao],
        "Valor Mínimo de Permanência": [valor_min_permanencia],
        "Status": [status],
        "Classe": [classe],
        "Categoria": [categoria],
        "Carteira": [carteira]
    })
    df_fundos = pd.concat([df_fundos, novo_fundo], ignore_index=True)
    salvar_fundos()
    limpar_campos()  # Limpa os campos após salvar o fundo

# Seleção de qual carteira balancear
st.header("Selecione a Carteira para Balancear")
carteira_selecionada = st.selectbox("Carteira", ["Mari", "Marcio"], key="carteira_selecionada")

# Filtra o DataFrame pela carteira selecionada
df_fundos_filtrado = df_fundos[df_fundos["Carteira"] == carteira_selecionada]

# Exibir os fundos cadastrados para a carteira selecionada
st.header(f"Fundos Cadastrados - Carteira {carteira_selecionada}")
st.dataframe(df_fundos_filtrado)

# Função de rebalanceamento
def calcular_rebalanceamento(df_fundos, aporte=0):
    # Alocações alvo para cada classe e categoria
    alocacao_classe = {
        "Estabilidade": 0.225,
        "Diversificação": 0.4,
        "Valorização": 0.3,
        "Antifragilidade": 0.075
    }

    # Filtra apenas fundos abertos
    df_abertos = df_fundos[df_fundos["Status"] == "ABERTO"]

    # Calcula o valor total investido atualmente
    valor_total_investido = df_abertos["Valor Investido"].sum() + aporte

    # Cálculo de rebalanceamento por classe
    resultados = []
    for classe, porcentagem in alocacao_classe.items():
        valor_alvo_classe = valor_total_investido * porcentagem
        fundos_classe = df_abertos[df_abertos["Classe"] == classe]
        valor_atual_classe = fundos_classe["Valor Investido"].sum()
        diferenca_classe = valor_alvo_classe - valor_atual_classe

        for idx, fundo in fundos_classe.iterrows():
            proporcao_fundo = fundo["Valor Investido"] / valor_atual_classe if valor_atual_classe > 0 else 0
            ajuste_fundo = diferenca_classe * proporcao_fundo
            valor_ajuste = round(ajuste_fundo, 0)
            if abs(valor_ajuste) >= fundo["Valor Mínimo de Aplicação"]:
                resultados.append((fundo["Nome"], classe, fundo["Valor Investido"], valor_ajuste))
    
    return pd.DataFrame(resultados, columns=["Fundo", "Classe", "Valor Investido", "Ajuste Necessário (R$)"])

# Entrada para o valor de aporte
aporte = st.number_input("Valor de Aporte", min_value=0.0, format="%.2f", key="aporte")

# Botão para calcular o rebalanceamento
if st.button("Calcular Rebalanceamento"):
    st.session_state.df_rebalanceamento = calcular_rebalanceamento(df_fundos_filtrado, aporte=aporte)

# Verifica se já existe um resultado de rebalanceamento calculado
if 'df_rebalanceamento' in st.session_state:
    df_rebalanceamento = st.session_state.df_rebalanceamento
    st.header("Resultados do Rebalanceamento")

    # Filtro para ajustar positivamente ou negativamente
    ajuste_tipo = st.selectbox("Filtrar Ajustes", ["Todos", "Ajustes Positivos", "Ajustes Negativos"], key="ajuste_tipo")
    if ajuste_tipo == "Ajustes Positivos":
        df_rebalanceamento = df_rebalanceamento[df_rebalanceamento["Ajuste Necessário (R$)"] > 0]
    elif ajuste_tipo == "Ajustes Negativos":
        df_rebalanceamento = df_rebalanceamento[df_rebalanceamento["Ajuste Necessário (R$)"] < 0]

    # Aplicar cores para os valores de ajuste
    def colorir_ajuste(val):
        if val > 0:
            return 'color: green'
        elif val < 0:
            return 'color: red'
        else:
            return 'color: black'

    st.dataframe(df_rebalanceamento.style.applymap(colorir_ajuste, subset=["Ajuste Necessário (R$)"]))

    # Gráficos de donut com a alocação atual e após o rebalanceamento
    st.header("Gráficos de Alocação por Classe")

    # Alocação atual por classe
    alocacao_atual = df_fundos_filtrado[df_fundos_filtrado["Status"] == "ABERTO"].groupby("Classe")["Valor Investido"].sum()
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    fig1.patch.set_facecolor('#0e1117')  # Define o fundo do gráfico para corresponder ao fundo da tela do Streamlit
    ax1.set_facecolor('#0e1117')
    wedges, texts, autotexts = ax1.pie(alocacao_atual, labels=alocacao_atual.index, autopct='%1.1f%%', startangle=140, wedgeprops={'width': 0.3, 'edgecolor': 'w'}, colors=plt.cm.Paired.colors)
    plt.setp(autotexts, size=12, weight="bold", color="white")
    plt.setp(texts, size=14, weight="bold", color="white")
    ax1.set_title(f"Alocação Atual por Classe - Carteira {carteira_selecionada}", fontsize=16, weight="bold", color="white")
    st.pyplot(fig1)

    # Alocação após o rebalanceamento
    df_rebalanceamento_agrupado = df_rebalanceamento.groupby("Classe")["Ajuste Necessário (R$)"].sum()
    nova_alocacao = alocacao_atual.add(df_rebalanceamento_agrupado, fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    fig2.patch.set_facecolor('#0e1117')
    ax2.set_facecolor('#0e1117')
    wedges, texts, autotexts = ax2.pie(nova_alocacao, labels=nova_alocacao.index, autopct='%1.1f%%', startangle=140, wedgeprops={'width': 0.3, 'edgecolor': 'w'}, colors=plt.cm.Paired.colors)
    plt.setp(autotexts, size=12, weight="bold", color="white")
    plt.setp(texts, size=14, weight="bold", color="white")
    ax2.set_title(f"Nova Alocação por Classe - Carteira {carteira_selecionada}", fontsize=16, weight="bold", color="white")
    st.pyplot(fig2)
