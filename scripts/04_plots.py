"""Шаг 4. Графики. Сохраняются в папку figures/."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # рисуем в файл, без окна на экране
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
RESULTS = ROOT / "results"

df = pd.read_csv(ROOT / "data" / "cookie_cats_clean.csv")
ab = pd.read_csv(RESULTS / "02_ab_results.csv")

# Единый стиль: светлый фон, тонкая сетка, одинаковые цвета групп
COLORS = {"gate_30": "#2a78d6", "gate_40": "#eb6834"}  # синий — старая версия, оранжевый — новая
LABELS = {"gate_30": "gate_30 (старая)", "gate_40": "gate_40 (новая)"}
plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "text.color": "#0b0b0b",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 0.8,
    "font.size": 11,
})

# ---------- График 1. Размеры групп ----------
sizes = df["version"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar([LABELS[g] for g in sizes.index], sizes.values,
              color=[COLORS[g] for g in sizes.index], width=0.5)
ax.bar_label(bars, labels=[f"{v:,}".replace(",", " ") for v in sizes.values], padding=3)
ax.axhline(sizes.sum() / 2, color="#52514e", linestyle="--", linewidth=1)
ax.text(1.3, sizes.sum() / 2, "ровно\nпополам", va="center", color="#52514e", fontsize=9)
ax.set_ylabel("Игроков")
ax.set_title("1. Сколько игроков в каждой группе")
ax.set_ylim(0, sizes.max() * 1.15)
ax.grid(axis="x", visible=False)  # вертикальная сетка столбцам не нужна
fig.tight_layout()
fig.savefig(FIG / "1_group_sizes.png", dpi=150)
plt.close(fig)

# ---------- График 2. Доля вернувшихся с доверительными интервалами ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(2)  # две метрики: 1-й и 7-й день
width = 0.35
for i, group in enumerate(["gate_30", "gate_40"]):
    rates = ab[f"rate_{group}"].to_numpy() * 100
    n = (df["version"] == group).sum()
    # Погрешность доли в каждой группе (95%): 1,96 * стандартная ошибка
    err = 1.96 * np.sqrt(rates / 100 * (1 - rates / 100) / n) * 100
    bars = ax.bar(x + (i - 0.5) * width, rates, width * 0.95, yerr=err, capsize=4,
                  color=COLORS[group], label=LABELS[group], error_kw={"ecolor": "#52514e"})
    ax.bar_label(bars, labels=[f"{r:.1f}%" for r in rates], padding=6, fontsize=9)
ax.set_xticks(x, ["Вернулись через 1 день", "Вернулись через 7 дней"])
ax.set_ylabel("Доля игроков, %")
ax.set_title("2. Доля вернувшихся игроков (чёрточки — 95% интервал)")
ax.legend(frameon=False)
ax.set_ylim(0, 55)
ax.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(FIG / "2_retention_by_group.png", dpi=150)
plt.close(fig)

# ---------- График 3. Бутстрэп: распределение разницы ----------
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
titles = {"retention_1": "1-й день", "retention_7": "7-й день"}
for ax, metric in zip(axes, ["retention_1", "retention_7"]):
    diffs = np.load(RESULTS / f"bootstrap_{metric}.npy") * 100
    low, high = np.percentile(diffs, [2.5, 97.5])
    ax.hist(diffs, bins=50, color="#2a78d6", edgecolor="#fcfcfb", linewidth=0.5)
    ax.axvline(0, color="#e34948", linewidth=2, label="0 = нет разницы")
    ax.axvspan(low, high, color="#2a78d6", alpha=0.12, label="95% интервал")
    ax.set_title(f"Удержание на {titles[metric]}")
    ax.set_xlabel("Разница gate_40 − gate_30, п.п.")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
axes[0].set_ylabel("Сколько раз из 10 000")
fig.suptitle("3. Бутстрэп: какой может быть разница, если повторить тест много раз")
fig.tight_layout()
fig.savefig(FIG / "3_bootstrap_diff.png", dpi=150)
plt.close(fig)

# ---------- График 4. Сколько раундов сыграли игроки ----------
# Обрезаем хвост на 200 раундах, чтобы было видно основную массу игроков
fig, ax = plt.subplots(figsize=(8, 4))
bins = np.arange(0, 201, 5)
for group in ["gate_30", "gate_40"]:
    rounds = df.loc[df["version"] == group, "sum_gamerounds"]
    # Вес каждого игрока = 100 / размер группы, тогда высота столбца —
    # процент игроков группы в этом интервале (группы разного размера сравнимы)
    weights = np.full(len(rounds), 100 / len(rounds))
    ax.hist(rounds.clip(upper=200), bins=bins, weights=weights, histtype="step",
            linewidth=2, color=COLORS[group], label=LABELS[group])
ax.axvline(30, color="#52514e", linestyle=":", linewidth=1)
ax.axvline(40, color="#52514e", linestyle=":", linewidth=1)
ax.text(31, ax.get_ylim()[1] * 0.9, "ворота 30 и 40", color="#52514e", fontsize=9)
ax.set_xlabel("Сыграно раундов за 14 дней (всё, что больше 200, в последнем столбце)")
ax.set_ylabel("% игроков группы (шаг 5 раундов)")
ax.set_title("4. Распределение числа сыгранных раундов")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "4_gamerounds_hist.png", dpi=150)
plt.close(fig)

print("Графики сохранены в", FIG)
