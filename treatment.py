import pandas as pd
import numpy as np
import warnings
import sys
import matplotlib.pyplot as plt
import seaborn as sns # Essencial para o boxplot

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# --- CONFIGURAÇÃO (Variáveis Globais/Constantes) ---
# Colunas de espessura que serão tratadas
EPI_COLS = ['C', 'S', 'ST', 'T', 'IT', 'I', 'IN', 'N', 'SN']

# Dicionário de Limites Clínicos Específicos (Mínimo, Máximo)
CLINICAL_LIMITS = {
    'C': (10, 160),
    'S': (10, 300), 'ST': (10, 300), 'T': (10, 300), 'IT': (10, 300), 
    'I': (10, 300), 'IN': (10, 300), 'N': (10, 300), 'SN': (10, 300)
}
# ----------------------------------------------------

def load_and_clean_epithelium_data(file_name: str, epi_cols: list = EPI_COLS, limits: dict = CLINICAL_LIMITS) -> pd.DataFrame:
    """
    Carrega dados de espessura do epitélio de um arquivo XLSX e realiza 
    a remoção de registros com valores biologicamente impossíveis (fora dos limites clínicos).
    """
    
    # 1. CARREGAMENTO DOS DADOS ORIGINAIS
    print(f"--- 1. Carregando dados do arquivo: {file_name} ---")
    try:
        df = pd.read_excel(file_name)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{file_name}' não encontrado. Verifique o nome/caminho.")
        return None 

    df_initial = df.copy()
    linhas_originais = len(df_initial)
    indices_para_remover = set()

    print("\n--- 2. Identificação de Registros com Valores Biologicamente Impossíveis (Outliers Clínicos) ---")

    for col in epi_cols:
        if col not in df_initial.columns:
            print(f"AVISO: Coluna '{col}' não encontrada no DataFrame e foi ignorada.")
            continue
            
        MIN_LIM, MAX_LIM = limits.get(col, (30, 100))
        
        # Identificar valores fora dos limites
        outliers = df_initial[(df_initial[col] < MIN_LIM) | (df_initial[col] > MAX_LIM)]
        
        if not outliers.empty:
            indices_para_remover.update(outliers.index)
            print(f"Coluna '{col}': Encontrados {len(outliers)} registros fora do limite ({MIN_LIM}-{MAX_LIM} µm).")

    # --- 3. REMOÇÃO DOS REGISTROS ---
    if indices_para_remover:
        df_clean = df_initial.drop(index=list(indices_para_remover)).copy()
        num_removidos = len(indices_para_remover)
        print(f"\n--- 3. Remoção de {num_removidos} registros (linhas) concluída. ---")
    else:
        df_clean = df_initial.copy()
        print("\n--- 3. Nenhum registro com valores impossíveis encontrado. ---")

    # --- 4. TRATAMENTO DE VALORES AUSENTES (NaN) ---
    # Apenas nas colunas de epitélio e após a remoção de outliers
    for col in epi_cols:
        if col in df_clean.columns and df_clean[col].isnull().any():
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
            print(f"Valores NaN na coluna '{col}' preenchidos com a mediana ({median_val:.2f}).")

    # --- 5. Sumário ---
    print("\n" + "="*70)
    print("RESUMO DO TRATAMENTO DE DADOS")
    print(f"Linhas originais: {linhas_originais}")
    print(f"Linhas removidas por conter outliers clínicos: {len(indices_para_remover)}")
    print(f"Linhas restantes para análise: {len(df_clean)}")
    print("="*70)
    
    return df_clean

# --------------------------------------------------------------------------

