import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# Dados médios por cluster (simplificados)
# -----------------------------
data_k2 = {
    0: [49.2, 50.0, 49.6, 48.7, 49.6, 51.0, 51.1, 50.8, 50.4],
    1: [57.2, 55.8, 56.2, 56.6, 56.6, 57.1, 57.3, 57.0, 56.2]
}

data_k3 = {
    0: [47.4, 48.5, 47.9, 47.1, 48.1, 49.4, 49.4, 49.3, 48.9],
    1: [59.9, 57.4, 58.1, 59.0, 58.9, 59.2, 59.2, 58.9, 57.9],
    2: [53.2, 53.2, 53.1, 52.7, 53.0, 54.2, 54.5, 54.2, 53.6]
}

data_k6 = {
    0: [44.2, 45.8, 44.8, 44.3, 45.5, 46.8, 46.4, 46.4, 45.9],
    1: [62.1, 58.7, 59.9, 61.3, 60.4, 60.8, 60.8, 61.0, 59.6],
    2: [50.2, 47.5, 47.9, 47.9, 48.6, 49.7, 49.6, 48.8, 48.0],
    3: [45.8, 56.0, 54.2, 50.2, 51.1, 53.5, 54.7, 56.0, 56.7],
    4: [56.6, 55.5, 55.7, 55.9, 56.1, 56.5, 56.8, 56.4, 55.6],
    5: [52.8, 52.5, 52.2, 52.0, 52.6, 53.9, 53.9, 53.4, 52.9]
}

regions = ['C', 'S', 'ST', 'T', 'IT', 'I', 'IN', 'N', 'SN']


# -----------------------------
# Função para plotar os perfis
# -----------------------------
def plot_profiles(data, K):
    plt.figure(figsize=(8,5))
    for cluster, values in data.items():
        plt.plot(regions, values, marker='o', label=f'Cluster {cluster}')
    plt.title(f'Perfis Médios de Espessura Epitelial (K={K})')
    plt.xlabel('Região do Olho')
    plt.ylabel('Espessura Média (µm)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# -----------------------------
# Gerar gráficos
# -----------------------------
plot_profiles(data_k2, 2)
plot_profiles(data_k3, 3)
plot_profiles(data_k6, 6)
