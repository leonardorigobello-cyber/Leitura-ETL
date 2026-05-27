import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Configuração do seu SQL Server local (com a barra dupla necessária para o Python)
SERVIDOR = "DESKTOP-RIGOBEL\\CURSOSQL"  
BANCO_DADOS = "master"  # Banco padrão para testar a conexão

# 2. Prepara os parâmetros de conexão usando a Autenticação do Windows
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BANCO_DADOS};"
    f"Trusted_Connection=yes;"
)

# 3. Cria o motor de conexão (Engine)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("🔄 Tentando conectar ao SQL Server...")

try:
    # TESTE: Tenta ler a lista de bancos de dados existentes no seu PC
    df_teste = pd.read_sql("SELECT name FROM sys.databases", con=engine)
    print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!\n")
    print("Bancos de dados ativos no seu servidor:")
    print(df_teste)
    
except Exception as e:
    print("❌ Erro ao conectar no SQL Server:")
    print(e)