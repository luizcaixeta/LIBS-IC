import os
import pandas as pd
import matplotlib.pyplot as plt

"""
Esse código entra nas pastas de dados, procura pelo arquivo .txt e com isso 
plota os espectros de cada um.

"""

#caminho da pasta principal
main_folder = 'amostras'

#função para verificar se o nome da subpasta é um número par
def is_even_folder(folder_name):
    try:
        return int(folder_name) % 2 == 0
    except ValueError:
        return False

#percorre todas as subpastas
for folder in os.listdir(main_folder):
    folder_path = os.path.join(main_folder, folder)
    
    #verifica se é uma subpasta de número par
    if os.path.isdir(folder_path) and is_even_folder(folder):
        print(f"Processando a pasta: {folder}")
        
        #busca arquivos .txt na subpasta
        for file in os.listdir(folder_path):
            if file.endswith('.txt'):
                file_path = os.path.join(folder_path, file)
                
                #lê o arquivo .txt e plota a primeira coluna pela segunda
                try:
                    df = pd.read_csv(file_path, delim_whitespace=True, skiprows=41, encoding='latin1')  # Especifica a codificação
                    plt.figure()
                    plt.plot(df.iloc[:, 0], df.iloc[:, 2], label=f'{folder}/{file}')
                    plt.xlabel('Primeira Coluna')
                    plt.ylabel('Segunda Coluna')
                    plt.title(f'Plotagem: {folder}/{file}')
                    plt.legend()
                    plt.show()
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")

