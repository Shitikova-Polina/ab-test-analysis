# Данные

Файл `cookie_cats.csv` в репозиторий не положен: у набора на Kaggle лицензия указана как «Unknown».
Скачайте его скриптом:

```bash
python scripts/01_download_data.py
```

Скрипт берёт файл из открытого зеркала на GitHub и сверяет контрольную сумму SHA-256,
чтобы было видно, что анализ сделан ровно на этом файле.

- Зеркало: https://github.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats
- Исходный набор: проект DataCamp «Mobile Games A/B Testing with Cookie Cats»
  (https://www.datacamp.com/projects/184), он же на Kaggle: https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing
- Размер: около 2,7 МБ, 90 189 строк

Колонки:

| Колонка | Что значит |
|---|---|
| `userid` | номер игрока |
| `version` | группа теста: `gate_30` (старая версия, «ворота» на 30-м уровне) или `gate_40` (новая, ворота на 40-м) |
| `sum_gamerounds` | сколько раундов игрок сыграл за первые 14 дней после установки |
| `retention_1` | вернулся ли игрок через 1 день после установки (True/False) |
| `retention_7` | вернулся ли через 7 дней (True/False) |
