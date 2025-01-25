import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

"""
Esse código entra nas pastas pares (1) ou nas pastas ímpares (2) 
e nelas acessa o arquivo .csv, plotando o spectro. Posteriormente,
procurando por todos os picos que podem (ou não) indicar a presença de algum
elemento. Depois disso, seleciona os picos e os salva em formato de imagem, 
calcula a intensidade (ponto de máximo) e utiliza o método do trapézio para
calcular a área do pico.
"""

#caminho da pasta principal
main_folder = 'amostras'

#função para verificar se o nome da subpasta é um número par
def is_even_folder(folder_name):
    try:
        return int(folder_name) % 2 == 0
    except ValueError:
        return False

#pergunta ao usuário se deseja acessar pastas pares ou ímpares
try:
    choice = int(input("Digite 1 para acessar pastas pares ou 2 para acessar pastas ímpares: ").strip())
    if choice not in [1, 2]:
        raise ValueError("Opção inválida. Escolha 1 ou 2.")
except ValueError as e:
    print(f"Erro: {e}")
    exit()

#define a função de filtro com base na escolha
def should_process_folder(folder_name):
    if choice == 1:
        return is_even_folder(folder_name)
    elif choice == 2:
        return not is_even_folder(folder_name)

#função para calcular a área sob a curva de um pico
def peak_area(wavelengths, intensity, a, b):
    """
    Calcula a área do pico no intervalo [a, b].
    """
    if (
        b > np.amax(wavelengths) or a > np.amax(wavelengths) or 
        a < np.amin(wavelengths) or b < np.amin(wavelengths)
    ):
        raise ValueError("'a' ou 'b' está fora do intervalo dos comprimentos de onda!")
    mask = (wavelengths >= a) & (wavelengths <= b)
    x = wavelengths[mask]
    y = intensity[mask]
    return np.trapz(y, x)

#define o diretório de saída com base na escolha
output_dir = 'resultados_pares' if choice == 1 else 'resultados_impares'
os.makedirs(output_dir, exist_ok=True)

#definir um threshold para eliminar casos negativos
THRESHOLD = 0

#processa as subpastas
for folder in os.listdir(main_folder):
    folder_path = os.path.join(main_folder, folder)
    
    if os.path.isdir(folder_path) and should_process_folder(folder):
        print(f"Processando a pasta: {folder}")
        folder_output_dir = os.path.join(output_dir, folder)
        os.makedirs(folder_output_dir, exist_ok=True)
        
        for file in os.listdir(folder_path):
            if file.endswith('.txt'):
                file_path = os.path.join(folder_path, file)
                
                try:
                    #lê o arquivo .txt
                    df = pd.read_csv(file_path, sep='\s+', skiprows=41, encoding='latin1')
                    wavelengths = df.iloc[:, 0].values
                    intensity = df.iloc[:, 2].values
                    
                    #aplica o threshold
                    intensity = np.maximum(intensity, THRESHOLD)
                    
                    #detecta picos diretamente nos dados processados
                    peaks, properties = find_peaks(
                        intensity, 
                        height=5000,  #altura mínima ajustada
                        prominence=3000,  #proeminência ajustada para evitar falsos positivos
                        distance=15  #distância mínima entre os picos
                    )
                    
                    #salva o gráfico completo 
                    plt.figure()
                    plt.plot(wavelengths, intensity, label='Dados Processados', alpha=0.8)
                    plt.scatter(wavelengths[peaks], intensity[peaks], color='red', label='Picos Detectados', zorder=5)
                    plt.xlabel('Comprimento de Onda (nm)')
                    plt.ylabel('Intensidade')
                    plt.title(f'Espectro Processado: {file}')
                    plt.legend()
                    
                    #salvar o gráfico completo
                    full_plot_path = os.path.join(folder_output_dir, f"{os.path.splitext(file)[0]}_grafico_completo.png")
                    plt.savefig(full_plot_path)
                    plt.close()
                    print(f"Gráfico completo salvo em: {full_plot_path}")
                    
                    #calcula as áreas e salva os gráficos de zoom para cada pico detectado
                    peak_data = []
                    for i, peak in enumerate(peaks):
                        #define uma região ao redor do pico (20 nm antes e depois)
                        region_width = 1  #ajustar conforme necessário
                        a = max(wavelengths[0], wavelengths[peak] - region_width)
                        b = min(wavelengths[-1], wavelengths[peak] + region_width)
                        area = peak_area(wavelengths, intensity, a, b)
                        peak_data.append({
                            'Comprimento de Onda (nm)': wavelengths[peak],
                            'Intensidade Máxima': intensity[peak],
                            'Área do Pico': area
                        })
                        
                        #gráfico de zoom na região do pico
                        mask = (wavelengths >= a) & (wavelengths <= b)
                        x_zoom = wavelengths[mask]
                        y_zoom = intensity[mask]
                        
                        plt.figure()
                        plt.plot(x_zoom, y_zoom, label=f'Pico {i+1}')
                        plt.scatter([wavelengths[peak]], [intensity[peak]], color='red', label='Pico Detectado', zorder=5)
                        plt.xlabel('Comprimento de Onda (nm)')
                        plt.ylabel('Intensidade')
                        plt.title(f'Zoom na Região do Pico {i+1}: {wavelengths[peak]:.2f} nm')
                        plt.legend()
                        
                        #salvar o gráfico de zoom
                        zoom_plot_path = os.path.join(
                            folder_output_dir,
                            f"{os.path.splitext(file)[0]}_pico_{i+1}_zoom.png"
                        )
                        plt.savefig(zoom_plot_path)
                        plt.close()
                        print(f"Gráfico de zoom do pico {i+1} salvo em: {zoom_plot_path}")
                    
                    #salva uma tabela com os picos detectados e suas áreas
                    peaks_df = pd.DataFrame(peak_data)
                    table_path = os.path.join(folder_output_dir, f"{os.path.splitext(file)[0]}_picos.csv")
                    peaks_df.to_csv(table_path, index=False, encoding='utf-8')
                    print(f"Tabela de picos salva em: {table_path}")
                
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")
