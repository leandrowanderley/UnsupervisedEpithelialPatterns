# Análise de Padrões Morfológicos em Mapas Epiteliais

## Resumo Executivo

Este projeto utiliza clustering não supervisionado (K-Means) para identificar padrões morfológicos em mapas de espessura epitelial. A análise revelou três perfis clínicos principais: **Plano (normalidade)**, **Donut (suspeita de ectasia)** e **Cunha (suspeita de DMP ou pós-cirurgia)**.

A análise demonstrou que **K=8 é o valor mais informativo**, pois é o primeiro a isolar simultaneamente os padrões Donut e Cunha, oferecendo a visão morfológica mais completa e clinicamente relevante.

## Padrões Morfológicos Identificados

O clustering permitiu a categorização dos mapas epiteliais em três padrões com distintas assinaturas morfológicas e implicações clínicas.

### Padrão 1: Plano (Homogêneo)

*   **Descrição:** Caracterizado por uma espessura epitelial relativamente uniforme em toda a área do mapa. Este padrão representa a morfologia de base, ou normalidade.
*   **Identificação:** É claramente visível em clusterizações com poucos clusters, como **K=2** e **K=3**, que separam a população em perfis "Fino", "Médio" e "Espesso", todos com morfologia plana.
    *   **K=3, Perfil 2 (Plano Médio/Padrão):** O maior cluster (2767 amostras), representando o perfil mais comum da normalidade, com espessura média de ~53µm.

### Padrão 2: Donut (Anel)

*   **Descrição:** Apresenta um centro epitelial fino e uma periferia mais espessa.
*   **Relevância Clínica:** Este padrão é um achado chave, frequentemente associado a ectasias como o **Ceratocone**, onde a remodelação epitelial compensa o afinamento estromal central.
*   **Identificação:** O padrão Donut é isolado pela primeira vez em **K=5**.
    *   **K=5, Perfil 2:** Centro (C) de **44.8µm** e periferia superior (S, SN, N) com espessura de até **55.9µm**.
*   **Refinamento em K=8:** O padrão é ainda mais bem definido.
    *   **K=8, Perfil 1 (Donut Extremo):** Centro (C) de **44.1µm** e periferia superior de até **55.5µm**, sugerindo casos de ectasia subclínica ou avançada.

### Padrão 3: Cunha (Wedge)

*   **Descrição:** Caracterizado por um centro epitelial espesso e uma periferia fina.
*   **Relevância Clínica:** Padrão vital para a identificação de condições como a **Degeneração Marginal Pelúcida (DMP)** ou para o acompanhamento de perfis pós-cirúrgicos (ablação).
*   **Identificação:** O padrão Cunha é isolado pela primeira vez em **K=8**.
    *   **K=8, Perfil 7:** Centro (C) de **53.4µm** e periferia (S, SN, T, IT) com espessura de até **~42µm**.

## A Importância do K=8: Máxima Riqueza Morfológica

A análise de múltiplos valores de K revelou que **K=8 oferece a visão mais completa e clinicamente útil**. Enquanto valores menores de K agrupam os perfis patológicos, e valores maiores apenas subdividem os já existentes, K=8 é o ponto ótimo que separa e isola os três padrões morfológicos fundamentais:

1.  **Perfis Planos:** Múltiplos clusters em K=8 representam variações da normalidade (fino, médio, espesso).
2.  **Padrão Donut:** Isola o perfil de afinamento central (Cluster 1).
3.  **Padrão Cunha:** Isola o perfil de espessamento central (Cluster 7).

## Conclusão

O clustering K-Means demonstrou ser uma ferramenta poderosa para a identificação de padrões morfológicos epiteliais. A categorização em perfis **Plano, Donut e Cunha** fornece um framework robusto para a triagem e acompanhamento de pacientes, com K=8 sendo a configuração de análise mais recomendada.

## Anexo: Visualização dos Clusters

| K=2 (Base Fina vs. Espessa) | K=3 (Estrutura Padrão) | K=8 (Donut + Cunha) |
| :---: | :---: | :---: |
| ![k=2](graphics/k2.png) | ![k=3](graphics/k3.png) | ![k=8](graphics/k8.png) |

## Como Executar o Projeto

1.  Instale as dependências:
    ```bash
    pip install pandas numpy scikit-learn matplotlib seaborn
    ```
2.  Execute o script principal:
    ```bash
    python main.py
    ```
