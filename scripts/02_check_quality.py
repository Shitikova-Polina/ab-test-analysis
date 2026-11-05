"""Шаг 2. Проверяем качество данных: пропуски, дубликаты, выбросы.

Результат печатаем на экран и сохраняем в results/01_data_quality.txt,
чтобы цифры в README можно было сверить с файлом.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "cookie_cats.csv"
OUT_PATH = ROOT / "results" / "01_data_quality.txt"

df = pd.read_csv(DATA_PATH)
lines = []  # сюда собираем строки отчёта

# 1. Размер таблицы и типы колонок
lines.append(f"Строк: {len(df)}, колонок: {df.shape[1]}")
lines.append(f"Колонки и типы: {dict(df.dtypes.astype(str))}")

# 2. Пропуски: сколько пустых значений в каждой колонке
lines.append(f"Пропуски по колонкам: {df.isna().sum().to_dict()}")

# 3. Дубликаты: полностью одинаковые строки и повторы одного игрока
lines.append(f"Полных дубликатов строк: {df.duplicated().sum()}")
lines.append(f"Повторяющихся userid: {df['userid'].duplicated().sum()}")

# 4. Какие значения есть в колонке с группой
lines.append(f"Группы: {df['version'].value_counts().to_dict()}")

# 5. Выбросы в числе сыгранных раундов
rounds = df["sum_gamerounds"]
lines.append("Описание sum_gamerounds:")
lines.append(rounds.describe().round(1).to_string())
lines.append(f"99-й перцентиль: {rounds.quantile(0.99):.0f}")
lines.append(f"Игроков с 0 раундов: {(rounds == 0).sum()} ({(rounds == 0).mean():.1%})")
lines.append("Пять самых больших значений:")
lines.append(df.nlargest(5, "sum_gamerounds").to_string(index=False))

# Сохраняем отчёт
OUT_PATH.parent.mkdir(exist_ok=True)
OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

# 6. Очистка. Убираем один явный выброс: 49 854 раунда за 14 дней —
# это около 3 500 раундов в день, у живого человека так не бывает
# (скорее всего, ошибка записи или бот). Следующее значение — 2 961.
# Игроков с 0 раундов НЕ убираем: они тоже попали в эксперимент,
# и если их выкинуть, мы бы искусственно завысили долю вернувшихся.
OUTLIER_LIMIT = 10_000
clean = df[df["sum_gamerounds"] < OUTLIER_LIMIT]
removed = len(df) - len(clean)
msg = f"Очистка: убрано строк с sum_gamerounds >= {OUTLIER_LIMIT}: {removed}. Осталось: {len(clean)}"
print(msg)
with open(OUT_PATH, "a", encoding="utf-8") as f:
    f.write(msg + "\n")

clean.to_csv(ROOT / "data" / "cookie_cats_clean.csv", index=False)
