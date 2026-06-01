# Pipeline de Dados: Indicadores de Saúde (DATASUS)

Projeto de engenharia de dados focado na estruturação e análise de indicadores de saúde pública brasileira (Natalidade e Esperança de Vida). O pipeline foi desenhado para garantir qualidade, rastreabilidade e facilidade de consumo, utilizando o ecossistema Databricks e a arquitetura Medallion.

## Stack Utilizada
*   **Processamento:** Apache Spark, PySpark.
*   **Storage/Lakehouse:** Delta Lake, Unity Catalog.
*   **Orquestração/Ambiente:** Databricks.
*   **Visualização:** Streamlit, Plotly.

## Arquitetura
O projeto segue o padrão **Medallion**, garantindo uma separação clara entre a ingestão bruta e os dados prontos para análise:

*   **Bronze:** Ingestão dos arquivos CSV do DATASUS/RIPSA.
*   **Silver:** Limpeza, padronização de tipos e normalização de nomes/códigos.
*   **Validation:** Camada de barreira com 14 regras de qualidade. Registros que falham na validação são desviados para uma tabela de **Quarentena** para análise posterior.
*   **Gold:** Tabelas analíticas agregadas (por UF, Região e Ano) prontas para o consumo do dashboard.

## Principais Indicadores
O pipeline processa e consolida duas métricas fundamentais:

1.  **Taxa Bruta de Natalidade:** Monitoramento demográfico e planejamento de serviços obstétricos.
2.  **Esperança de Vida ao Nascer:** Indicador de desenvolvimento humano utilizado para políticas de saúde pública.

## Qualidade de Dados
Em vez de apenas processar, o pipeline foca na consistência. As validações abrangem:

*   Integridade de códigos (IBGE, UF, Região).
*   Consistência temporal (datas e competências).
*   Sanidade dos indicadores (valores nulos ou negativos).
*   **Resultado:** Qualquer dado fora dos critérios é isolado na tabela `workspace.gold.quarentena` com o log dos motivos da rejeição, permitindo identificar gargalos na fonte.

## Orquestração e Automação

### Databricks Job - Pipeline Automatizado
O projeto inclui um **Databricks Job** configurado para executar o pipeline completo automaticamente, garantindo rastreabilidade e integridade.

### Arquitetura de Execução
O fluxo segue uma dependência sequencial rígida para garantir que nenhum dado seja processado na camada seguinte sem passar pela anterior:

1. **Bronze (Ingestão)** → 2. **Silver (Limpeza)** → 3. **Validation (Qualidade)** → 4. **Gold (Agregação)**

> **Nota:** Se qualquer etapa falhar, o job interrompe a execução para evitar a propagação de inconsistências.

### Configurações do Job
| Configuração | Valor |
| :--- | :--- |
| **Compute** | Serverless |
| **Max Concurrent Runs** | 1 |
| **Retries por Task** | 2 |
| **Email Notifications** | Ativo |


### Resiliência e Fault Tolerance
Para garantir a robustez do processo:
* **Retries Automáticos**: Cada task possui 2 tentativas automáticas em caso de falha transitória (ex: indisponibilidade de fonte ou timeout).
* **Alertas**: Notificações por e-mail são disparadas automaticamente caso o limite de tentativas seja atingido, permitindo intervenção rápida.

## Dashboard
O dashboard desenvolvido em **Streamlit** centraliza as análises, oferecendo:

*   Visão macro da evolução dos indicadores nacionais.
*   Comparativo entre estados (UF vs Brasil).
*   Ranking dos estados com melhores/piores indicadores.
*   Monitoramento da saúde do pipeline (taxa de qualidade dos dados).
