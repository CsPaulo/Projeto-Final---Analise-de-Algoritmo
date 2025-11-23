import os
import csv
import statistics
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

FIGS_DIR = "figs"
os.makedirs(FIGS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")

CSV_PATH = os.path.join(FIGS_DIR, "raw_times.csv")
JSON_PATH = os.path.join(FIGS_DIR, "results.json")


def summarize_csv(path=CSV_PATH):
    """Roda um resumo rápido (usa raw_times.csv) e imprime no console."""
    if not os.path.exists(path):
        print("Arquivo não encontrado:", path)
        return
    data = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            col = row["collection"]
            alg = row["algoritmo"]
            t = int(row["tempo_ns"])
            data.setdefault(col, {}).setdefault(alg, []).append(t)

    for col, cols in data.items():
        print(f"\nColeção: {col}")
        for alg, times in cols.items():
            print(f"  {alg}: count={len(times):3}  min={min(times):12d} ns  max={max(times):12d} ns  mean={statistics.mean(times):.2f} ns  mean_ms={statistics.mean(times)/1e6:.4f} ms")


def load_df(path=CSV_PATH):
    """Carrega CSV gerado pelo experimento e normaliza colunas."""
    df = pd.read_csv(path)
    # garantir tipos e colunas
    if "tempo_ns" not in df.columns:
        raise ValueError("CSV inválido: falta coluna 'tempo_ns'")
    df["tempo_ns"] = df["tempo_ns"].astype(np.int64)
    df["tempo_ms"] = df["tempo_ns"] / 1e6
    df["algoritmo"] = df["algoritmo"].str.lower()
    df["collection"] = df["collection"].astype(str)
    df["execucao_index"] = df["execucao_index"].astype(int)
    return df


def compute_summary_table(df):
    """Gera tabela com min, max, mean, median, mode, std, count (valores em ms)."""
    rows = []
    grouped = df.groupby(["collection", "algoritmo"])["tempo_ms"]
    for (collection, alg), series in grouped:
        vals = series.values
        cnt = len(vals)
        mn = float(np.min(vals))
        mx = float(np.max(vals))
        mean = float(np.mean(vals))
        med = float(np.median(vals))
        # moda: se houver moda única, usamos; caso contrário "Não existe"
        modes = series.mode().values
        if len(modes) == 1:
            moda = float(modes[0])
        else:
            moda = "Não existe"
        std = float(np.std(vals, ddof=1)) if cnt > 1 else 0.0
        rows.append({
            "collection": collection,
            "algoritmo": alg,
            "count": cnt,
            "min_ms": round(mn, 4),
            "max_ms": round(mx, 4),
            "mean_ms": round(mean, 4),
            "median_ms": round(med, 4),
            "mode_ms": moda if isinstance(moda, str) else round(moda, 4),
            "std_ms": round(std, 4)
        })
    summary_df = pd.DataFrame(rows).sort_values(["collection", "algoritmo"])
    return summary_df


def save_summary(summary_df):
    """Salva CSV com estatísticas e gera imagem da tabela (formatada)."""
    csv_out = os.path.join(FIGS_DIR, "summary_stats.csv")
    summary_df.to_csv(csv_out, index=False)
    print("Resumo salvo em CSV:", os.path.abspath(csv_out))

    # gerar versão legível para apresentação: formatar strings
    display_df = summary_df.copy()
    numeric_cols = ["min_ms", "max_ms", "mean_ms", "median_ms", "std_ms"]
    for c in numeric_cols:
        display_df[c] = display_df[c].apply(lambda v: f"{v:.3f}" if pd.notna(v) else v)
    display_df["mode_ms"] = display_df["mode_ms"].apply(lambda v: f"{v:.3f}" if isinstance(v, (int, float, np.floating)) else v)

    # salvar imagem da tabela (legível)
    fig, ax = plt.subplots(figsize=(12, max(2, 0.45 * len(display_df))))
    ax.axis('off')
    table = ax.table(cellText=display_df.values,
                     colLabels=display_df.columns,
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.3)
    img_path = os.path.join(FIGS_DIR, "summary_table.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()
    print("Imagem da tabela salva em:", os.path.abspath(img_path))


def medias_com_erro(df):
    """Bar plot de média ± desvio padrão (já existente e aprovado)."""
    for colecao in df["collection"].unique():
        sub = df[df["collection"] == colecao]
        stats = sub.groupby("algoritmo")["tempo_ms"].agg(["mean", "std", "count"]).reset_index()
        plt.figure(figsize=(8, 6))
        ax = sns.barplot(data=stats, x="algoritmo", y="mean", palette="viridis", capsize=0.12)
        # adicionar barras de erro manualmente
        for i, row in stats.iterrows():
            ax.errorbar(i, row["mean"], yerr=row["std"], color='k', capsize=4, fmt='none')
            ax.text(i, row["mean"] * 1.02, f"{row['mean']:.2f} ms", ha='center', va='bottom', fontsize=9)
        ax.set_title(f"Tempo Médio ± Desvio - {colecao}")
        ax.set_ylabel("Tempo médio (ms)")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, f"medias_erro_{colecao}.png"), dpi=150)
        plt.close()


