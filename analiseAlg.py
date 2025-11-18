import time
import random
import statistics
import matplotlib.pyplot as plt


# ===============================================================
# 1. ALGORITMOS
# ===============================================================

# Insertion Sort (quadrático)
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


# Merge Sort (log-linear)
def merge_sort(arr):
    arr = arr.copy()
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


# Híbrido (Merge + Insertion)
def hybrid_sort(arr, n0):
    if len(arr) <= n0:
        return insertion_sort(arr)

    mid = len(arr) // 2
    left = hybrid_sort(arr[:mid], n0)
    right = hybrid_sort(arr[mid:], n0)

    return merge(left, right)


# Função merge usada pelo Merge Sort e Híbrido
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


# ===============================================================
# 2. FUNÇÕES DE MEDIÇÃO DE TEMPO
# ===============================================================

def tempo(func, arr):
    inicio = time.perf_counter_ns()
    func(arr)
    fim = time.perf_counter_ns()
    return fim - inicio


# Encontrar empiricamente o n0
def find_n0(limit=200, rep=30):
    print("Calculando n0, aguarde...")

    for n in range(5, limit):
        insertion_times = []
        merge_times = []

        for _ in range(rep):
            arr = [random.randint(0, 1_000_000) for _ in range(n)]
            insertion_times.append(tempo(insertion_sort, arr))
            merge_times.append(tempo(merge_sort, arr))

        if statistics.mean(insertion_times) > statistics.mean(merge_times):
            print(f"n0 encontrado ≈ {n}")
            return n

    print("n0 não encontrado dentro do limite.")
    return None


# Medir tempos individuais + estatísticas
def medir_tempo(algoritmo, dados, rep=100, n0=None):
    tempos = []

    for _ in range(rep):
        inicio = time.perf_counter_ns()
        
        if algoritmo == hybrid_sort:
            algoritmo(dados, n0)
        else:
            algoritmo(dados)
        
        fim = time.perf_counter_ns()
        tempos.append(fim - inicio)

    return {
        "min": min(tempos),
        "max": max(tempos),
        "media": statistics.mean(tempos),
        "mediana": statistics.median(tempos),
        "moda": statistics.mode(tempos) if len(set(tempos)) != len(tempos) else "Não existe",
        "desvio": statistics.stdev(tempos),
        "lista": tempos
    }


# ===============================================================
# 3. GRÁFICOS
# ===============================================================

def grafico_medias(result, titulo):
    algs = ["insertion", "merge", "hibrido"]
    valores = [result[a]["media"] for a in algs]

    plt.figure(figsize=(8, 5))
    plt.bar(algs, valores)
    plt.title("Tempo Médio - " + titulo)
    plt.ylabel("Tempo (ns)")
    plt.show()


def grafico_execucoes(result, titulo):
    plt.figure(figsize=(10, 5))

    for alg, cor in zip(result.keys(), ["blue", "red", "green"]):
        plt.plot(result[alg]["lista"], label=alg, color=cor)

    plt.title("100 Execuções - " + titulo)
    plt.xlabel("Execução")
    plt.ylabel("Tempo (ns)")
    plt.legend()
    plt.show()


def grafico_min_max_media(result, titulo):
    algs = ["insertion", "merge", "hibrido"]
    mins = [result[a]["min"] for a in algs]
    maxs = [result[a]["max"] for a in algs]
    medias = [result[a]["media"] for a in algs]

    x = range(len(algs))

    plt.figure(figsize=(10, 5))
    plt.plot(x, mins, marker="o", label="Min")
    plt.plot(x, medias, marker="o", label="Média")
    plt.plot(x, maxs, marker="o", label="Max")

    plt.xticks(x, algs)
    plt.title("Min, Média e Max - " + titulo)
    plt.ylabel("Tempo (ns)")
    plt.legend()
    plt.show()


# ===============================================================
# 4. EXECUÇÃO PRINCIPAL
# ===============================================================

if __name__ == "__main__":

    # Encontrar n0 automaticamente
    n0 = find_n0(limit=800, rep=200)
    print(f"\nn0 usado no híbrido = {n0}\n")

    # Coleções de dados
    dados_ordenados = list(range(10_000))
    dados_inversos = list(range(10_000, 0, -1))

    # Medições
    result = {
        "ordenados": {
            "insertion": medir_tempo(insertion_sort, dados_ordenados),
            "merge": medir_tempo(merge_sort, dados_ordenados),
            "hibrido": medir_tempo(hybrid_sort, dados_ordenados, n0=n0)
        },
        "inversos": {
            "insertion": medir_tempo(insertion_sort, dados_inversos),
            "merge": medir_tempo(merge_sort, dados_inversos),
            "hibrido": medir_tempo(hybrid_sort, dados_inversos, n0=n0)
        }
    }

    # Mostrar resultados
    print("\n=== RESULTADOS FINAIS ===\n")
    print(result)

    # Gráficos
    print("\nGerando gráficos para dados ORDENADOS...\n")
    grafico_medias(result["ordenados"], "Ordenados")
    grafico_execucoes(result["ordenados"], "Ordenados")
    grafico_min_max_media(result["ordenados"], "Ordenados")

    print("\nGerando gráficos para dados INVERSOS...\n")
    grafico_medias(result["inversos"], "Inversos")
    grafico_execucoes(result["inversos"], "Inversos")
    grafico_min_max_media(result["inversos"], "Inversos")
