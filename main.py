from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# 1. SIMULAÇÃO DO CARREGAMENTO DE DADOS (Substitua esta seção pelo seu carregamento real)
print("--- 1. Carregando e Visualizando Dados Simulados ---")

epi_cols = ['C', 'S', 'ST', 'T', 'IT', 'I', 'IN', 'N', 'SN']

data = {
    'Index': range(100),
    'pID': [f'P{i:03d}' for i in range(100)],   
    'Age': np.random.randint(20, 70, 100),
    'Gender': np.random.choice(['M', 'F'], 100),
    'Eye': np.random.choice(['OS', 'OD'], 100),
    'C': np.random.normal(55, 3, 100),
    'S': np.random.normal(60, 4, 100),
    'ST': np.random.normal(62, 5, 100),
    'T': np.random.normal(58, 4, 100),
    'IT': np.random.normal(61, 3, 100),
    'I': np.random.normal(63, 4, 100),
    'IN': np.random.normal(60, 3, 100),
    'N': np.random.normal(59, 4, 100),
    'SN': np.random.normal(62, 5, 100),
}
df = pd.DataFrame(data)

# Injetando valores extremos e um NaN
df.loc[3, 'C'] = 120  # Outlier extremo
df.loc[10, 'S'] = 20   # Outlier extremo
df.loc[50, 'IN'] = np.nan # Missing Value

df[epi_cols] = df[epi_cols].round(0)
print(df.head(10))
print("\nEstatísticas antes da Winsorização:")
print(df[epi_cols].describe().T[['min', 'max', 'mean', 'std']])


# 2. TRATAMENTO DE DADOS AUSENTES (Missing Values)
print("\n--- 2. Tratamento de Missing Values ---")

missing_count = df[epi_cols].isnull().sum().sum()
print(f"Total de NaNs nas colunas de espessura antes: {missing_count}")

for col in epi_cols:
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)

missing_count_after = df[epi_cols].isnull().sum().sum()
print(f"Total de NaNs nas colunas de espessura após a imputação: {missing_count_after}")


# 3. WINSORIZAÇÃO (Limitação de Outliers)
print("\n--- 3. Winsorização (Tratamento de Outliers) ---")

df_processed = df.copy()

LOWER_BOUND = 0.05
UPPER_BOUND = 0.95

print(f"Aplicando Winsorização com limites: {LOWER_BOUND*100:.0f}% e {UPPER_BOUND*100:.0f}%")

for col in epi_cols:
    # 1. Calcular os limites
    lower_limit = df_processed[col].quantile(LOWER_BOUND)
    upper_limit = df_processed[col].quantile(UPPER_BOUND)

    # 2. Aplicar a Winsorização
    df_processed[col] = np.where(df_processed[col] < lower_limit, lower_limit, df_processed[col])
    df_processed[col] = np.where(df_processed[col] > upper_limit, upper_limit, df_processed[col])

    df_processed[col] = df_processed[col].astype(int)


# 4. VISUALIZAÇÃO PÓS-PROCESSAMENTO
print("\nEstatísticas após Winsorização:")
print(df_processed[epi_cols].describe().T[['min', 'max', 'mean', 'std']])

# Comparando os valores extremos que foram "winsorizados"
print("\nComparação dos Outliers (Linhas 3 e 10):")
print(f"Original C (Linha 3): {df.loc[3, 'C']} -> Processado C: {df_processed.loc[3, 'C']}")
print(f"Original S (Linha 10): {df.loc[10, 'S']} -> Processado S: {df_processed.loc[10, 'S']}")


# DEPOIS


# 5. PADRONIZAÇÃO (StandardScaler)
print("\n--- 5. Padronização (StandardScaler) ---")

# Seleciona as colunas de espessura processadas
X = df_processed[epi_cols].values

# Aplica o Standard Scaler: (valor - média) / desvio_padrao
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Cria o DataFrame Padronizado (df_scaled)
df_scaled = pd.DataFrame(X_scaled, columns=epi_cols)
df_final = pd.concat([df_processed[['Index', 'pID', 'Age', 'Gender', 'Eye']].reset_index(drop=True), df_scaled], axis=1)

print("Estatísticas após Padronização (Média ~0, Std ~1):")
print(df_scaled.describe().T[['mean', 'std']])


# ACHAR O K
print("\n--- 6. Achar o K: Determinação do Número Ótimo de Clusters ---")

k_range = range(2, 11) # Testando K de 2 a 10
wcss = []              # Para o Método do Cotovelo (Inércia)
silhouette_scores = {} # Para o Coeficiente de Silhueta

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    kmeans.fit(X_scaled)

    # 1. Método do Cotovelo
    wcss.append(kmeans.inertia_)

    # 2. Coeficiente de Silhueta
    score = silhouette_score(X_scaled, kmeans.labels_)
    silhouette_scores[k] = score
    print(f"K={k}: Coeficiente de Silhueta = {score:.4f}")

# Cria uma figura para os dois subplots lado a lado
plt.figure(figsize=(14, 6)) 

# --------------------------
# SUBPLOT 1 (Posição: Esquerda): Método do Cotovelo
# --------------------------
plt.subplot(1, 2, 1) # 1 linha, 2 colunas, 1ª posição (esquerda)
plt.plot(k_range, wcss, marker='o', linestyle='-', color='blue')
plt.title('1. Método do Cotovelo (Inércia vs. K)', fontsize=14)
plt.xlabel('Número de Clusters (K)')
plt.ylabel('WCSS (Inércia)')
plt.xticks(k_range)
plt.grid(axis='y', linestyle='--')


# --------------------------
# SUBPLOT 2 (Posição: Direita): Coeficiente de Silhueta (AGORA COMO GRÁFICO DE LINHA)
# --------------------------
plt.subplot(1, 2, 2) # 1 linha, 2 colunas, 2ª posição (direita)
# O dicionário silhouette_scores é diretamente plotado em um gráfico de linha
silhouette_values = list(silhouette_scores.values())
plt.plot(k_range, silhouette_values, marker='o', linestyle='-', color='blue')
plt.title('2. Coeficiente de Silhueta Médio por K', fontsize=14)
plt.xlabel('Número de Clusters (K)')
plt.ylabel('Média do Coeficiente de Silhueta')
plt.xticks(k_range)
plt.grid(axis='y', linestyle='--')

plt.tight_layout()
plt.show()

# ---

print("\nAnálise concluída. Escolha o K com o maior score de Silhueta (e que faça sentido no Cotovelo) para a aplicação final do K-Means.")


### Próxima Ação: Aplicar o K-Means e Caracterizar os Perfis

'''Após analisar os gráficos gerados:

1.  **Escolha o valor de K (exemplo: 4):** Baseado no cotovelo e no score de silhueta.
2.  **Rode o K-Means final:** Aplique o algoritmo com o K escolhido.
3.  **Análise dos Clusters:** Calcule a média das espessuras para cada cluster para dar o **nome/perfil** clínico.

Qual valor de $K$ você escolheu para continuarmos com a aplicação final do K-Means e a análise dos perfis?'''