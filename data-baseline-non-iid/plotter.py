# import glob
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Percorso della cartella contenente i file CSV (modifica il percorso della tua cartella)
# folder_path = '.'

# # Usa glob per trovare tutti i file CSV nella cartella
# pattern = f"{folder_path}/*-test.csv"
# csv_files = glob.glob(pattern)

# # Lista per memorizzare i dati
# data = []

# print(f'found {len(csv_files)} files')
# # Scorrere i file CSV trovati
# for file in csv_files:
#     # Estrai il nome del file
#     filename = file.split('/')[-1]
    
#     # Estrai l'algoritmo e il seed dal nome del file
#     parts = filename.split('_')
#     algorithm = parts[1].split('-')[1]  # fedproxy o scaffold
#     seed = parts[0].split('-')[1]  # seed (es. 1)

#     # Carica il CSV e prendi la colonna 'accuracy'
#     df = pd.read_csv(file)
#     accuracy = df['Accuracy'].mean()  # Calcola la media della colonna 'accuracy'

#     # Aggiungi i dati al dataframe
#     data.append({
#         'Algorithm': algorithm,
#         'Seed': seed,
#         'Accuracy': accuracy
#     })

# # Creazione del dataframe con i dati
# df_data = pd.DataFrame(data)

# print(df_data)

# # Creazione del boxplot
# plt.figure(figsize=(10, 6))
# sns.boxplot(data=df_data, x='Algorithm', y='Accuracy', hue='Algorithm', showfliers=False)
# plt.title('Andamento delle accuracy per algoritmo sui vari seed')
# plt.ylim(0.0, 1.0)
# plt.savefig('boxplot.pdf', dpi= 500)
# plt.close()

import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Percorso della cartella contenente i file CSV (modifica il percorso della tua cartella)
folder_path = '.'

# Usa glob per trovare tutti i file CSV che seguono il pattern specificato
pattern = f"{folder_path}/*-test.csv"
csv_files = glob.glob(pattern)

# Lista per memorizzare i dati
data = []

# Scorrere i file CSV trovati
for file in csv_files:
    # Estrai il nome del file
    filename = file.split('/')[-1]
    
    # Estrai l'algoritmo e il seed dal nome del file
    parts = filename.split('_')
    algorithm = parts[1].split('-')[1]  # fedproxy o scaffold
    seed = parts[0].split('-')[1]  # seed (es. 1)
    areas = parts[4].split('-')[1]  # Ottieni il valore di areas (3, 5, o 9)

    # Carica il CSV e prendi la colonna 'accuracy'
    df = pd.read_csv(file)
    accuracy = df['Accuracy'].mean()  # Calcola la media della colonna 'accuracy'

    # Aggiungi i dati al dataframe
    data.append({
        'Algorithm': algorithm,
        'Seed': seed,
        'Accuracy': accuracy,
        'Areas': areas
    })

# Creazione del dataframe con i dati
df_data = pd.DataFrame(data)

# Creazione del boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_data, x='Areas', y='Accuracy', hue='Algorithm', showfliers=False)

# Impostiamo i limiti dell'asse y tra 0.0 e 1.0
plt.ylim(0.0, 1.0)

# Titolo del grafico
plt.title('Andamento delle accuracy per algoritmo sui vari valori di areas')

# Mostra il grafico
plt.savefig('boxplot.pdf', dpi= 500)
plt.close()
