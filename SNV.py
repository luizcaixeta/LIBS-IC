import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


#função para normalizar o comprimento dos espectros
def normalize_length(matrix, target_length=None):
    if target_length is None:
        #determina o comprimento mínimo comum
        target_length = min(len(spectrum) for spectrum in matrix)

    normalized_matrix = []
    for spectrum in matrix:
        if len(spectrum) > target_length:
            #trunca os espectros mais longos
            normalized_matrix.append(spectrum[:target_length])
        elif len(spectrum) < target_length:
            #preenche com zeros os espectros mais curtos
            normalized_matrix.append(
                np.pad(spectrum, (0, target_length - len(spectrum)), mode="constant")
            )
        else:
            #mantém os espectros que já possuem o tamanho correto
            normalized_matrix.append(spectrum)

    return np.array(normalized_matrix)

#função para ler as amostras e montar a matriz
def dirtoread(root_folder, matrix=[], column_index=2):

    ROOT = Path(root_folder)
    for subfolder in sorted(ROOT.iterdir()):
        if subfolder.is_dir():
            for csv_file in sorted(subfolder.glob("*.csv")):
                try:
                    data = pd.read_csv(csv_file, header=1)  
                    if column_index < data.shape[1]: 
                        matrix.append(data.iloc[:, column_index].to_numpy()) 
                except Exception as e:
                    print(f"Erro ao processar {csv_file}: {e}")
    return matrix

def y_ml(A, B):
    return np.concatenate([np.zeros(A), np.ones(B)])

dir_pares = "resultados_pares"
dir_impares = "resultados_impares"

matrix = dirtoread(dir_impares, column_index=1) 
shape1 = len(matrix)
matrix = dirtoread(dir_pares, matrix, column_index=1)
shape2 = len(matrix) - shape1

X = normalize_length(matrix)
y = y_ml(shape1, shape2)

print(f"Total de amostras sem colágeno: {shape1}")
print(f"Total de amostras com colágeno: {shape2}")

clf = make_pipeline(StandardScaler(), SVC(gamma="auto"))
clf.fit(X, y)

score = clf.score(X, y)
print(f"Precisão do modelo: {score * 100:.2f}%")

decision_scores = clf.decision_function(X)

x = np.arange(len(decision_scores))

plt.plot(x[:shape1], decision_scores[:shape1], "r*", label="Sem colágeno")
plt.plot(x[shape1:], decision_scores[shape1:], "b*", label="Com colágeno")
plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
plt.xlabel("Índice da Amostra")
plt.ylabel("Score de Decisão")
plt.legend()
plt.grid()
plt.title("Scores de Decisão do Classificador SVM")
plt.show()

plt.savefig('snv.jpg', dpi=800)

print(X)
print(y)

