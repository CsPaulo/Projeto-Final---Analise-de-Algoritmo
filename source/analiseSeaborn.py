import time
import random
import statistics
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set_theme(style="whitegrid")  # deixa tudo bonito


# ================================================================
#  ALGORITMOS DE ORDENAÇÃO
# ================================================================
def insertion_sort(arr):
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr):
    arr = arr.copy()
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def hybrid_sort(arr, n0):
    if len(arr) <= n0:
        return insertion_sort(arr)
    mid = len(arr) // 2
    left = hybrid_sort(arr[:mid], n0)
    right = hybrid_sort(arr[mid:], n0)
    return merge(left, right)


# ================================================================
#  FUNÇÕES DE MEDIÇÃO
# ================================================================
def tempo(func, arr):
    inicio = time.perf_counter_ns()
    func(arr)
    fim = time.perf_counter_ns()
    return fim - inicio


# n₀ reduzido para ser encontrado rapidamente
def find_n0(limit=300, rep=20):
    print("Calculando n0...")
    for n in range(2, limit):
        insertion_times = []
        merge_times = []

        for _ in range(rep):
            arr = [random.randint(0, 1000000) for _ in range(n)]
            insertion_times.append(tempo(insertion_sort, arr))
            merge_times.append(tempo(merge_sort, arr))

        if statistics.mean(insertion_times) > statistics.mean(merge_times):
            print(f"n0 encontrado: {n}")
            return n

    print("n0 não encontrado dentro do limite.")
    return None


def medir_tempo_raw(algoritmo, dados, nome, rep=100):
    tempos = []
    for _ in range(rep):
        inicio = time.perf_counter_ns()
        algoritmo(dados)
        fim = time.perf_counter_ns()
        tempos.append(fim - inicio)

    return [{"algoritmo": nome, "tempo": t} for t in tempos]


# ================================================================
#  GRÁFICOS
# ================================================================
def plotar_graficos(resultados, titulo):
    df = pd.DataFrame(resultados)

    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="algoritmo", y="tempo", palette="rocket")
    plt.title(f"Distribuição dos Tempos - {titulo}")
    plt.ylabel("Tempo (ns)")
    plt.xlabel("Algoritmo")
    plt.tight_layout()
    plt.savefig(f"boxplot_{titulo}.png")
    plt.show()

    # Médias
    medias = df.groupby("algoritmo")["tempo"].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=medias, x="algoritmo", y="tempo", palette="mako")
    plt.title(f"Tempo Médio por Algoritmo - {titulo}")
    plt.ylabel("Tempo Médio (ns)")
    plt.tight_layout()
    plt.savefig(f"barras_{titulo}.png")
    plt.show()

    # Linha (execuções)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x=df.index, y="tempo", hue="algoritmo", palette="viridis")
    plt.title(f"Execuções Individuais (100 repetições) - {titulo}")
    plt.ylabel("Tempo (ns)")
    plt.xlabel("Execução")
    plt.tight_layout()
    plt.savefig(f"linha_{titulo}.png")
    plt.show()


# ================================================================
#  MAIN
# ================================================================
if __name__ == "__main__":
    n0 = find_n0()

    print(f"\nUsando n0 = {n0}\n")

    dados_ordenados = list(range(1000))
    dados_inversos = list(range(1000, 0, -1))

    # COLETANDO DADOS
    ord_ins = medir_tempo_raw(insertion_sort, dados_ordenados, "Insertion")
    ord_mer = medir_tempo_raw(merge_sort, dados_ordenados, "Merge")
    ord_hib = medir_tempo_raw(lambda x: hybrid_sort(x, n0), dados_ordenados, "Híbrido")

    inv_ins = medir_tempo_raw(insertion_sort, dados_inversos, "Insertion")
    inv_mer = medir_tempo_raw(merge_sort, dados_inversos, "Merge")
    inv_hib = medir_tempo_raw(lambda x: hybrid_sort(x, n0), dados_inversos, "Híbrido")

    # GRÁFICOS ORDENADOS
    plotar_graficos(ord_ins + ord_mer + ord_hib, "Ordenado")

    # GRÁFICOS INVERSOS
    plotar_graficos(inv_ins + inv_mer + inv_hib, "Inverso")
