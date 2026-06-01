# 🏥 Dashboard DATASUS - Streamlit

Dashboard interativo para visualização e análise de indicadores de saúde pública do Brasil, utilizando dados do DATASUS (Taxa Bruta de Natalidade e Esperança de Vida ao Nascer).

## 📊 Funcionalidades

### 1. 📈 Visão Geral
- Métricas principais do projeto
- Evolução temporal dos indicadores nacionais
- Análise comparativa por região

### 2. 🗺️ Análise por UF
- Seleção individual de estados
- Comparação UF vs Brasil
- Gráficos evolutivos específicos

### 3. 📈 Evolução Temporal
- Mapas de calor interativos
- Análise de períodos customizados
- Distribuição por região (box plots)

### 4. 🏆 Rankings
- Top 10 maiores taxas de natalidade
- Top 10 maiores esperanças de vida
- Desvios em relação à média nacional

### 5. 🔍 Comparativos
- Comparação entre até 5 UFs simultaneamente
- Correlação entre indicadores
- Análise de scatter plots

### 6. ⚠️ Qualidade dos Dados
- Estatísticas de validação
- Registros em quarentena
- 14 regras de qualidade implementadas

## 🚀 Como Executar

### Pré-requisitos

1. **Python 3.8+** instalado
2. **Acesso ao Databricks** com as tabelas Gold criadas
3. **Credenciais do Databricks SQL Warehouse**

### Instalação

#### 1. Clone ou baixe os arquivos do projeto

```bash
cd Projeto1/Databricks-DATASUS
```

#### 2. Crie um ambiente virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### Configuração das Credenciais

#### Opção 1: Variáveis de Ambiente (Recomendado)

Crie um arquivo `.env` na raiz do projeto:

```env
DATABRICKS_SERVER_HOSTNAME=seu-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxxx
DATABRICKS_TOKEN=dapi_xxxxxxxxxxxxxxxxxxxxxxxxx
```

E adicione no início do `streamlit_app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

#### Opção 2: Definir no Terminal

```bash
# Windows
set DATABRICKS_SERVER_HOSTNAME=seu-workspace.cloud.databricks.com
set DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxxx
set DATABRICKS_TOKEN=dapi_xxxxxxxxxxxxxxxxxxxxxxxxx

# Linux/Mac
export DATABRICKS_SERVER_HOSTNAME="seu-workspace.cloud.databricks.com"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/xxxxxx"
export DATABRICKS_TOKEN="dapi_xxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Como Obter as Credenciais do Databricks

1. **DATABRICKS_SERVER_HOSTNAME**:
   - Acesse seu workspace Databricks
   - A URL será algo como: `https://dbc-12345678-9abc.cloud.databricks.com`
   - O hostname é: `dbc-12345678-9abc.cloud.databricks.com`

2. **DATABRICKS_HTTP_PATH**:
   - Vá em **SQL Warehouses** no menu lateral
   - Selecione seu warehouse
   - Clique em **Connection Details**
   - Copie o **HTTP Path** (ex: `/sql/1.0/warehouses/abc123def456`)

3. **DATABRICKS_TOKEN**:
   - Clique no seu perfil (canto superior direito)
   - Vá em **User Settings** → **Developer** → **Access Tokens**
   - Clique em **Generate New Token**
   - Dê um nome (ex: "Streamlit Dashboard")
   - Copie o token gerado (começa com `dapi`)

### Executar a Aplicação

```bash
streamlit run streamlit_app.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

## 🏗️ Arquitetura dos Dados

O dashboard consome dados da camada **Gold** da arquitetura Medallion:

```
📁 workspace
  └── 🥉 bronze/
      ├── taxa_bruta_natalidade
      └── esperanca_vida_nascer
  └── 🥈 silver/
      ├── taxa_bruta_natalidade
      └── esperanca_vida_nascer
  └── 🛡️ validation/
      ├── taxa_bruta_natalidade
      ├── esperanca_vida_nascer
      └── teste_de_validacao
  └── 🥇 gold/
      ├── indicadores_br_ano ✅
      ├── indicadores_uf_ano ✅
      ├── ranking_esp_vida ✅
      ├── ranking_natalidade ✅
      ├── comparativo_uf_vs_br ✅
      ├── media_indicadores_ano ✅
      └── quarentena ✅
```

## 📝 Tabelas Gold Utilizadas

| Tabela | Descrição | Uso no Dashboard |
|--------|-----------|------------------|
| `indicadores_br_ano` | Indicadores agregados Brasil/ano | Visão Geral, Evolução Temporal |
| `indicadores_uf_ano` | Indicadores por UF/ano | Todas as páginas |
| `ranking_esp_vida` | Ranking de esperança de vida | Rankings |
| `ranking_natalidade` | Ranking de natalidade | Rankings |
| `comparativo_uf_vs_br` | Desvios UF vs Brasil | Comparativos |
| `quarentena` | Registros rejeitados | Qualidade dos Dados |

## 🎨 Personalização

### Alterar o Tema

Crie um arquivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Adicionar Novos Gráficos

O código está modularizado. Para adicionar novos gráficos:

1. Crie uma nova query SQL
2. Execute com `run_query()`
3. Converta os dados para numérico
4. Use Plotly para criar a visualização

## 🐛 Troubleshooting

### Erro de Conexão

```
Erro ao conectar no Databricks: ...
```

**Solução**: Verifique se:
- As variáveis de ambiente estão configuradas corretamente
- O token não expirou
- O SQL Warehouse está ligado
- Você tem permissões de acesso às tabelas Gold

### Gráficos Não Aparecem

```
DataFrame vazio retornado
```

**Solução**:
- Verifique se as tabelas Gold existem no catálogo `workspace`
- Execute as queries manualmente no Databricks SQL Editor para testar
- Confirme que há dados nas tabelas

### Performance Lenta

**Soluções**:
- Aumente o cache TTL (atualmente 600 segundos)
- Reduza o período de análise na página Evolução Temporal
- Use um SQL Warehouse maior (atualmente 2X-Small)
- Otimize as queries com filtros adicionais

## 📊 Métricas de Performance

- **Cache**: 10 minutos (600s)
- **Queries otimizadas**: Agregações pré-calculadas nas tabelas Gold
- **Lazy loading**: Dados carregados sob demanda por página

## 🔒 Segurança

⚠️ **IMPORTANTE**: Nunca commite o arquivo `.env` ou exponha seu token!

Adicione ao `.gitignore`:

```
.env
*.pyc
__pycache__/
venv/
.streamlit/secrets.toml
```

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework web para dashboards
- **Plotly**: Visualizações interativas
- **Pandas**: Manipulação de dados
- **Databricks SQL Connector**: Conexão com Databricks
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## 📚 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [Databricks SQL Connector](https://docs.databricks.com/dev-tools/python-sql-connector.html)

## 🤝 Contribuindo

Melhorias sugeridas:
- [ ] Adicionar exportação para Excel/CSV
- [ ] Implementar filtros avançados
- [ ] Criar página de análise preditiva
- [ ] Adicionar mapas geográficos
- [ ] Implementar autenticação de usuários

## 📄 Licença

Dados públicos do DATASUS/RIPSA - Ministério da Saúde do Brasil
