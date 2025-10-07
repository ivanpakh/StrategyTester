import os
import pandas as pd
import chardet

# === Настройки ===
DATA_FOLDER = "quotes_data"  # Папка, где лежат CSV из MT5

# === Функция чтения котировок ===
def read_quotes_csv(file_path):
    print(f"=== Обрабатываем: {file_path}")
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return None

    try:
        # Определяем кодировку
        with open(file_path, 'rb') as f:
            enc = chardet.detect(f.read(10000))['encoding']

        print(f"→ Определена кодировка: {enc}")

        # Загружаем CSV
        df = pd.read_csv(file_path, encoding=enc, sep=',')

        # Проверяем структуру
        expected_cols = {'time', 'open', 'high', 'low', 'close', 'tick_volume'}
        if not expected_cols.issubset(set(df.columns)):
            print(f"⚠ Неожиданные колонки в {file_path}: {df.columns.tolist()}")

        # Преобразуем колонку времени, если она есть
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')

        print(f"✅ Успешно загружено {len(df)} строк\n")
        return df

    except UnicodeDecodeError:
        print(f"⚠ Ошибка декодирования. Пробуем cp1251...")
        try:
            df = pd.read_csv(file_path, encoding='cp1251', sep=',')
            return df
        except Exception as e2:
            print(f"Не удалось прочитать {file_path}: {e2}")
            return None

    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        return None


# === Основной блок ===
def main():
    if not os.path.exists(DATA_FOLDER):
        print(f"Папка {DATA_FOLDER} не найдена.")
        return

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    if not files:
        print(f"Нет CSV файлов в папке {DATA_FOLDER}.")
        return

    all_data = {}
    for file_name in files:
        file_path = os.path.join(DATA_FOLDER, file_name)
        df = read_quotes_csv(file_path)
        if df is not None:
            all_data[file_name] = df

    print(f"\n=== Итог ===")
    print(f"Загружено файлов: {len(all_data)}")
    for name, df in all_data.items():
        print(f"{name}: {len(df)} строк, {list(df.columns)}")

    # Можно дальше передавать all_data в тестер стратегий
    return all_data


if __name__ == "__main__":
    main()
