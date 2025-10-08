from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import seaborn as sns

try:
    from treatment import load_and_clean_epithelium_data, EPI_COLS, CLINICAL_LIMITS
except ImportError:
    print("ERRO: Não foi possível importar a função 'load_and_clean_epithelium_data' de 'treatment.py'.")
    print("Certifique-se de que o arquivo 'treatment.py' está no mesmo diretório e contém a função.")
    exit()

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# --- CONFIGURAÇÃO CHAVE ---
NOME_ARQUIVO = 'RTVue_20221110_MLClass.xlsx' 
epi_cols = EPI_COLS
id_cols = ['Index', 'pID', 'Age', 'Gender', 'Eye'] 
# -------------------------

# --- FASE 1: CARREGAMENTO E TRATAMENTO CLÍNICO (Via Função) ---

# 1. CARREGAMENTO E TRATAMENTO CLÍNICO (Substitui as antigas Fases 1 e 2)
print("--- FASE 1: Carregamento e Tratamento Clínico de Valores Impossíveis ---")

df_processed = load_and_clean_epithelium_data(
    file_name=NOME_ARQUIVO, 
    epi_cols=epi_cols, 
    limits=CLINICAL_LIMITS
)

if df_processed is None:
    exit()

print(f"\nDataFrame pronto para a próxima fase com {len(df_processed)} linhas.")

# --- FASE 2: TRANSFORMAÇÃO (Normalização MinMax) ---

# 4. NORMALIZAÇÃO (MinMaxScaler) - Substitui a Padronização
print("\n--- 4. Normalização (MinMaxScaler - Escala [0, 1]) ---")

X = df_processed[epi_cols].values 
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
df_scaled = pd.DataFrame(X_scaled, columns=epi_cols)

df_final = pd.concat([df_processed[id_cols].reset_index(drop=True), df_scaled], axis=1)

print("Normalização MinMax concluída. Dados prontos para o Clustering.")


# --- VISUALIZAÇÃO 1: EFEITO DA NORMALIZAÇÃO (Distribuições lado a lado) ---
print("\n--- 5. Visualização: Efeito da Normalização MinMax [0, 1] ---")
plt.figure(figsize=(14, 6))
plt.suptitle('Validação da Normalização MinMax (Escala [0, 1])', fontsize=16, y=1.02)

# Gráfico 1.1: Antes da Normalização (Escala μm) - Foco na primeira coluna
col_exemplo = epi_cols[0] if epi_cols else None

if col_exemplo:
    plt.subplot(1, 2, 1)
    sns.histplot(df_processed[col_exemplo], kde=True, color='blue', bins=15)
    plt.title(f'A) ANTES da Normalização ({col_exemplo} | Média: {df_processed[col_exemplo].mean():.1f})')
    plt.xlabel(f'Espessura {col_exemplo} (μm)')
    plt.ylabel('Frequência')

    # Gráfico 1.2: Após a Normalização (Escala [0, 1])
    plt.subplot(1, 2, 2)
    sns.histplot(df_scaled[col_exemplo], kde=True, color='blue', bins=15)
    plt.title(f'B) APÓS Normalização (Escala [0, 1]) | Min: {df_scaled[col_exemplo].min():.1f}, Max: {df_scaled[col_exemplo].max():.1f}')
    plt.xlabel(f'Espessura {col_exemplo} (Escala 0-1)')
    plt.ylabel('Frequência')

    plt.tight_layout()
    plt.show()
else:
    print("AVISO: Visualização de Normalização pulada. Nenhuma coluna de espessura para visualização.")


# --- FASE 3: MINERAÇÃO (Achar o K) - VERSÃO REFEITA ---
print("\n--- 6. Achar o K: Determinação do Número Ótimo de Clusters (cotovelo + silhueta) ---")

n_samples = X_scaled.shape[0]
if n_samples < 2:
    print("Não há dados suficientes para clustering (menos de 2 amostras).")
