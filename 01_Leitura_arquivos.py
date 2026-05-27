"""
01_Leitura_arquivos.py
------------------
Interface gráfica (tkinter) para leitura de múltiplos arquivos de dados e visualização.
Delega o pipeline de processamento e limpeza para o módulo "02_ limpeza_etl.py".
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import importlib
import os
import sys

# Garante que o Python encontre o arquivo 02 mesmo se executado fora da pasta notebooks
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
if diretorio_atual not in sys.path:
    sys.path.insert(0, diretorio_atual)

# Importação dinâmica do arquivo de ETL contendo espaços no nome
try:
    modulo_etl = importlib.import_module("02_ limpeza_etl")
    ProcessadorETL = modulo_etl.ProcessadorETL
except ModuleNotFoundError:
    messagebox.showerror(
        "Erro de Inicialização", 
        "Não foi possível encontrar o arquivo '02_ limpeza_etl.py' na mesma pasta."
    )
    sys.exit(1)


# ─────────────────────────────────────────────
# 1. FUNÇÕES DE LEITURA (ROBUSTA)
# ─────────────────────────────────────────────

def ler_arquivo(caminho: str) -> pd.DataFrame:
    """
    Lê um arquivo de dados e retorna um DataFrame do pandas.
    Descobre automaticamente se o separador é vírgula ou ponto e vírgula.
    """
    caminho_lower = caminho.lower()
    
    if caminho_lower.endswith(".gz") or caminho_lower.endswith(".zip"):
        nome_sem_compactacao = os.path.splitext(caminho_lower)[0]
        ext = os.path.splitext(nome_sem_compactacao)[1]
    else:
        ext = os.path.splitext(caminho_lower)[1]

    # 1. Leitura de CSV (Tratando separadores de forma inteligente)
    if ext == ".csv":
        try:
            df = pd.read_csv(caminho, encoding="utf-8-sig")
            if df.shape[1] == 1:
                df_sep = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
                if df_sep.shape[1] > 1:
                    return df_sep
            return df
        except Exception:
            return pd.read_csv(caminho, sep=None, engine="python", encoding="utf-8-sig")

    # 2. Leitura de Excel
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(caminho, engine="openpyxl" if ext == ".xlsx" else None)

    # 3. Leitura de JSON
    elif ext == ".json":
        try:
            return pd.read_json(caminho)
        except Exception:
            return pd.read_json(caminho, lines=True)

    # 4. Leitura de TXT
    elif ext == ".txt":
        try:
            return pd.read_csv(caminho, sep="\t", encoding="utf-8-sig")
        except Exception:
            return pd.read_csv(caminho, sep=r"\s+", engine="python", encoding="utf-8-sig")

    # 5. Leitura de Parquet
    elif ext == ".parquet":
        return pd.read_parquet(caminho)

    else:
        raise ValueError(f"Formato não suportado: '{ext}'")


def resumo_dataframe(df: pd.DataFrame) -> str:
    """Gera um resumo textual do DataFrame."""
    linhas, colunas = df.shape
    nulos = df.isnull().sum().sum()
    tipos = df.dtypes.value_counts().to_dict()
    tipos_str = ", ".join(f"{v}x {k}" for k, v in tipos.items())

    return (
        f"  Linhas: {linhas:,}    Colunas: {colunas}\n"
        f"  Tipos : {tipos_str}\n"
        f"  Nulos : {nulos:,} células"
    )


# ─────────────────────────────────────────────
# 2. INTERFACE GRÁFICA (UI)
# ─────────────────────────────────────────────

class LeitorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Leitor de Arquivos & Pipeline de ETL")
        self.root.geometry("1000x620")
        self.root.resizable(True, True)

        self.arquivos_carregados: dict[str, pd.DataFrame] = {}
        self._construir_interface()

    def _construir_interface(self):
        """Monta os widgets da janela."""
        barra = tk.Frame(self.root, pady=8, padx=10)
        barra.pack(fill="x")

        tk.Button(
            barra, text="📂  Selecionar arquivos",
            command=self.selecionar_arquivos,
            bg="#2563eb", fg="white", padx=12, pady=5,
            relief="flat", cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            barra, text="🗑  Limpar tudo",
            command=self.limpar_tudo,
            bg="#e5e7eb", fg="#374151", padx=12, pady=5,
            relief="flat", cursor="hand2"
        ).pack(side="left")

        # Botões do pipeline de ETL
        tk.Button(
            barra, text="✨ Executar ETL Completo",
            command=self.executar_etl,
            bg="#059669", fg="white", padx=12, pady=5,
            relief="flat", cursor="hand2"
        ).pack(side="left", padx=(16, 8))

        tk.Button(
            barra, text="💾 Exportar CSV Limpo",
            command=self.exportar_arquivo,
            bg="#4b5563", fg="white", padx=12, pady=5,
            relief="flat", cursor="hand2"
        ).pack(side="left")

        self.label_status = tk.Label(
            barra, text="", fg="#16a34a", font=("Segoe UI", 10, "bold")
        )
        self.label_status.pack(side="left", padx=16)

        # Painel principal dividido
        painel = tk.PanedWindow(self.root, orient="horizontal", sashwidth=5)
        painel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Lista lateral esquerda
        frame_lista = tk.Frame(painel, width=220)
        painel.add(frame_lista, minsize=180)

        tk.Label(
            frame_lista, text="Arquivos carregados",
            font=("Segoe UI", 10, "bold"), anchor="w"
        ).pack(fill="x", padx=8, pady=(6, 2))

        self.listbox = tk.Listbox(
            frame_lista, selectmode="single",
            font=("Segoe UI", 9), activestyle="none",
            selectbackground="#2563eb", selectforeground="white"
        )
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self.exibir_previa)

        # Painel de prévia à direita
        frame_previa = tk.Frame(painel)
        painel.add(frame_previa, minsize=400)

        tk.Label(
            frame_previa, text="Prévia do arquivo",
            font=("Segoe UI", 10, "bold"), anchor="w"
        ).pack(fill="x", padx=8, pady=(6, 2))

        self.label_resumo = tk.Label(
            frame_previa, text="", justify="left",
            font=("Courier New", 9), fg="#6b7280", anchor="w"
        )
        self.label_resumo.pack(fill="x", padx=8)

        frame_tabela = tk.Frame(frame_previa)
        frame_tabela.pack(fill="both", expand=True, padx=8, pady=6)

        self.tabela = ttk.Treeview(frame_tabela, show="headings")

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        scroll_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tabela.pack(fill="both", expand=True)

    def selecionar_arquivos(self):
        tipos = [
            ("Arquivos de dados", "*.csv *.xlsx *.xls *.json *.txt *.parquet *.csv.gz *.csv.zip"),
            ("Todos", "*.*"),
        ]
        caminhos = filedialog.askopenfilenames(title="Selecione os arquivos de dados", filetypes=tipos)

        if not caminhos:
            return

        novos = 0
        erros = []

        for caminho in caminhos:
            nome = os.path.basename(caminho)
            if nome in self.arquivos_carregados:
                continue

            try:
                df = ler_arquivo(caminho)
                self.arquivos_carregados[nome] = df
                self.listbox.insert("end", nome)
                novos += 1
            except Exception as e:
                erros.append(f"{nome}: {e}")

        if novos:
            self._status(f"✔  {novos} arquivo(s) lido(s) com sucesso!", cor="#16a34a")

        if erros:
            messagebox.showerror("Erro ao ler arquivos", "Não foi possível ler:\n\n" + "\n".join(erros))

        if novos:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set("end")
            self.exibir_previa()

    def exibir_previa(self, event=None):
        """Atualiza a tabela de prévia separando colunas por vírgula ou ponto e vírgula."""
        selecionados = self.listbox.curselection()
        if notGrid := not selecionados:
            return

        nome = self.listbox.get(selecionados[0])
        df = self.arquivos_carregados.get(nome)

        if df is None:
            return

        # 1. Atualiza o resumo
        self.label_resumo.config(text=resumo_dataframe(df))
        
        # 2. Limpa completamente as colunas e dados anteriores da tabela
        self.tabela.delete(*self.tabela.get_children())
        
        colunas_exibicao = list(df.columns)[:100]
        self.tabela["columns"] = colunas_exibicao

        # Configura os novos cabeçalhos e colunas corretamente separadas
        for col in colunas_exibicao:
            self.tabela.heading(col, text=str(col))
            self.tabela.column(col, width=130, minwidth=70, anchor="w")

        # 3. Alimenta as linhas organizadas nas colunas certas
        for _, row in df.head(50).iterrows():
            valores = [str(row[col]) if pd.notna(row[col]) else "" for col in colunas_exibicao]
            self.tabela.insert("", "end", values=valores)

    def ejecutar_etl(self): 
        self.executar_etl()

    def executar_etl(self):
        """Chama a classe de limpeza externa contida no arquivo 02."""
        selecionados = self.listbox.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo na lista para aplicar o ETL.")
            return

        nome = self.listbox.get(selecionados[0])
        df_original = self.arquivos_carregados[nome]
        
        linhas_antes = len(df_original)
        
        # 1. Remoção de Duplicatas (Lógica interna rápida)
        df_processado = df_original.drop_duplicates()
        duplicatas_removidas = linhas_antes - len(df_processado)
        
        # 2. Tratamento de Nulos (Consumido do arquivo 02)
        nulos_antes = df_processado.isnull().sum().sum()
        df_processado = ProcessadorETL.tratar_dados_faltantes(df_processado, estrategia="auto")
        
        # 3. Remoção de Outliers (Consumido do arquivo 02)
        df_processado, outliers_removidos = ProcessadorETL.remover_outliers_iqr(df_processado)
        
        # Atualiza o estado da memória e a tela
        self.arquivos_carregados[nome] = df_processado
        self.exibir_previa()
        self._status("✔ ETL executado via Módulo 02!", cor="#059669")
        
        relatorio = (
            f"Relatório de Transformação (ETL) para:\n{nome}\n\n"
            f"• Linhas originais: {linhas_antes:,}\n"
            f"• Linhas pós-limpeza: {len(df_processado):,}\n\n"
            f"⚙ Limpezas efetuadas pelo Módulo 02:\n"
            f" - {duplicatas_removidas:,} Linhas duplicadas removidas.\n"
            f" - {nulos_antes:,} Células nulas preenchidas.\n"
            f" - {outliers_removidos:,} Outliers removidos pelo método IQR."
        )
        messagebox.showinfo("Sucesso no Processamento", relatorio)

    def exportar_arquivo(self):
        """Salva o dataset limpo em formato CSV."""
        selecionados = self.listbox.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione um arquivo limpo para exportar.")
            return

        nome = self.listbox.get(selecionados[0])
        df = self.arquivos_carregados[nome]

        caminho_salvar = filedialog.asksaveasfilename(
            title="Salvar arquivo limpo",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfile=f"limpo_{nome}"
        )

        if caminho_salvar:
            try:
                df.to_csv(caminho_salvar, index=False, encoding="utf-8-sig")
                messagebox.showinfo("Sucesso", "Arquivo exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def limpar_tudo(self):
        self.arquivos_carregados.clear()
        self.listbox.delete(0, "end")
        self.tabela.delete(*self.tabela.get_children())
        self.tabela["columns"] = []
        self.label_resumo.config(text="")
        self._status("")

    def _status(self, message: str, cor: str = "#16a34a"):
        self.label_status.config(text=message, fg=cor)


# ─────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = LeitorApp(root)
    root.mainloop()