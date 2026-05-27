import pandas as pd
from sqlalchemy import create_engine, text  # <-- Importamos o 'text' aqui
import urllib

# 1. Conexão inicial no 'master' para podermos criar o banco novo
SERVIDOR = "DESKTOP-RIGOBEL\\CURSOSQL"
params_master = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE=master;"
    f"Trusted_Connection=yes;"
)
engine_master = create_engine(f"mssql+pyodbc:///?odbc_connect={params_master}")

print("🔄 Criando o banco de dados 'Projeto_F1_Testes'...")
try:
    with engine_master.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # Usamos text() para envelopar a consulta SQL pura
        bancos = conn.execute(text("SELECT name FROM sys.databases")).fetchall()
        bancos_nomes = [b[0] for b in bancos]
        
        if "Projeto_F1_Testes" not in bancos_nomes:
            # Usamos text() aqui também para o comando de criação
            conn.execute(text("CREATE DATABASE Projeto_F1_Testes"))
            print("✅ Banco 'Projeto_F1_Testes' criado com sucesso!")
        else:
            print("💡 O banco 'Projeto_F1_Testes' já existe.")
except Exception as e:
    print(f"❌ Erro na criação do banco: {e}")

# 2. Agora nos conectamos diretamente ao novo banco criado
params_projeto = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE=Projeto_F1_Testes;"
    f"Trusted_Connection=yes;"
)
engine_projeto = create_engine(f"mssql+pyodbc:///?odbc_connect={params_projeto}")

# 3. Criando o DataFrame com dados "SUJOS" para você tratar
dados_sujos = {
    "id_cliente": [1, 2, 2, 3, 4, 5, 6],
    "nome": ["Leonardo", "Ana Silva", "Ana Silva", "Carlos Souza", "Beatriz Lima", "Marcos Santos", "Julia Costa"],
    "idade": [28, 34, 34, None, 22, 45, None],  
    "salario": [5000, 7200, 7200, 4100, 999999, 3100, 6000],  # 999999 é o outlier
    "cidade": ["São Paulo", "Rio", "Rio", "Belo Horizonte", "Santos", None, "Curitiba"]
}

df_sujo = pd.DataFrame(dados_sujos)

print("\n🔄 Inserindo dados sujos na tabela 'clientes_brutos'...")
try:
    # Salva os dados no banco na tabela 'clientes_brutos'
    df_sujo.to_sql("clientes_brutos", con=engine_projeto, if_exists="replace", index=False)
    print("✅ Tabela 'clientes_brutos' criada e povoada com sucesso!")
    
    print("\nDados que já estão lá no seu SQL Server prontos para o ETL:")
    print(df_sujo)
    
except Exception as e:
    print(f"❌ Erro ao inserir dados na tabela: {e}")