else:
    # limite superior seguro para K: ao menos 2 clusters e no máximo n_samples-1 para permitir cálculo de silhueta
    max_k_possible = min(15, n_samples - 1)  # Aumentado para incluir K=12
    if max_k_possible < 2:
        print("Não há amostras suficientes para avaliar múltiplos K (precisa de pelo menos 3 amostras).")
    else:
        k_range = range(2, max_k_possible + 1)
        wcss = []
        silhouette_scores = {}

        for k in k_range:
            # Ajuste do KMeans (usar n_init numérico para compatibilidade)
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            wcss.append(kmeans.inertia_)

            # Cálculo seguro da silhueta — captura exceções/valores inválidos
            try:
                # silhouette_score pode falhar em casos extremos (clusters singletons etc.)
                sil = silhouette_score(X_scaled, labels)
            except Exception:
                sil = np.nan
            silhouette_scores[k] = sil

        # --- IDENTIFICAÇÃO DO MELHOR K (SILHUETA) ---
        # escolhe o K com maior silhueta entre os calculados (ignorando NaN)
        valid_sil_items = [(k, s) for k, s in silhouette_scores.items() if not np.isnan(s)]
        if valid_sil_items:
            best_silhouette_k = max(valid_sil_items, key=lambda t: t[1])[0]
        else:
            best_silhouette_k = None

        # --- ESTIMATIVA DO COTOVELO (método: maior distância entre o ponto e a reta first-last) ---
        ks = np.array(list(k_range))
        wcss_arr = np.array(wcss)

        if len(ks) >= 2:
            # pontos extremos
            x1, y1 = ks[0], wcss_arr[0]
            x2, y2 = ks[-1], wcss_arr[-1]
            # distância perpendicular de cada (x,y) à linha (x1,y1)-(x2,y2)
            num = np.abs((y2 - y1) * ks - (x2 - x1) * wcss_arr + x2 * y1 - y2 * x1)
            den = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
            distances = num / den
            best_elbow_k = int(ks[np.argmax(distances)])
        else:
            best_elbow_k = None

        # --- PLOT: Cotovelo (WCSS) e Silhueta ---
        print("\n--- 7. Gerando Gráficos de K (Mineração) ---")
        plt.figure(figsize=(14, 6))

        # Subplot 1: Cotovelo (WCSS)
        plt.subplot(1, 2, 1)
        plt.plot(ks, wcss_arr, marker='o', linestyle='-')
        if best_elbow_k is not None:
            plt.axvline(x=best_elbow_k, color='red', linestyle='--', label=f'Elbow K = {best_elbow_k}')
            # anotar o ponto exato
            plt.scatter([best_elbow_k], [wcss_arr[np.where(ks == best_elbow_k)[0][0]]], s=100, edgecolors='k')
        plt.title('1. Método do Cotovelo (Inércia vs. K)', fontsize=14)
        plt.xlabel('Número de Clusters (K)')
        plt.ylabel('WCSS (Inércia)')
        plt.xticks(ks)
        plt.grid(axis='y', linestyle='--')
        if best_elbow_k is not None:
            plt.legend(fontsize=8)

        # Subplot 2: Silhueta
        plt.subplot(1, 2, 2)
        # construir arrays alinhados (coloca NaN onde não houve cálculo)
        silhouette_vals = np.array([silhouette_scores[k] for k in ks])
        plt.plot(ks, silhouette_vals, marker='o', linestyle='-')
        if best_silhouette_k is not None:
            plt.axvline(x=best_silhouette_k, color='red', linestyle='--', label=f'Best Silhouette K = {best_silhouette_k}')
            plt.scatter([best_silhouette_k], [silhouette_scores[best_silhouette_k]], s=100, edgecolors='k')
        plt.title('2. Coeficiente de Silhueta', fontsize=14)
        plt.xlabel('Número de Clusters (K)')
        plt.ylabel('Média do Coeficiente de Silhueta')
        plt.xticks(ks)
        plt.grid(axis='y', linestyle='--')
        if best_silhouette_k is not None:
            plt.legend(fontsize=8)

        plt.tight_layout()
        plt.savefig('elbow_silhouette.png')
        plt.show()

        # --- FASE 4: AVALIAÇÃO E CARACTERIZAÇÃO ---
        # Define a lista de K's para análise conforme solicitado
        K_MODELOs = [5, 6, 8, 10, 12]
        
        # Filtra a lista para garantir que os valores de K sejam possíveis com os dados
        K_MODELOs = [k for k in K_MODELOs if 2 <= k <= max_k_possible]

        if not K_MODELOs:
            print("Nenhum K válido selecionado para caracterização (filtro por tamanho de amostra).")
        else:
            print(f"\n--- 8. Aplicação e Caracterização para K's Selecionados: {K_MODELOs} ---")

            for K_MODELO in K_MODELOs:
                kmeans_final = KMeans(n_clusters=K_MODELO, random_state=42, n_init=10)
                kmeans_final.fit(X_scaled)

                # inversão para as unidades originais (μm)
                centroids_original = scaler.inverse_transform(kmeans_final.cluster_centers_)
                centroids_df = pd.DataFrame(centroids_original, columns=epi_cols).round(1)
                centroids_df.index.name = 'Perfil / Cluster'

                df_final[f'Cluster_Label_K{K_MODELO}'] = kmeans_final.labels_
                cluster_counts = df_final[f'Cluster_Label_K{K_MODELO}'].value_counts().sort_index()
                centroids_df['Contagem'] = cluster_counts.values if len(cluster_counts) == len(centroids_df) else cluster_counts.reindex(range(len(centroids_df)), fill_value=0).values

                # obter/estimar silhueta para este K (se não foi calculado antes)
                silh_score = silhouette_scores.get(K_MODELO)
                if np.isnan(silh_score):
                    try:
                        silh_score = silhouette_score(X_scaled, kmeans_final.labels_)
                    except Exception:
                        silh_score = np.nan

                print("\n" + "#" * 50)
                print(f"### PERFIS FINAIS DE ESPESSURA (K = {K_MODELO}) ###")
                print(f"Silhueta Média para K={K_MODELO}: {silh_score if not np.isnan(silh_score) else 'N/A'}")
                print("#" * 50)
                print(centroids_df)


