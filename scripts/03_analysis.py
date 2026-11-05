"""Шаг 3. Анализ A/B-теста.

Что считаем:
  1. Одинаковы ли по размеру группы (проверка на перекос, SRM).
  2. Долю вернувшихся игроков (retention) на 1-й и 7-й день в каждой группе.
  3. Z-тест для двух долей: не случайна ли разница.
  4. 95% доверительный интервал разницы долей.
  5. Бутстрэп как второй, независимый способ получить тот же интервал.

Все числа сохраняются в results/02_ab_results.csv и results/03_summary.txt.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "cookie_cats_clean.csv")
RESULTS = ROOT / "results"
summary = []  # строки текстового отчёта

# Группа A — старая версия (контроль), группа B — новая версия
A, B = "gate_30", "gate_40"
group_a = df[df["version"] == A]
group_b = df[df["version"] == B]

# ---------- 1. Размеры групп ----------
# Если игроков делили между версиями поровну (50/50), то размеры групп
# должны быть близки. Хи-квадрат проверяет, насколько реальное деление
# похоже на 50/50. Маленькое p-value значит, что перекос вряд ли случаен.
n_a, n_b = len(group_a), len(group_b)
chi2, p_srm = stats.chisquare([n_a, n_b])  # по умолчанию ожидание: поровну
summary.append(f"Размеры групп: {A} = {n_a}, {B} = {n_b}, доля {B} = {n_b / (n_a + n_b):.2%}")
summary.append(f"Проверка деления 50/50 (хи-квадрат): chi2 = {chi2:.2f}, p-value = {p_srm:.4f}")

# ---------- 2-4. Метрики, тест, интервал ----------
rows = []
for metric in ["retention_1", "retention_7"]:
    # Сколько игроков вернулось в каждой группе
    success_a = group_a[metric].sum()
    success_b = group_b[metric].sum()
    rate_a = success_a / n_a
    rate_b = success_b / n_b
    diff = rate_b - rate_a  # насколько новая версия лучше (+) или хуже (-)

    # Z-тест для двух долей: проверяет гипотезу «доли на самом деле равны»
    z_stat, p_value = proportions_ztest([success_b, success_a], [n_b, n_a])

    # 95% доверительный интервал разницы (обычная формула Вальда):
    # стандартная ошибка разницы двух независимых долей
    se = np.sqrt(rate_a * (1 - rate_a) / n_a + rate_b * (1 - rate_b) / n_b)
    ci_low = diff - 1.96 * se
    ci_high = diff + 1.96 * se

    rows.append({
        "metric": metric,
        "rate_gate_30": round(rate_a, 5),
        "rate_gate_40": round(rate_b, 5),
        "diff_pp": round(diff * 100, 3),           # разница в процентных пунктах
        "ci95_low_pp": round(ci_low * 100, 3),
        "ci95_high_pp": round(ci_high * 100, 3),
        "z": round(z_stat, 3),
        "p_value": round(p_value, 5),
    })

table = pd.DataFrame(rows)
table.to_csv(RESULTS / "02_ab_results.csv", index=False)
summary.append("\nРезультаты z-теста (разница = gate_40 минус gate_30, в п.п.):")
summary.append(table.to_string(index=False))

# ---------- 5. Бутстрэп ----------
# Идея: много раз (10 000) случайно «перевытягиваем» игроков из каждой
# группы с возвращением, считаем разницу долей и смотрим, в каком диапазоне
# лежат 95% таких разниц. Формулы не нужны, только повторение.
rng = np.random.default_rng(42)  # фиксируем случайность, чтобы результат повторялся
N_BOOT = 10_000
boot_rows = []
for metric in ["retention_1", "retention_7"]:
    values_a = group_a[metric].to_numpy()
    values_b = group_b[metric].to_numpy()
    diffs = np.empty(N_BOOT)
    for i in range(N_BOOT):
        sample_a = rng.choice(values_a, size=len(values_a), replace=True)
        sample_b = rng.choice(values_b, size=len(values_b), replace=True)
        diffs[i] = sample_b.mean() - sample_a.mean()
    # Сохраняем все разницы, чтобы потом нарисовать их распределение
    np.save(RESULTS / f"bootstrap_{metric}.npy", diffs)
    boot_rows.append({
        "metric": metric,
        "boot_ci95_low_pp": round(np.percentile(diffs, 2.5) * 100, 3),
        "boot_ci95_high_pp": round(np.percentile(diffs, 97.5) * 100, 3),
        # В какой доле повторов новая версия оказалась хуже старой
        "share_gate40_worse": round((diffs < 0).mean(), 4),
    })

boot = pd.DataFrame(boot_rows)
boot.to_csv(RESULTS / "04_bootstrap.csv", index=False)
summary.append(f"\nБутстрэп ({N_BOOT} повторов):")
summary.append(boot.to_string(index=False))

text = "\n".join(summary) + "\n"
(RESULTS / "03_summary.txt").write_text(text, encoding="utf-8")
print(text)
