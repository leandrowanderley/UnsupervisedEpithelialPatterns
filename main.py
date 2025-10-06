from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import seaborn as sns # Biblioteca essencial para boxplots e distribuições

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# --- FASES 1 a 3: CARREGAMENTO E TRATAMENTO ---

# 1. SIMULAÇÃO DO CARREGAMENTO DE DADOS 
print("--- 1. Carregando e Visualizando Dados Simulados ---")
epi_cols = ['C', 'S', 'ST', 'T', 'IT', 'I', 'IN', 'N', 'SN']
np.random.seed(42) # Garante reprodutibilidade
data = {
    'Index': range(100), 'pID': [f'P{i:03d}' for i in range(100)],
    'Age': np.random.randint(20, 70, 100), 'Gender': np.random.choice(['M', 'F'], 100),
    'Eye': np.random.choice(['OS', 'OD'], 100),
    'C': np.random.normal(55, 3, 100), 'S': np.random.normal(60, 4, 100),
    'ST': np.random.normal(62, 5, 100), 'T': np.random.normal(58, 4, 100),
    'IT': np.random.normal(61, 3, 100), 'I': np.random.normal(63, 4, 100),
    'IN': np.random.normal(60, 3, 100), 'N': np.random.normal(59, 4, 100),
    'SN': np.random.normal(62, 5, 100),
}
df = pd.DataFrame(data)
# Injetando Outliers e NaN (para simular a necessidade de limpeza)
df.loc[3, 'C'] = 120; df.loc[10, 'S'] = 20; df.loc[50, 'IN'] = np.nan
df[epi_cols] = df[epi_cols].round(0)

# 2. TRATAMENTO DE DADOS AUSENTES (Missing Values)
for col in epi_cols:
    df[col] = df[col].fillna(df[col].median())

# 3. WINSORIZAÇÃO (Limitação de Outliers)
print("\n--- 3. Winsorização (Tratamento de Outliers) ---")
df_processed = df.copy()
LOWER_BOUND = 0.05; UPPER_BOUND = 0.95
for col in epi_cols:
    lower_limit = df_processed[col].quantile(LOWER_BOUND)
    upper_limit = df_processed[col].quantile(UPPER_BOUND)
    df_processed[col] = np.where(df_processed[col] < lower_limit, lower_limit, df_processed[col])
    df_processed[col] = np.where(df_processed[col] > upper_limit, upper_limit, df_processed[col])
    df_processed[col] = df_processed[col].astype(int)


# --- VISUALIZAÇÃO 1: EFEITO DA WINSORIZAÇÃO EM TODAS AS COLUNAS (FORMATO SOLICITADO) ---
print("\n--- 4. Visualização: Boxplots Antes e Depois da Winsorização ---")

# 1. Cria um DataFrame longo (tidy) para o Seaborn
df_plot_winsor = pd.DataFrame()
df_plot_winsor['Antes'] = df[epi_cols].stack()
df_plot_winsor['Depois'] = df_processed[epi_cols].stack()
df_plot_winsor['Variável'] = df[epi_cols].columns.repeat(len(df))
df_plot_winsor = df_plot_winsor.melt(id_vars='Variável', value_vars=['Antes', 'Depois'], 
                                     var_name='Status', value_name='Espessura (μm)')

plt.figure(figsize=(15, 6))
# Cria o Boxplot que compara o 'Antes' e 'Depois' para cada 'Variável'
sns.boxplot(data=df_plot_winsor, x='Variável', y='Espessura (μm)', hue='Status', palette={'Antes': 'red', 'Depois': 'green'})
plt.title('Validação da Winsorização: Distribuição das Espessuras Antes e Depois', fontsize=16)
plt.ylabel('Espessura (μm)')
plt.xlabel('Região de Medição')
plt.legend(title='Processamento')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.show()

# --- FASE 2: TRANSFORMAÇÃO (Padronização) ---

