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
    'C': (40, 65),
    'S': (30, 100), 'ST': (30, 100), 'T': (30, 100), 'IT': (30, 100), 
    'I': (30, 100), 'IN': (30, 100), 'N': (30, 100), 'SN': (30, 100)
}
# ----------------------------------------------------

def load_and_clean_epithelium_data(file_name: str, epi_cols: list = EPI_COLS, limits: dict = CLINICAL_LIMITS) -> pd.DataFrame:
    """
    Carrega dados de espessura do epitélio de um arquivo XLSX e realiza 
    o tratamento de valores biologicamente impossíveis (fora dos limites clínicos).
    """
    
    # 1. CARREGAMENTO DOS DADOS ORIGINAIS
    print(f"--- 1. Carregando dados do arquivo: {file_name} ---")
    try:
        df = pd.read_excel(file_name)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{file_name}' não encontrado. Verifique o nome/caminho.")
        return None 

    df_clean = df.copy()
    total_impossiveis = 0
    registros_com_impossiveis = set()

    print("\n--- 2. Identificação e Tratamento de Valores Biologicamente Impossíveis (Clínicos) ---")

    for col in epi_cols:
        if col not in df_clean.columns:
            print(f"AVISO: Coluna '{col}' não encontrada no DataFrame e foi ignorada.")
            continue
            
        MIN_LIM, MAX_LIM = limits.get(col, (30, 100))
        
        # 2.1. Identificar valores impossíveis
        impossiveis_min = df_clean[col] < MIN_LIM
        impossiveis_max = df_clean[col] > MAX_LIM
        
        count_min = impossiveis_min.sum()
        count_max = impossiveis_max.sum()
        total_col = count_min + count_max
        total_impossiveis += total_col

        # 2.2. Registrar os índices (registros/linhas) afetados
        if total_col > 0:
            indices_min = df_clean[impossiveis_min].index.tolist()
            indices_max = df_clean[impossiveis_max].index.tolist()
            registros_com_impossiveis.update(indices_min + indices_max)

            print(f"Coluna {col} (Limites: {MIN_LIM}-{MAX_LIM} µm):")
            print(f"  - {count_min} valores tratados (ajustados para {MIN_LIM} µm)")
            print(f"  - {count_max} valores tratados (ajustados para {MAX_LIM} µm)")

        # 2.3. TRATAMENTO: Substituir valores impossíveis pelo limite clínico mais próximo (Clamping)
        df_clean.loc[impossiveis_min, col] = MIN_LIM
        df_clean.loc[impossiveis_max, col] = MAX_LIM
        
        # 2.4. Trata NaN
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())


    # --- 3. Sumário e Visualização dos Resultados (Simplificada na função) ---
    print("\n" + "="*70)
    print(f"RESUMO DO TRATAMENTO DE VALORES BIOLOGICAMENTE IMPOSSÍVEIS")
    print(f"Total de valores corrigidos: {total_impossiveis}")
    print(f"Total de pacientes (linhas) afetados: {len(registros_com_impossiveis)}")
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