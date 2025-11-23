import time
import random
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import csv

# ...existing code...

# tema bonito
sns.set_theme(style="whitegrid", palette="muted")

# criar pasta de saída de figuras
FIGS_DIR = "figs"
os.makedirs(FIGS_DIR, exist_ok=True)

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

    # tratar moda sem erro
    try:
        moda = statistics.mode(tempos)
    except statistics.StatisticsError:
        moda = "Não existe"

    desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0

    return {
        "min": min(tempos),
        "max": max(tempos),
        "media": statistics.mean(tempos),
        "mediana": statistics.median(tempos),
        "moda": moda,
        "desvio": desvio,
        "lista": tempos
    }


# ===============================================================
# 3. GRÁFICOS
# ===============================================================

def _save_and_maybe_show(titulo, sufixo):
    filename = f"{titulo.replace(' ', '_')}_{sufixo}.png"
    path = os.path.join(FIGS_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Gráfico salvo em: {os.path.abspath(path)}")
    try:
        plt.show()
    except Exception:
        # ambiente headless: apenas salvar
        pass
    finally:
        plt.close()


def grafico_medias(result, titulo):
    algs = ["insertion", "merge", "hibrido"]
    # converter para ms para melhor leitura
    valores_ms = [result[a]["media"] / 1e6 for a in algs]

    plt.figure(figsize=(8, 5))
    ax = plt.gca()
    sns.barplot(x=algs, y=valores_ms, palette="muted", ax=ax)
    plt.title("Tempo Médio - " + titulo)
    plt.ylabel("Tempo médio (ms)")
    _save_and_maybe_show(titulo + "_medias", "medias")


def grafico_execucoes(result, titulo):
    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    # plotar cada algoritmo; converter lista para ms
    for alg, cor in zip(result.keys(), ["#1f77b4", "#ff7f0e", "#2ca02c"]):
        tempos_ms = [t / 1e6 for t in result[alg]["lista"]]
        sns.lineplot(x=range(len(tempos_ms)), y=tempos_ms, label=alg, color=cor, ax=ax, marker="o", linewidth=1)

    plt.title("100 Execuções - " + titulo)
    plt.xlabel("Execução")
    plt.ylabel("Tempo (ms)")
    plt.legend()
    _save_and_maybe_show(titulo + "_execucoes", "execucoes")


def grafico_min_max_media(result, titulo):
    algs = ["insertion", "merge", "hibrido"]
    mins_ms = [result[a]["min"] / 1e6 for a in algs]
    maxs_ms = [result[a]["max"] / 1e6 for a in algs]
    medias_ms = [result[a]["media"] / 1e6 for a in algs]

    x = range(len(algs))

    plt.figure(figsize=(10, 5))
    ax = plt.gca()
    sns.lineplot(x=list(x), y=mins_ms, marker="o", label="Min", ax=ax)
    sns.lineplot(x=list(x), y=medias_ms, marker="o", label="Média", ax=ax)
    sns.lineplot(x=list(x), y=maxs_ms, marker="o", label="Max", ax=ax)

    plt.xticks(x, algs)
    plt.title("Min, Média e Max - " + titulo)
    plt.ylabel("Tempo (ms)")
    plt.legend()
    _save_and_maybe_show(titulo + "_min_med_max", "min_med_max")


# ===============================================================
# 4. EXECUÇÃO PRINCIPAL
# ===============================================================

if __name__ == "__main__":

    # Encontrar n0 automaticamente
    n0 = find_n0(limit=800, rep=200)
    print(f"\nn0 usado no híbrido = {n0}\n")

    # Coleções de dados (10k conforme enunciado)
    dados_ordenados = list(range(10_000))
    dados_inversos = list(range(10_000, 0, -1))

    # Medições (rep padrão = 100 conforme enunciado)
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

    # SALVAR DADOS (JSON + CSV com tempos brutos) para reuso posterior
    json_path = os.path.join(FIGS_DIR, "results.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(result, jf, indent=2, ensure_ascii=False)
    print(f"Dados salvos em: {os.path.abspath(json_path)}")

    csv_path = os.path.join(FIGS_DIR, "raw_times.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(["collection", "algoritmo", "execucao_index", "tempo_ns"])
        for collection_name, collection_data in result.items():
            for alg_name, stats in collection_data.items():
                for idx, t in enumerate(stats["lista"]):
                    writer.writerow([collection_name, alg_name, idx, t])
    print(f"Tempos brutos salvos em: {os.path.abspath(csv_path)}")

    # Gráficos (salvos em figs/)
    print("\nGerando gráficos para dados ORDENADOS...\n")
    grafico_medias(result["ordenados"], "Ordenados")
    grafico_execucoes(result["ordenados"], "Ordenados")
    grafico_min_max_media(result["ordenados"], "Ordenados")

    print("\nGerando gráficos para dados INVERSOS...\n")
    grafico_medias(result["inversos"], "Inversos")
    grafico_execucoes(result["inversos"], "Inversos")
    grafico_min_max_media(result["inversos"], "Inversos")