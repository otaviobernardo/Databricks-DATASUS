#!/usr/bin/env python3
"""
Script para testar a conexão com o Databricks antes de executar o dashboard.
Execute: python test_connection.py
"""

import os
import sys
from databricks import sql
from dotenv import load_dotenv

def test_connection():
    """Testa a conexão com o Databricks e lista as tabelas Gold"""
    
    print("=" * 60)
    print("🔍 Teste de Conexão Databricks")
    print("=" * 60)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica variáveis de ambiente
    hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    
    print("\n1️⃣ Verificando variáveis de ambiente...")
    
    if not hostname or hostname == "seu-workspace.cloud.databricks.com":
        print("❌ DATABRICKS_SERVER_HOSTNAME não configurado")
        print("   Configure no arquivo .env")
        return False
    
    if not http_path or http_path == "/sql/1.0/warehouses/xxxxxx":
        print("❌ DATABRICKS_HTTP_PATH não configurado")
        print("   Configure no arquivo .env")
        return False
    
    if not token or token == "dapi_xxxxxxxxxxxxxxxxxxxxxxxxx":
        print("❌ DATABRICKS_TOKEN não configurado")
        print("   Configure no arquivo .env")
        return False
    
    print(f"✅ Hostname: {hostname}")
    print(f"✅ HTTP Path: {http_path}")
    print(f"✅ Token: {token[:10]}...{token[-5:]}")
    
    # Testa conexão
    print("\n2️⃣ Testando conexão com o Databricks...")
    
    try:
        connection = sql.connect(
            server_hostname=hostname,
            http_path=http_path,
            access_token=token
        )
        print("✅ Conexão estabelecida com sucesso!")
        
        # Lista tabelas Gold
        print("\n3️⃣ Verificando tabelas Gold...")
        
        cursor = connection.cursor()
        
        # Lista schemas
        cursor.execute("SHOW SCHEMAS IN workspace")
        schemas = [row[0] for row in cursor.fetchall()]
        
        if 'gold' not in schemas:
            print("❌ Schema 'gold' não encontrado!")
            print(f"   Schemas disponíveis: {', '.join(schemas)}")
            return False
        
        print("✅ Schema 'gold' encontrado")
        
        # Lista tabelas Gold
        cursor.execute("SHOW TABLES IN workspace.gold")
        tables = [row[1] for row in cursor.fetchall()]
        
        expected_tables = [
            'indicadores_br_ano',
            'indicadores_uf_ano',
            'ranking_esp_vida',
            'ranking_natalidade',
            'comparativo_uf_vs_br',
            'quarentena'
        ]
        
        print(f"\nTabelas encontradas no schema gold:")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f"\n⚠️ Tabelas esperadas não encontradas:")
            for table in missing_tables:
                print(f"  ❌ {table}")
            print("\nExecute os notebooks do projeto para criar as tabelas faltantes.")
        
        # Testa query simples
        print("\n4️⃣ Testando query simples...")
        
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM workspace.gold.indicadores_uf_ano
        """)
        
        result = cursor.fetchone()
        total_registros = result[0] if result else 0
        
        print(f"✅ Query executada com sucesso!")
        print(f"   Total de registros em indicadores_uf_ano: {total_registros:,}")
        
        if total_registros == 0:
            print("\n⚠️ Atenção: Tabela vazia! Execute os notebooks do projeto.")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ 🎉 Todos os testes passaram!")
        print("=" * 60)
        print("\n➡️ Você pode executar o dashboard agora:")
        print("   streamlit run streamlit_app.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        print("\n💡 Dicas para resolver:")
        print("  1. Verifique se o SQL Warehouse está ligado")
        print("  2. Confirme se o token não expirou")
        print("  3. Verifique as permissões de acesso")
        print("  4. Teste manualmente no Databricks SQL Editor")
        return False

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)