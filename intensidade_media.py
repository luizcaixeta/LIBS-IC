import os
import pandas as pd
from collections import defaultdict

def processar_pastas(root_dir, output_file):
    # Dicionário para acumular valores
    wavelength_data = defaultdict(lambda: {'Intensidade Máxima': [], 'Área do Pico': []})

    # Listar apenas as subpastas numeradas
    subfolders = sorted([f for f in os.listdir(root_dir) if f.isdigit()])

    for folder in subfolders:
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('.csv'):
                    file_path = os.path.join(folder_path, file)
                    try:
                        # Verifica se o arquivo não está vazio
                        if os.stat(file_path).st_size == 0:
                            print(f"O arquivo {file_path} está vazio e foi ignorado.")
                            continue

                        # Ler o arquivo CSV
                        df = pd.read_csv(file_path)

                        # Verifica se o DataFrame possui as colunas esperadas
                        expected_columns = ['Comprimento de Onda (nm)', 'Intensidade Máxima', 'Área do Pico']
                        if not all(col in df.columns for col in expected_columns):
                            print(f"O arquivo {file_path} não possui as colunas esperadas e foi ignorado.")
                            continue

                        # Garantir que as colunas sejam interpretadas corretamente
                        df['Comprimento de Onda (nm)'] = pd.to_numeric(df['Comprimento de Onda (nm)'], errors='coerce')
                        df['Intensidade Máxima'] = pd.to_numeric(df['Intensidade Máxima'], errors='coerce')
                        df['Área do Pico'] = pd.to_numeric(df['Área do Pico'], errors='coerce')

                        # Remover linhas com valores NaN
                        df = df.dropna()

                        # Arredondar os comprimentos de onda para o múltiplo mais próximo de 5 nm
                        df['Comprimento de Onda (nm)'] = df['Comprimento de Onda (nm)'].round(-1)

                        # Acumular os dados no dicionário
                        for _, row in df.iterrows():
                            wavelength = row['Comprimento de Onda (nm)']
                            wavelength_data[wavelength]['Intensidade Máxima'].append(row['Intensidade Máxima'])
                            wavelength_data[wavelength]['Área do Pico'].append(row['Área do Pico'])

                    except Exception as e:
                        print(f"Erro ao processar o arquivo {file_path}: {e}")

    # Calcular a média para cada comprimento de onda
    average_results = {
        wavelength: {
            'Intensidade Máxima Média': sum(values['Intensidade Máxima']) / len(values['Intensidade Máxima']),
            'Área do Pico Média': sum(values['Área do Pico']) / len(values['Área do Pico']),
        }
        for wavelength, values in wavelength_data.items()
    }

    # Ordenar os resultados por comprimento de onda
    sorted_results = sorted(average_results.items())

    # Converter para DataFrame e salvar como CSV
    output_df = pd.DataFrame([
        {
            'Comprimento de Onda (nm)': wavelength,
            **values
        }
        for wavelength, values in sorted_results
    ])
    output_df.to_csv(output_file, index=False)

    print(f"Cálculo concluído. Os resultados foram salvos em '{output_file}'.")


# Processar pastas pares e ímpares
processar_pastas('resultados_pares', 'intensidades_medias_pares.csv')
processar_pastas('resultados_impares', 'intensidades_medias_impares.csv')
