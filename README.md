## BASE

### Установка:
```bash
# Получение репозитория
git clone https://github.com/TBWanderer/lksh-p-task-2025
cd lksh-p-task-2025/base

# Установка токена
export LKSH_P_AUTH_TOKEN="-> TOKEN HERE <-" 
# или можно через файл .env:
echo -ne 'LKSH_P_AUTH_TOKEN="-> TOKEN HERE <-"'

# (Опционально) установка виртуального окружения
python -m venv ./venv
source ./venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Запуск:
```bash
python main.py
```

## ADVANCED

### Установка:
```bash
# Получение репозитория
git clone https://github.com/TBWanderer/lksh-p-task-2025
cd lksh-p-task-2025/advanced

# Установка токена
export LKSH_P_AUTH_TOKEN="-> TOKEN HERE <-" 
```

### Запуск:
```bash
docker-compose up --build
# При первом запуске потребуется примерно 1-2 минуты для получения данных с сервера в первый раз
```
Cервис начнет работу на 0.0.0.0 и порту 8000. Получить к нему доступ можно как извне, так и по адресу localhost:8000
