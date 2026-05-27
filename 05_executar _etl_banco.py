import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Conexão com o banco de testes que criamos
SERVIDOR = "DESKTOP-RIGOBEL\\CURSOSQL"
BANCO_DADOS = "Projeto_F1_Testes"

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BANCO_DADOS};"
    f"Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("📥 [ETAPA 1: EXTRAÇÃO] Lendo os dados brutos do SQL Server...")
# O Pandas lê a tabela do banco e transforma em um DataFrame
df_bruto = pd.read_sql("SELECT * FROM clientes_brutos", con=engine)
print("Dados originais extraídos do banco:")
print(df_bruto)
print("-" * 50)

print("\n⚙️ [ETAPA 2: TRANSFORMAÇÃO] Iniciando a limpeza dos dados...")

# Passo A: Remover linhas duplicadas (Ex: Ana Silva que estava repetida)
df_limpo = df_bruto.drop_duplicates(subset=["id_cliente"], keep="first").copy()

# Passo B: Tratar valores nulos na idade (Preencher com a mediana das idades)
mediana_idade = df_limpo["idade"].median()
df_limpo["idade"] = df_limpo["idade"].fillna(mediana_idade)

# Passo C: Tratar valores nulos na cidade (Preencher com 'Não Informado')
df_limpo["cidade"] = df_limpo["cidade"].fillna("Não Informado")

# Passo D: Remover Outliers no salário (Ex: Tirar o salário de 999999)
# Vamos aplicar um filtro simples: manter apenas salários menores que 50.000
df_limpo = df_limpo[df_limpo["salario"] < 50000]

print("✅ Dados transformados e limpos com sucesso!")
print(df_limpo)
print("-" * 50)

print("\n📤 [ETAPA 3: CARREGAMENTO] Salvando os dados limpos de volta no SQL Server...")
try:
    # Salva o resultado em uma tabela NOVA chamada 'clientes_finais'
    df_limpo.to_sql("clientes_finais", con=engine, if_exists="replace", index=False)
    print("🎯 SUCESSO COMPLETO! A tabela 'clientes_finais' está pronta no seu banco de dados.")
except Exception as e:
    print(f"❌ Erro ao carregar dados no banco: {e}")