def plot_comparison_boxplots(file_name: str, df_processed: pd.DataFrame, epi_cols: list = EPI_COLS, limits: dict = CLINICAL_LIMITS):
    """
    Gera boxplots de comparação Antes (Original) e Depois (Tratado) para 
    visualizar o efeito do tratamento clínico de valores impossíveis.
    """
    print("\n--- 3. Visualização: Boxplots Antes (Original) e Depois (Tratado) ---")
    
    try:
        df_original = pd.read_excel(file_name)
    except FileNotFoundError:
        print("AVISO: Não foi possível recarregar o DataFrame original para visualização.")
        return

    # Garante que só temos as colunas de espessura que queremos plotar
    cols_to_plot = [col for col in epi_cols if col in df_original.columns and col in df_processed.columns]

    # --- Prepara os dados para o formato longo (tidy) ---
    
    # Adiciona a coluna de Status em cópias temporárias
    df_original_temp = df_original[cols_to_plot].copy()
    df_original_temp['Status'] = 'Original (Antes)'
    
    df_processed_temp = df_processed[cols_to_plot].copy()
    df_processed_temp['Status'] = 'Tratado Clinicamente (Depois)'
    
    # Concatena e converte para o formato longo
    df_combined = pd.concat([df_original_temp, df_processed_temp], ignore_index=True)
    
    df_plot = df_combined.melt(
        id_vars='Status',
        value_vars=cols_to_plot,
        var_name='Região',
        value_name='Espessura (μm)'
    ).dropna(subset=['Espessura (μm)'])
    
    # --- Geração dos Boxplots Lado a Lado ---
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True) # sharey=True para manter a mesma escala Y
    plt.suptitle('Efeito do Tratamento Clínico: Boxplots Antes e Depois', fontsize=18)
    
    # 1. Boxplot Original (Antes)
    sns.boxplot(
        ax=axes[0],
        data=df_plot[df_plot['Status'] == 'Original (Antes)'], 
        x='Região', 
        y='Espessura (μm)', 
        palette='Reds',
        showfliers=True # Mostrar Outliers para ver o que será cortado
    )
    axes[0].set_title('A) Dados Originais (Com Valores Impossíveis)', fontsize=14)
    axes[0].set_xlabel('Região de Medição')
    axes[0].set_ylabel('Espessura (μm)')
    axes[0].grid(axis='y', linestyle='--')
    
    # 2. Boxplot Tratado (Depois)
    sns.boxplot(
        ax=axes[1],
        data=df_plot[df_plot['Status'] == 'Tratado Clinicamente (Depois)'], 
        x='Região', 
        y='Espessura (μm)', 
        palette='Blues',
        showfliers=True # Mostrar os valores limitados (agora próximos aos limites clínicos)
    )
    axes[1].set_title('B) Dados Tratados (Valores Clamped aos Limites Clínicos)', fontsize=14)
    axes[1].set_xlabel('Região de Medição')
    axes[1].set_ylabel('') # Já tem label no primeiro gráfico
    axes[1].grid(axis='y', linestyle='--')

    # Adicionar Linhas de Limite (Apenas para contexto visual)
    C_min, C_max = limits.get('C', (40, 65))
    P_min, P_max = limits.get('S', (30, 100)) 
    
    for ax in axes:
        # Linhas de referência para o limite central
        ax.axhline(C_min, color='green', linestyle=':', linewidth=1.0, alpha=0.8)
        ax.axhline(C_max, color='green', linestyle=':', linewidth=1.0, alpha=0.8)
        
        # Linhas de referência para o limite periférico (mais amplas)
        ax.axhline(P_min, color='orange', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.axhline(P_max, color='orange', linestyle='--', linewidth=0.8, alpha=0.7)

    # Legenda (para os limites)
    handles = [
        plt.Line2D([0], [0], color='green', linestyle=':', label=f'Limites C: {C_min}-{C_max} µm'),
        plt.Line2D([0], [0], color='orange', linestyle='--', label=f'Limites P: {P_min}-{P_max} µm')
    ]
    fig.legend(handles=handles, loc='upper right', title='Limites Clínicos Aplicados')
    
    plt.tight_layout(rect=[0, 0, 0.95, 0.95]) # Ajusta layout para a legenda
    plt.show()

# --------------------------------------------------------------------------
# --- EXECUÇÃO DO SCRIPT ---

if __name__ == "__main__":

    NOME_ARQUIVO_REAL = 'RTVue_20221110_MLClass.xlsx' 

    # 1. Carregamento e Tratamento Clínico
    df_processed = load_and_clean_epithelium_data(NOME_ARQUIVO_REAL)

    if df_processed is not None:
        # 2. Visualização de Boxplots
        plot_comparison_boxplots(NOME_ARQUIVO_REAL, df_processed, EPI_COLS, CLINICAL_LIMITS)
        
        print("\nPróxima etapa: O DataFrame 'df_processed' está pronto para Normalização e Clustering.")