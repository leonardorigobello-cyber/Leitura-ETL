"""
02_ limpeza_etl.py
------------------
Módulo responsável pelas regras de tratamento, limpeza e pipeline de ETL.
"""
import pandas as pd

class ProcessadorETL:
    """
    Classe estática responsável por aplicar as regras de limpeza nos DataFrames.
    """
    
    @staticmethod
    def tratar_dados_faltantes(df: pd.DataFrame, estrategia: str = "auto") -> pd.DataFrame:
        df_limpo = df.copy()
        if estrategia == "remover":
            return df_limpo.dropna()
            
        elif estrategia == "auto":
            for col in df_limpo.columns:
                if pd.api.types.is_numeric_dtype(df_limpo[col]):
                    mediana = df_limpo[col].median()
                    df_limpo[col] = df_limpo[col].fillna(mediana)
                else:
                    df_limpo[col] = df_limpo[col].fillna("Não Informado")
        return df_limpo

    @staticmethod
    def remover_outliers_iqr(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        df_limpo = df.copy()
        linhas_iniciais = len(df_limpo)
        colunas_numericas = df_limpo.select_dtypes(include=["number"]).columns
        
        for col in colunas_numericas:
            Q1 = df_limpo[col].quantile(0.25)
            Q3 = df_limpo[col].quantile(0.75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            df_limpo = df_limpo[(df_limpo[col] >= limite_inferior) & (df_limpo[col] <= limite_superior)]
            
        linhas_removidas = linhas_iniciais - len(df_limpo)
        return df_limpo, linhas_removidas