def min_med_max_por_colecao(df):
    """Gráfico com Min, Média e Max lado a lado para cada algoritmo (facilita comparação)."""
    for colecao in df["collection"].unique():
        sub = df[df["collection"] == colecao]
        stats = sub.groupby("algoritmo")["tempo_ms"].agg(["min", "mean", "max"]).reset_index()
        algs = stats["algoritmo"].tolist()
        mins = stats["min"].values
        means = stats["mean"].values
        maxs = stats["max"].values

        x = np.arange(len(algs))
        width = 0.25
        plt.figure(figsize=(9, 5))
        plt.bar(x - width, mins, width=width, label="Min", color="#4c72b0")
        plt.bar(x, means, width=width, label="Média", color="#55a868")
        plt.bar(x + width, maxs, width=width, label="Max", color="#c44e52")
        plt.xticks(x, algs)
        plt.ylabel("Tempo (ms)")
        plt.title(f"Min / Média / Max - {colecao}")
        for i in x:
            plt.text(i - width, mins[i] * 1.01, f"{mins[i]:.2f}", ha='center', fontsize=8)
            plt.text(i, means[i] * 1.01, f"{means[i]:.2f}", ha='center', fontsize=8)
            plt.text(i + width, maxs[i] * 1.01, f"{maxs[i]:.2f}", ha='center', fontsize=8)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, f"min_med_max_{colecao}.png"), dpi=150)
        plt.close()


def linhas_execucoes(df):
    """Gera duas versões: linear e log-scale para comparar execuções individuais.
    Usa marker pequeno e alpha para evitar sobreposição; garante todas as algs presentes."""
    for colecao in df["collection"].unique():
        sub = df[df["collection"] == colecao]
        algs = sorted(sub["algoritmo"].unique())
        colors = sns.color_palette("tab10", n_colors=len(algs))

        # linear
        plt.figure(figsize=(12, 6))
        ax = plt.gca()
        for alg, c in zip(algs, colors):
            tempos = sub[sub["algoritmo"] == alg].sort_values("execucao_index")["tempo_ms"].values
            ax.plot(np.arange(len(tempos)), tempos, label=alg, marker="o", markersize=4, linewidth=1, color=c, alpha=0.9)
        ax.set_title(f"Execuções Individuais - {colecao} (linear)")
        ax.set_xlabel("Execução")
        ax.set_ylabel("Tempo (ms)")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, f"linhas_linear_{colecao}.png"), dpi=150)
        plt.close()

        # log
        plt.figure(figsize=(12, 6))
        ax = plt.gca()
        ax.set_yscale("log")
        for alg, c in zip(algs, colors):
            tempos = sub[sub["algoritmo"] == alg].sort_values("execucao_index")["tempo_ms"].values
            ax.plot(np.arange(len(tempos)), tempos, label=alg, marker="o", markersize=4, linewidth=1, color=c, alpha=0.9)
        ax.set_title(f"Execuções Individuais - {colecao} (log scale)")
        ax.set_xlabel("Execução")
        ax.set_ylabel("Tempo (ms) - escala log")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, f"linhas_log_{colecao}.png"), dpi=150)
        plt.close()


def speedup_percentual(df, baseline="insertion"):
    """Percentual de melhoria relativo ao baseline:
       %melhora = (baseline_mean - mean) / baseline_mean * 100
       positivo => algoritmo é mais rápido que baseline."""
    for colecao in df["collection"].unique():
        sub = df[df["collection"] == colecao]
        means = sub.groupby("algoritmo")["tempo_ms"].mean()
        if baseline not in means.index:
            continue
        baseline_mean = means.loc[baseline]
        rel = ((baseline_mean - means) / baseline_mean) * 100
        rel_df = rel.reset_index(name="perc_melhora").sort_values("perc_melhora", ascending=False)
        plt.figure(figsize=(8, 5))
        ax = sns.barplot(data=rel_df, x="algoritmo", y="perc_melhora", palette="coolwarm")
        ax.axhline(0, color="k", linewidth=0.8)
        for i, v in enumerate(rel_df["perc_melhora"].values):
            va = 'bottom' if v >= 0 else 'top'
            offset = 1.5 if v >= 0 else -1.5
            ax.text(i, v + offset, f"{v:.1f}%", ha='center', va=va, fontsize=9)
        ax.set_title(f"Percentual de Melhora vs {baseline} - {colecao}")
        ax.set_ylabel("% melhora (positivo = mais rápido que baseline)")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGS_DIR, f"speedup_{colecao}.png"), dpi=150)
        plt.close()


if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        print("Arquivo não encontrado:", CSV_PATH)
        raise SystemExit(1)

    # 1) impressão rápida no terminal
    summarize_csv()

    # 2) carregar em DataFrame e gerar tabela resumida + salvar
    df = load_df()
    summary_df = compute_summary_table(df)
    print("\nTabela resumo (ms):\n")
    print(summary_df.to_string(index=False))
    save_summary(summary_df)

    # 3) gerar gráficos bonitos para análise visual
    medias_com_erro(df)
    min_med_max_por_colecao(df)
    linhas_execucoes(df)
    speedup_percentual(df)

    print("\nTodos os plots e a tabela resumo foram salvos em:", os.path.abspath(FIGS_DIR))