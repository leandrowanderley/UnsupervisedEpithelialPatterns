# Análise de Padrões Morfológicos em Mapas Epiteliais com K-Means

## Resumo

Este projeto utiliza o algoritmo de clustering não supervisionado K-Means para identificar e caracterizar padrões morfológicos em mapas de espessura epitelial da córnea. O objetivo é agrupar pacientes com perfis de espessura semelhantes, permitindo a descoberta de assinaturas que podem estar associadas a diferentes condições clínicas, como ectasias (ex: ceratocone) ou perfis pós-cirúrgicos.

## Metodologia

O fluxo de trabalho consiste em três etapas principais:

### 1. Tratamento e Limpeza dos Dados

A qualidade dos dados é fundamental para um clustering significativo. A primeira etapa consiste em um rigoroso processo de limpeza:

- **Carregamento dos Dados:** Os dados são carregados a partir de um arquivo `RTVue_20221110_MLClass.xlsx`.
- **Remoção de Outliers Clínicos:** Para garantir a robustez da análise, os registros (pacientes) que apresentam valores de espessura biologicamente implausíveis ou que representam combinações raras são removidos. Um exemplo de critério para remoção seria um paciente com espessura superior a 100 µm em uma região (`S > 100 µm`) e inferior a 30 µm em outra (`I < 30 µm`). Esta filtragem é crucial para evitar que outliers distorçam os centróides dos clusters e gerem grupos sem significado clínico.
- **Tratamento de Valores Ausentes:** Valores ausentes (`NaN`) são preenchidos com a mediana da respectiva coluna.

### 2. Normalização

Após a limpeza, os dados de espessura epitelial são normalizados utilizando `MinMaxScaler`. Este processo coloca todas as variáveis na mesma escala (entre 0 e 1), garantindo que nenhuma região do mapa tenha um peso desproporcional durante o cálculo das distâncias no algoritmo K-Means.

### 3. Clusterização com K-Means

O K-Means é aplicado aos dados normalizados para diferentes valores de `K` (número de clusters). A análise foi focada em `K = {5, 6, 8, 10, 12}` para explorar desde agrupamentos mais gerais até a identificação de sub-padrões mais específicos e raros.

## Resultados e Análise dos Perfis

A análise dos centróides para cada valor de `K` revelou diferentes padrões morfológicos. À medida que `K` aumenta, padrões mais sutis e raros são isolados.

*(A análise detalhada dos perfis para cada K será fornecida separadamente).*

## Como Executar o Projeto

1.  **Pré-requisitos:** Certifique-se de ter o Python e as seguintes bibliotecas instaladas:
    ```bash
    pip install pandas numpy scikit-learn matplotlib seaborn openpyxl
    ```
2.  **Estrutura do Projeto:** O arquivo de dados `RTVue_20221110_MLClass.xlsx` deve estar no mesmo diretório que os scripts Python.
3.  **Execução:** Para rodar a análise completa, execute o script principal:
    ```bash
    python main.py
    ```
    O script irá realizar o tratamento dos dados, executar a clusterização e imprimir os perfis dos centróides para os valores de K definidos.