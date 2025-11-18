import time 
import random
import statistics
import matplotlib.pyplot as plt

## Trabalho - Análise téorica (notação assintótica) X análise empírica (tempo de execução)

# Insertion Sort 
def insertion_sort(arr):
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+ 1] = arr[j]
            j -= 1
            arr[j + 1] = key
    return arr

# Merge Sort
def merge_sort(arr):
    arr = arr.copy()
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)

# Hybrid Sort
def hybrid_sort(arr, n0):
    if len(arr) <= n0: 
        return insertion_sort(arr)
    
    mid = len(arr) // 2
    left = hybrid_sort(arr[:mid], n0)
    right = hybrid_sort(arr[mid:], n0)

    return merge(left, right)

# Function merge 
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

# function find n0
def tempo(func, arr):
    inicio = time.perf_counter_ns()
    func(arr)
    fim = time.perf_counter_ns()
    return fim - inicio

def find_n0(limit=2000, rep=2000):
    for n in range(2, limit):
        tempo_insertion = []
        tempo_merge = []

        for _ in range(rep):
            arr = [random.randint(0,1000000) for _ in range(n)]
            tempo_insertion.append(tempo(insertion_sort, arr))
            tempo_merge.append(tempo(merge_sort, arr))
        
        if (sum(tempo_insertion) / rep) > (sum(tempo_merge) / rep):
            return n
    return None

def medir_tempo(algoritmo, dados, rep=100):
    tempos = []
    for _ in range(rep):
        inicio = time.perf_counter_ns()
        algoritmo(dados)
        fim = time.perf_counter_ns()
        tempos.append(fim - inicio)
    
    return  {
        "min": min(tempos),
        "max": max(tempos),
        "media": statistics.mean(tempos),
        "mediana": statistics.median(tempos),
        "moda": statistics.mode(tempos) if len(set(tempos)) != len(tempos) else "não existe",
        "desvio padrão": statistics.stdev(tempos)
    }


if __name__ == "__main__": 
    # Coleção com dados ordernados
    dados_ordernados = list(range(10000))

    # Coleção com dados inveros
    dados_inversos = list(range(10000, 0, -1))

    result = {
        "Ordernados": {
            "insertion": medir_tempo(insertion_sort, dados_ordernados),
            "merge": medir_tempo(merge_sort, dados_ordernados),
            "hibrido": medir_tempo(hybrid_sort, dados_ordernados)
        }, 
        "inversos": {
            "insertion": medir_tempo(insertion_sort, dados_inversos),
            "merge": medir_tempo(merge_sort, dados_inversos),
            "hibrido": medir_tempo(hybrid_sort, dados_inversos)
        }
    }

    print(result)



