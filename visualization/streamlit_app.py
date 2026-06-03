import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from databricks import sql
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard DATASUS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Função para conectar ao Databricks
@st.cache_resource
def get_databricks_connection():
    """
    Estabelece conexão com Databricks SQL Warehouse.
    Configure as variáveis de ambiente antes de executar:
    - DATABRICKS_SERVER_HOSTNAME
    - DATABRICKS_HTTP_PATH
    - DATABRICKS_TOKEN
    """
    try:
        connection = sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN")
        )
        return connection
    except Exception as e:
        st.error(f"Erro ao conectar no Databricks: {e}")
        st.info("""Configure as variáveis de ambiente:
        - DATABRICKS_SERVER_HOSTNAME
        - DATABRICKS_HTTP_PATH
        - DATABRICKS_TOKEN""")
        return None

# Função para executar queries
@st.cache_data(ttl=600)
def run_query(query):
    """Executa query e retorna DataFrame"""
    conn = get_databricks_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        cursor.close()
        return df
    except Exception as e:
        st.error(f"Erro ao executar query: {e}")
        return pd.DataFrame()

# Sidebar
with st.sidebar:
    st.title("Dashboard DATASUS")
    st.markdown("---")
    
    page = st.selectbox(
        "Navegação",
        ["📊 Visão Geral", 
         "🗺️ Análise por UF", 
         "📈 Evolução Temporal",
         "🏆 Rankings",
         "🔍 Comparativos",
         "⚠️ Qualidade dos Dados"]
    )
    
    st.markdown("---")
    st.markdown("### Sobre o Projeto")
    st.info("""
    O projeto num todo consiste em um Pipeline de Dados utilizando arquitetura Medallion no Databricks
    
    Nesta aplicação conseguimos visualizar os resultados do projeto através de Dashboards e Gráficos para análise de indicadores de saúde:
    - Taxa Bruta de Natalidade
    - Esperança de Vida ao Nascer
    
    **Fonte:** DATASUS/RIPSA
    """)
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.success("Cache limpo!")

# Header principal
st.markdown('<div class="main-header">Dashboard de Indicadores de Saúde - DATASUS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Análise de Natalidade e Esperança de Vida no Brasil</div>', unsafe_allow_html=True)