# 5. PADRONIZAÇÃO (StandardScaler)
print("\n--- 5. Padronização (StandardScaler - Z-Score) ---")
X = df_processed[epi_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
df_scaled = pd.DataFrame(X_scaled, columns=epi_cols)
df_final = pd.concat([df_processed[['Index', 'pID', 'Age', 'Gender', 'Eye']].reset_index(drop=True), df_scaled], axis=1)

# --- VISUALIZAÇÃO 2: EFEITO DA PADRONIZAÇÃO (Distribuições lado a lado) ---
print("\n--- 6. Visualização: Efeito da Padronização Z-Score ---")
plt.figure(figsize=(14, 6))
plt.suptitle('Validação da Padronização Z-Score', fontsize=16, y=1.02)

# Gráfico 2.1: Antes da Padronização (Escala μm) - Foco na coluna 'C'
plt.subplot(1, 2, 1)
sns.histplot(df_processed['C'], kde=True, color='blue', bins=15)
plt.title(f'A) ANTES da Padronização (Escala μm) | Média: {df_processed["C"].mean():.1f}')
plt.xlabel('Espessura C (μm)')
plt.ylabel('Frequência')

# Gráfico 2.2: Após a Padronização (Escala Z-Score)
plt.subplot(1, 2, 2)
sns.histplot(df_scaled['C'], kde=True, color='blue', bins=15)
plt.title(f'B) APÓS Padronização (Escala Z-Score) | Média: {df_scaled["C"].mean():.1f}, Std: {df_scaled["C"].std():.1f}')
plt.xlabel('Espessura C (Z-Score)')
plt.ylabel('Frequência')

plt.tight_layout()
plt.show()

# --- FASE 2: MINERAÇÃO (Achar o K) ---
print("\n--- 7. Achar o K: Determinação do Número Ótimo de Clusters ---")
k_range = range(2, 11); wcss = []; silhouette_scores = {}
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)
    silhouette_scores[k] = silhouette_score(X_scaled, kmeans.labels_)

# --- IDENTIFICAÇÃO DOS MELHORES K ---
best_silhouette_k = max(silhouette_scores, key=silhouette_scores.get)
diff_diff_wcss = np.diff(np.diff(wcss))
if len(diff_diff_wcss) > 0:
    best_elbow_k_est = np.argmin(diff_diff_wcss) + 3 
else:
    best_elbow_k_est = 3
best_elbow_k = min(max(2, best_elbow_k_est), 10)


# --- 8. Visualização Final Unificada (Métodos de K) ---
print("\n--- 8. Gerando Gráficos de K (Mineração) ---")

plt.figure(figsize=(14, 6)) 
# SUBPLOT 1 (Esquerda): Método do Cotovelo
plt.subplot(1, 2, 1)
plt.plot(k_range, wcss, marker='o', linestyle='-', color='blue')
label_elbow = f'K={best_elbow_k}, valor que melhor se enquadra na regra do Cotovelo'
plt.axvline(x=best_elbow_k, color='red', linestyle='--', label=label_elbow)
plt.title('1. Método do Cotovelo (Inércia vs. K)', fontsize=14)
plt.xlabel('Número de Clusters (K)')
plt.ylabel('WCSS (Inércia)')
plt.xticks(k_range)
plt.legend(fontsize=8)
plt.grid(axis='y', linestyle='--')

# SUBPLOT 2 (Direita): Coeficiente de Silhueta
plt.subplot(1, 2, 2)
silhouette_values = list(silhouette_scores.values())
plt.plot(k_range, silhouette_values, marker='o', linestyle='-', color='blue')
label_silhouette = f'Melhor K (Silhueta) = {best_silhouette_k}'
plt.axvline(x=best_silhouette_k, color='red', linestyle='--', label=label_silhouette)
plt.title(f'2. Coeficiente de Silhueta (Melhor K = {best_silhouette_k})', fontsize=14)
plt.xlabel('Número de Clusters (K)')
plt.ylabel('Média do Coeficiente de Silhueta')
plt.xticks(k_range)
plt.legend(fontsize=8)
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.show()

# --- FASE 3: AVALIAÇÃO E CARACTERIZAÇÃO (Aplicação Final) ---

K_MODELO = 3
print(f"\nK ESCOLHIDO PARA APLICAÇÃO FINAL: K = {K_MODELO}")

# Aplicação Final do K-Means
kmeans_final = KMeans(n_clusters=K_MODELO, random_state=42, n_init='auto')
kmeans_final.fit(X_scaled)
df_final['Cluster_Label'] = kmeans_final.labels_

# Caracterização (Des-padronização)
centroids_original = scaler.inverse_transform(kmeans_final.cluster_centers_)
centroids_df = pd.DataFrame(centroids_original, columns=epi_cols).round(1)
centroids_df.index.name = 'Perfil / Cluster'

# Sumário Final
print("\n######################################################")
print(f"### PERFIS FINAIS DE ESPESSURA (K={K_MODELO}) ###")
print("######################################################")
print(centroids_df)

# print("\n--- Próxima Ação: NOMEAR OS PERFIS ---")
# print("A fase de Avaliação está completa. Use a tabela acima para nomear os perfis (ex: 'Padrão Central Fino') para a apresentação final.")