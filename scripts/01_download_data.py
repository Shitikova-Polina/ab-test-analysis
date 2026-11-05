"""Шаг 1. Скачиваем данные A/B-теста Cookie Cats.

Файл лежит в открытом репозитории на GitHub, регистрация не нужна.
После скачивания сверяем контрольную сумму: если файл в зеркале
когда-нибудь поменяют, мы это сразу заметим.
"""
import hashlib
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/ryanschaub/"
    "Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv"
)
# Контрольная сумма файла, на котором сделан анализ (скачан 2026-11-04)
EXPECTED_SHA256 = "5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd"

# Путь считаем от папки проекта, чтобы скрипт работал из любой папки
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cookie_cats.csv"


def main():
    if not DATA_PATH.exists():
        print("Скачиваю", URL)
        urllib.request.urlretrieve(URL, DATA_PATH)
    else:
        print("Файл уже скачан:", DATA_PATH)

    # Считаем SHA-256 файла и сравниваем с ожидаемой
    sha = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(
            f"Контрольная сумма не совпала: {sha}. "
            "Файл в источнике изменился, результаты могут отличаться от README."
        )
    print("Контрольная сумма совпала, файл тот же, что в анализе.")


if __name__ == "__main__":
    main()