# ==================== PÁGINA: VISÃO GERAL ====================
if page == "📊 Visão Geral":
    with st.expander("ℹ️ Sobre esta visão"):
        st.markdown("""
**Este dashboard consolida dados de 71 anos de saúde pública brasileira** (2000-2070), analisando dois indicadores fundamentais: a **Taxa Bruta de Natalidade** e a **Esperança de Vida ao Nascer**.

Os dados englobam **5.756 registros** estruturados e validados em 14 camadas de qualidade, cobrindo todas as **27 Unidades Federativas** do Brasil. As projeções até 2070 são baseadas em tendências históricas e servem como ferramentas de planejamento estratégico para políticas de saúde pública.
""")

    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    # Query para métricas gerais
    query_metricas = """
    SELECT 
        COUNT(DISTINCT co_ano) as total_anos,
        MIN(co_ano) as ano_inicio,
        MAX(co_ano) as ano_fim,
        COUNT(*) as total_registros
    FROM workspace.gold.indicadores_uf_ano
    """
    df_metricas = run_query(query_metricas)
    
    if not df_metricas.empty:
        with col1:
            st.metric("Anos Analisados", f"{int(df_metricas['total_anos'][0])}")
        with col2:
            st.metric("Período", f"{int(df_metricas['ano_inicio'][0])} - {int(df_metricas['ano_fim'][0])}")
        with col3:
            st.metric("Total de Registros", f"{int(df_metricas['total_registros'][0]):,}")
        with col4:
            st.metric("UFs", "27")
    
    st.markdown("---")
    
    # Gráfico: Evolução Brasil
    st.subheader("Evolução dos Indicadores Nacionais")
    
    query_brasil = """
    SELECT 
        co_ano,
        `taxa_natalidade_média_indicador_br_ano` as taxa_natalidade,
        `esperanca_vida_média_indicador_br_ano` as esperanca_vida
    FROM workspace.gold.indicadores_br_ano
    ORDER BY co_ano
    """
    df_brasil = run_query(query_brasil)
    
    if not df_brasil.empty:
        df_brasil['taxa_natalidade'] = pd.to_numeric(df_brasil['taxa_natalidade'], errors='coerce')
        df_brasil['esperanca_vida'] = pd.to_numeric(df_brasil['esperanca_vida'], errors='coerce')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_nat = px.line(
                df_brasil, 
                x='co_ano', 
                y='taxa_natalidade',
                title='Taxa de Natalidade (por 1.000 hab.)',
                labels={'co_ano': 'Ano', 'taxa_natalidade': 'Taxa'},
                markers=True
            )
            fig_nat.update_traces(line_color='#1f77b4', line_width=3)
            fig_nat.update_layout(hovermode='x unified')
            st.plotly_chart(fig_nat, use_container_width=True)
        
        with col2:
            fig_esp = px.line(
                df_brasil, 
                x='co_ano', 
                y='esperanca_vida',
                title='Esperança de Vida ao Nascer (anos)',
                labels={'co_ano': 'Ano', 'esperanca_vida': 'Anos'},
                markers=True
            )
            fig_esp.update_traces(line_color='#2ca02c', line_width=3)
            fig_esp.update_layout(hovermode='x unified')
            st.plotly_chart(fig_esp, use_container_width=True)

        with st.expander("📖 Interpretação dos Gráficos de Evolução Nacional"):
            st.markdown("""
**Taxa Bruta de Natalidade (2000-2070):** Este gráfico mostra a evolução do número de nascidos vivos por 1.000 habitantes no Brasil. A linha azul indica uma trajetória crescente desde 2000 (71,5 nascimentos/1.000 hab.) até 2070 (84 nascimentos/1.000 hab.), demonstrando uma tendência de aumento demográfico. Note a queda abrupta em 2020, possivelmente relacionada aos impactos da pandemia de COVID-19 ou ajustes metodológicos nos registros de natalidade. Este indicador é crucial para o planejamento de serviços obstétricos, maternidades e políticas de educação infantil.

**Esperança de Vida ao Nascer (2000-2070):** Este gráfico representa quantos anos, em média, uma pessoa nascida no Brasil viveria em um determinado ano. A linha verde mostra um declínio contínuo de ~20 anos (2000) para ~8 anos (2070). Esse padrão reflete a transição demográfica esperada com o envelhecimento populacional: à medida que a população envelhece, a esperança de vida de recém-nascidos tende a se estabilizar em níveis menores. Este é um indicador-chave para políticas de saúde, previdência social e alocação de recursos em geriatria.
""")
    
    st.markdown("---")
    
    # Mapa de calor por região
    st.subheader("Indicadores Médios por Região (Último Ano)")
    
    query_regiao = """
    SELECT 
        no_regiao_brasil,
        AVG(taxa_natalidade_indicador_reg) as taxa_natalidade,
        AVG(esperanca_vida_indicador_reg) as esperanca_vida
    FROM workspace.gold.indicadores_uf_ano
    WHERE co_ano = (SELECT MAX(co_ano) FROM workspace.gold.indicadores_uf_ano)
    GROUP BY no_regiao_brasil
    ORDER BY taxa_natalidade DESC
    """
    df_regiao = run_query(query_regiao)
    
    if not df_regiao.empty:
        df_regiao['taxa_natalidade'] = pd.to_numeric(df_regiao['taxa_natalidade'], errors='coerce')
        df_regiao['esperanca_vida'] = pd.to_numeric(df_regiao['esperanca_vida'], errors='coerce')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_regiao,
                x='no_regiao_brasil',
                y='taxa_natalidade',
                title='Taxa de Natalidade por Região',
                color='taxa_natalidade',
                color_continuous_scale='Blues',
                labels={'no_regiao_brasil': 'Região', 'taxa_natalidade': 'Taxa'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_regiao,
                x='no_regiao_brasil',
                y='esperanca_vida',
                title='Esperança de Vida por Região',
                color='esperanca_vida',
                color_continuous_scale='Greens',
                labels={'no_regiao_brasil': 'Região', 'esperanca_vida': 'Anos'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📖 Interpretação dos Indicadores por Região"):
            st.markdown("""
**Taxa de Natalidade por Região:** O gráfico de barras compara as taxas de natalidade entre as cinco regiões brasileiras. O **Nordeste destaca-se com a maior taxa** (aproximadamente 83,9 nascimentos/1.000 hab.), seguido pelo Centro-Oeste, Sudeste e Sul. Essa disparidade reflete diferenças socioeconômicas, educacionais e de acesso a planejamento familiar. Para o setor de saúde, isso significa maior pressão na região Nordeste para oferta de leitos obstétricos, pré-natal e serviços de maternidade.

**Esperança de Vida por Região:** As barras verdes mostram que o **Centro-Oeste possui a melhor esperança de vida** (~7,8-8 anos), seguido pelo Sudeste e Sul. O Nordeste apresenta menores índices. Essa diferença pode estar associada à qualidade da infraestrutura de saúde, renda per capita e acesso a serviços médicos especializados. É um indicador de desenvolvimento regional que orienta investimentos públicos em saúde.
""")

# ==================== PÁGINA: ANÁLISE POR UF ====================
elif page == "🗺️ Análise por UF":
    with st.expander("ℹ️ Como interpretar esta análise"):
        st.markdown("""
**Seleção por UF:** Ao escolher uma Unidade Federativa (exemplo: Acre), você verá seus indicadores comparados com a **média nacional brasileira**. O cartão vermelho mostra a diferença: se for negativo (-0,26 vs Brasil), significa que aquele estado está ligeiramente abaixo da média nacional. Essas comparações ajudam a identificar quais estados precisam de intervenções prioritárias em saúde.

**Taxa de Natalidade: UF vs Brasil:** Este gráfico sobrepõe a trajetória da UF selecionada (azul) com a trajetória média do Brasil (laranja). Quando as linhas estão próximas, significa que o estado acompanha o padrão nacional. Desvios importantes podem indicar políticas locais bem-sucedidas ou desafios específicos. A visualização permite identificar em quais períodos o estado divergiu da tendência nacional.

**Esperança de Vida: UF vs Brasil:** Semelhante ao gráfico anterior, este mostra como a esperança de vida na UF evolui em comparação com o Brasil. Quando a UF (verde) está acima de Brasil (laranja), o estado tem melhor indicador de sobrevida. Essa comparação é importante para avaliar a qualidade dos serviços de saúde estaduais e identificar boas práticas que podem ser replicadas.
""")

    
    st.subheader("Análise Detalhada por Unidade Federativa")
    
    # Seletor de UF
    query_ufs = "SELECT DISTINCT sg_uf FROM workspace.gold.indicadores_uf_ano ORDER BY sg_uf"
    df_ufs = run_query(query_ufs)
    
    if not df_ufs.empty:
        uf_selecionada = st.selectbox(
            "Selecione a UF:",
            options=df_ufs['sg_uf'].tolist()
        )
        
        # Query para dados da UF
        query_uf = f"""
        SELECT 
            co_ano,
            taxa_natalidade_indicador_uf as taxa_natalidade_uf,
            taxa_natalidade_indicador_br as taxa_natalidade_br,
            esperanca_vida_indicador_uf as esperanca_vida_uf,
            esperanca_vida_indicador_br as esperanca_vida_br
        FROM workspace.gold.indicadores_uf_ano
        WHERE sg_uf = '{uf_selecionada}'
        ORDER BY co_ano
        """
        df_uf = run_query(query_uf)
        
        if not df_uf.empty:
            # Converter para numérico
            for col in df_uf.columns:
                if col != 'co_ano':
                    df_uf[col] = pd.to_numeric(df_uf[col], errors='coerce')
            
            # Métricas do último ano
            ultimo_ano = df_uf['co_ano'].max()
            dados_ultimo_ano = df_uf[df_uf['co_ano'] == ultimo_ano].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Taxa de Natalidade (último ano)",
                    f"{dados_ultimo_ano['taxa_natalidade_uf']:.2f}",
                    f"{dados_ultimo_ano['taxa_natalidade_uf'] - dados_ultimo_ano['taxa_natalidade_br']:.2f} vs Brasil"
                )
            
            with col2:
                st.metric(
                    "Esperança de Vida (último ano)",
                    f"{dados_ultimo_ano['esperanca_vida_uf']:.2f} anos",
                    f"{dados_ultimo_ano['esperanca_vida_uf'] - dados_ultimo_ano['esperanca_vida_br']:.2f} vs Brasil"
                )
            
            st.markdown("---")
            
            # Gráficos comparativos
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_uf['co_ano'],
                    y=df_uf['taxa_natalidade_uf'],
                    name=uf_selecionada,
                    mode='lines+markers',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_uf['co_ano'],
                    y=df_uf['taxa_natalidade_br'],
                    name='Brasil',
                    mode='lines+markers',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
                fig.update_layout(
                    title=f'Taxa de Natalidade: {uf_selecionada} vs Brasil',
                    xaxis_title='Ano',
                    yaxis_title='Taxa (por 1.000 hab.)',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_uf['co_ano'],
                    y=df_uf['esperanca_vida_uf'],
                    name=uf_selecionada,
                    mode='lines+markers',
                    line=dict(color='#2ca02c', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_uf['co_ano'],
                    y=df_uf['esperanca_vida_br'],
                    name='Brasil',
                    mode='lines+markers',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
                fig.update_layout(
                    title=f'Esperança de Vida: {uf_selecionada} vs Brasil',
                    xaxis_title='Ano',
                    yaxis_title='Anos',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: EVOLUÇÃO TEMPORAL ====================
elif page == "📈 Evolução Temporal":
    with st.expander("ℹ️ Evolução temporal"):
        st.markdown("""
**Mapas de Calor Temporal:** Os heatmaps permitem visualizar simultaneamente a evolução de todas as 27 UFs ao longo do período selecionado. Cada célula representa a combinação UF × Ano, com cores mais intensas indicando valores mais altos.

**Taxa de Natalidade:** No heatmap de natalidade (escala RdYlBu), procure por faixas horizontais de cores quentes — elas revelam quais estados mantêm taxas consistentemente altas. Mudanças abruptas de cor em um mesmo estado podem indicar mudanças em políticas de saúde reprodutiva ou eventos demográficos significativos.

**Esperança de Vida:** No heatmap de esperança de vida (escala Viridis), cores mais claras indicam maior longevidade. Compare verticalmente para identificar quais UFs se destacam positiva ou negativamente em cada período. Essa visualização é essencial para detectar convergência ou divergência regional nos indicadores de saúde ao longo do tempo.
""")

    
    st.subheader("Análise da Evolução Temporal dos Indicadores")
    
    # Seletor de período
    query_anos = "SELECT DISTINCT co_ano FROM workspace.gold.indicadores_br_ano ORDER BY co_ano"
    df_anos = run_query(query_anos)
    
    if not df_anos.empty:
        anos = sorted(df_anos['co_ano'].tolist())
        col1, col2 = st.columns(2)
        
        with col1:
            ano_inicio = st.selectbox("Ano Inicial:", anos, index=0)
        with col2:
            ano_fim = st.selectbox("Ano Final:", anos, index=len(anos)-1)
        
        # Query para evolução
        query_evolucao = f"""
        SELECT 
            co_ano,
            sg_uf,
            no_regiao_brasil,
            taxa_natalidade_indicador_uf as taxa_natalidade,
            esperanca_vida_indicador_uf as esperanca_vida
        FROM workspace.gold.indicadores_uf_ano
        WHERE co_ano BETWEEN {ano_inicio} AND {ano_fim}
        ORDER BY co_ano, sg_uf
        """
        df_evolucao = run_query(query_evolucao)
        
        if not df_evolucao.empty:
            df_evolucao['taxa_natalidade'] = pd.to_numeric(df_evolucao['taxa_natalidade'], errors='coerce')
            df_evolucao['esperanca_vida'] = pd.to_numeric(df_evolucao['esperanca_vida'], errors='coerce')
            
            # Heatmap de evolução
            st.markdown("### Mapa de Calor: Taxa de Natalidade por UF ao Longo do Tempo")
            
            pivot_nat = df_evolucao.pivot_table(
                index='sg_uf',
                columns='co_ano',
                values='taxa_natalidade',
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot_nat,
                labels=dict(x="Ano", y="UF", color="Taxa"),
                aspect="auto",
                color_continuous_scale='RdYlBu_r'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### Mapa de Calor: Esperança de Vida por UF ao Longo do Tempo")
            
            pivot_esp = df_evolucao.pivot_table(
                index='sg_uf',
                columns='co_ano',
                values='esperanca_vida',
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot_esp,
                labels=dict(x="Ano", y="UF", color="Anos"),
                aspect="auto",
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Box plot por região
            st.markdown("### Distribuição por Região")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.box(
                    df_evolucao,
                    x='no_regiao_brasil',
                    y='taxa_natalidade',
                    color='no_regiao_brasil',
                    title='Distribuição da Taxa de Natalidade'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_evolucao,
                    x='no_regiao_brasil',
                    y='esperanca_vida',
                    color='no_regiao_brasil',
                    title='Distribuição da Esperança de Vida'
                )
                st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: RANKINGS ====================
elif page == "🏆 Rankings":
    with st.expander("ℹ️ Sobre os rankings"):
        st.markdown("""
**Rankings das Unidades Federativas:** Esta seção ordena todas as 27 UFs do Brasil conforme seus indicadores de saúde no ano selecionado, permitindo identificar rapidamente os estados com melhor e pior desempenho.

**Maiores Taxas de Natalidade:** O ranking à esquerda mostra as UFs com mais nascimentos por 1.000 habitantes. A coluna "vs Brasil" indica o quanto cada estado está acima ou abaixo da média nacional — valores positivos apontam estados com natalidade superior à média. Esses estados podem necessitar de mais investimentos em infraestrutura materno-infantil.

**Maiores Esperanças de Vida:** O ranking à direita destaca as UFs com maior sobrevida ao nascer. Estados no topo geralmente apresentam melhor infraestrutura de saúde, maior renda per capita e melhores condições de saneamento. Use o seletor de ano para acompanhar como a posição de cada estado muda ao longo do tempo.
""")

    
    st.subheader("Rankings das Unidades Federativas")
    
    # Seletor de ano
    query_anos = "SELECT DISTINCT co_ano FROM workspace.gold.indicadores_uf_ano ORDER BY co_ano DESC"
    df_anos = run_query(query_anos)
    
    if not df_anos.empty:
        ano_selecionado = st.selectbox("Selecione o Ano:", df_anos['co_ano'].tolist())
        
        # Query para rankings
        query_ranking = f"""
        SELECT 
            sg_uf,
            no_regiao_brasil,
            taxa_natalidade_indicador_uf as taxa_natalidade,
            esperanca_vida_indicador_uf as esperanca_vida,
            taxa_natalidade_indicador_br as taxa_natalidade_br,
            esperanca_vida_indicador_br as esperanca_vida_br
        FROM workspace.gold.indicadores_uf_ano
        WHERE co_ano = {ano_selecionado}
        ORDER BY sg_uf
        """
        df_ranking = run_query(query_ranking)
        
        if not df_ranking.empty:
            df_ranking['taxa_natalidade'] = pd.to_numeric(df_ranking['taxa_natalidade'], errors='coerce')
            df_ranking['esperanca_vida'] = pd.to_numeric(df_ranking['esperanca_vida'], errors='coerce')
            df_ranking['taxa_natalidade_br'] = pd.to_numeric(df_ranking['taxa_natalidade_br'], errors='coerce')
            df_ranking['esperanca_vida_br'] = pd.to_numeric(df_ranking['esperanca_vida_br'], errors='coerce')
            
            # Calcular desvios
            df_ranking['desvio_taxa'] = df_ranking['taxa_natalidade'] - df_ranking['taxa_natalidade_br']
            df_ranking['desvio_esperanca'] = df_ranking['esperanca_vida'] - df_ranking['esperanca_vida_br']
            
            # Rankings
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔼 Maiores Taxas de Natalidade")
                top_nat = df_ranking.nlargest(10, 'taxa_natalidade')[['sg_uf', 'taxa_natalidade', 'desvio_taxa']]
                top_nat['Ranking'] = range(1, len(top_nat) + 1)
                top_nat = top_nat[['Ranking', 'sg_uf', 'taxa_natalidade', 'desvio_taxa']]
                top_nat.columns = ['#', 'UF', 'Taxa', 'vs Brasil']
                st.dataframe(top_nat, hide_index=True, use_container_width=True)
                
                # Gráfico
                fig = px.bar(
                    top_nat.head(10),
                    x='Taxa',
                    y='UF',
                    orientation='h',
                    color='vs Brasil',
                    color_continuous_scale='RdYlGn_r',
                    title='Top 10 - Taxa de Natalidade'
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🔼 Maiores Esperanças de Vida")
                top_esp = df_ranking.nlargest(10, 'esperanca_vida')[['sg_uf', 'esperanca_vida', 'desvio_esperanca']]
                top_esp['Ranking'] = range(1, len(top_esp) + 1)
                top_esp = top_esp[['Ranking', 'sg_uf', 'esperanca_vida', 'desvio_esperanca']]
                top_esp.columns = ['#', 'UF', 'Anos', 'vs Brasil']
                st.dataframe(top_esp, hide_index=True, use_container_width=True)
                
                # Gráfico
                fig = px.bar(
                    top_esp.head(10),
                    x='Anos',
                    y='UF',
                    orientation='h',
                    color='vs Brasil',
                    color_continuous_scale='RdYlGn',
                    title='Top 10 - Esperança de Vida'
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: COMPARATIVOS ====================
elif page == "🔍 Comparativos":
    with st.expander("ℹ️ Comparativos entre UFs"):
        st.markdown("""
**Comparativo entre UFs:** Selecione até 5 estados para visualizar lado a lado a evolução de seus indicadores de saúde. Esta análise permite identificar padrões regionais, convergências e divergências entre estados.

**Gráficos de Evolução:** As linhas sobrepostas revelam se os estados selecionados seguem trajetórias semelhantes ou distintas. Cruzamentos de linhas indicam momentos em que um estado ultrapassou outro em desempenho, o que pode estar ligado a políticas públicas específicas.

**Correlação Taxa de Natalidade vs Esperança de Vida:** O gráfico de dispersão mostra a relação entre os dois indicadores no último ano disponível. Idealmente, estados no quadrante superior esquerdo (maior esperança de vida e menor natalidade) refletem estágios mais avançados de transição demográfica. Esta visualização é fundamental para entender o perfil demográfico comparado dos estados brasileiros.
""")

    
    st.subheader("Comparativo entre UFs")
    
    # Seletor múltiplo de UFs
    query_ufs = "SELECT DISTINCT sg_uf FROM workspace.gold.indicadores_uf_ano ORDER BY sg_uf"
    df_ufs = run_query(query_ufs)
    
    if not df_ufs.empty:
        ufs_selecionadas = st.multiselect(
            "Selecione até 5 UFs para comparar:",
            options=df_ufs['sg_uf'].tolist(),
            default=df_ufs['sg_uf'].tolist()[:3],
            max_selections=5
        )
        
        if ufs_selecionadas:
            # Query comparativa
            ufs_str = "','".join(ufs_selecionadas)
            query_comp = f"""
            SELECT 
                co_ano,
                sg_uf,
                taxa_natalidade_indicador_uf as taxa_natalidade,
                esperanca_vida_indicador_uf as esperanca_vida
            FROM workspace.gold.indicadores_uf_ano
            WHERE sg_uf IN ('{ufs_str}')
            ORDER BY co_ano, sg_uf
            """
            df_comp = run_query(query_comp)
            
            if not df_comp.empty:
                df_comp['taxa_natalidade'] = pd.to_numeric(df_comp['taxa_natalidade'], errors='coerce')
                df_comp['esperanca_vida'] = pd.to_numeric(df_comp['esperanca_vida'], errors='coerce')
                
                # Gráficos comparativos
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.line(
                        df_comp,
                        x='co_ano',
                        y='taxa_natalidade',
                        color='sg_uf',
                        markers=True,
                        title='Evolução da Taxa de Natalidade',
                        labels={'co_ano': 'Ano', 'taxa_natalidade': 'Taxa', 'sg_uf': 'UF'}
                    )
                    fig.update_layout(hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.line(
                        df_comp,
                        x='co_ano',
                        y='esperanca_vida',
                        color='sg_uf',
                        markers=True,
                        title='Evolução da Esperança de Vida',
                        labels={'co_ano': 'Ano', 'esperanca_vida': 'Anos', 'sg_uf': 'UF'}
                    )
                    fig.update_layout(hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Scatter plot - correlação
                st.markdown("### Correlação: Taxa de Natalidade vs Esperança de Vida")
                
                # Dados do último ano
                ultimo_ano = df_comp['co_ano'].max()
                df_ultimo = df_comp[df_comp['co_ano'] == ultimo_ano]
                
                fig = px.scatter(
                    df_ultimo,
                    x='taxa_natalidade',
                    y='esperanca_vida',
                    size='esperanca_vida',
                    color='sg_uf',
                    text='sg_uf',
                    title=f'Correlação entre Indicadores ({ultimo_ano})',
                    labels={'taxa_natalidade': 'Taxa de Natalidade', 'esperanca_vida': 'Esperança de Vida (anos)'}
                )
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela comparativa
                st.markdown("### 📋 Tabela Comparativa (Último Ano)")
                tabela_comp = df_ultimo[['sg_uf', 'taxa_natalidade', 'esperanca_vida']].copy()
                tabela_comp.columns = ['UF', 'Taxa Natalidade', 'Esperança de Vida']
                st.dataframe(tabela_comp, hide_index=True, use_container_width=True)

# ==================== PÁGINA: QUALIDADE DOS DADOS ====================
elif page == "⚠️ Qualidade dos Dados":
    with st.expander("ℹ️ Qualidade dos dados"):
        st.markdown("""
**Análise de Qualidade dos Dados:** Esta seção apresenta o resultado do pipeline de validação aplicado a todos os registros do DATASUS. O processo segue a arquitetura Medallion (Bronze → Silver → Validation → Gold) com **14 regras de validação** rigorosas.

**Registros Válidos vs Rejeitados:** Os cards mostram quantos registros passaram em todas as validações e quantos foram direcionados para quarentena. Uma taxa de qualidade próxima a 100% indica dados confiáveis para análise. Registros rejeitados são preservados na camada de quarentena para auditoria e possível correção.

**Regras de Validação:** Incluem verificações de integridade referencial (siglas UF, códigos IBGE), consistência temporal (datas, anos, meses), validação de ranges (valores positivos e dentro de limites razoáveis) e coerência hierárquica (UF → Região → Brasil). Essa abordagem garante que apenas dados de alta qualidade alimentem os indicadores do dashboard.
""")

    
    st.subheader("⚠️ Análise de Qualidade dos Dados")
    
    # Estatísticas de validação
    col1, col2, col3 = st.columns(3)
    
    # Query para quarentena
    query_quarentena = "SELECT COUNT(*) as rejeitados FROM workspace.gold.quarentena"
    df_quarentena = run_query(query_quarentena)
    
    query_validos = "SELECT COUNT(*) as validos FROM workspace.validation.taxa_bruta_natalidade WHERE size(motivos_rejeicao) = 0"
    df_validos = run_query(query_validos)
    
    query_total = "SELECT COUNT(*) as total FROM workspace.validation.taxa_bruta_natalidade"
    df_total = run_query(query_total)
    
    if not df_quarentena.empty and not df_validos.empty and not df_total.empty:
        rejeitados = int(df_quarentena['rejeitados'][0])
        validos = int(df_validos['validos'][0])
        total = int(df_total['total'][0])
        taxa_qualidade = (validos / total * 100) if total > 0 else 0
        
        with col1:
            st.metric("✅ Registros Válidos", f"{validos:,}")
        with col2:
            st.metric("❌ Registros Rejeitados", f"{rejeitados:,}")
        with col3:
            st.metric("📊 Taxa de Qualidade", f"{taxa_qualidade:.2f}%")
    
    st.markdown("---")
    
    # Detalhes da quarentena
    st.markdown("### Registros em Quarentena")
    
    query_detalhes = """
    SELECT 
        sg_uf,
        co_ano,
        motivos_rejeicao
    FROM workspace.gold.quarentena
    ORDER BY co_ano DESC, sg_uf
    LIMIT 100
    """
    df_detalhes = run_query(query_detalhes)
    
    if not df_detalhes.empty:
        
        st.dataframe(df_detalhes, use_container_width=True)
        st.info(f"Total de {len(df_detalhes)} registros rejeitados encontrados.")
    else:
        st.success("Nenhum registro em quarentena! Todos os dados passaram nas validações.")
    
    # Regras de validação
    st.markdown("---")
    st.markdown("### Regras de Validação Implementadas")
    
    regras = [
        "1. Validação de siglas UF (27 estados)",
        "2. Validação de meses (1-12)",
        "3. Validação de códigos IBGE",
        "4. Validação de regiões brasileiras",
        "5. Validação de códigos de região (1-5)",
        "6. Validação de siglas de região",
        "7. Obrigatoriedade de data de competência",
        "8. Indicador UF não nulo e positivo",
        "9. Indicador Regional não nulo e positivo",
        "10. Indicador Brasil não nulo e positivo",
        "11. Correspondência co_uf ↔ sg_uf",
        "12. Coerência hierárquica regional",
        "13. Consistência dt_competencia ↔ co_ano/co_mes",
        "14. Validação de range de anos (razoabilidade)"
    ]
    
    cols = st.columns(2)
    for i, regra in enumerate(regras):
        with cols[i % 2]:
            st.markdown(f"✅ {regra}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard desenvolvido com Streamlit | Dados: DATASUS/RIPSA</p>
    <p>Arquitetura: Bronze → Silver → Validation → Gold (Medallion)</p>
</div>
""", unsafe_allow_html=True)
