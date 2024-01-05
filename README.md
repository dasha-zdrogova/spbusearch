<!-- ABOUT THE PROJECT -->
## Описание

Сервис `spbusearch` позволяет запустить свой поисковик по файлам образовательных программ СПбГУ.

### Написан с использованием

Наш сервис использует `fastapi`, <a href="https://manticoresearch.com/">`manticore search`</a> и `docker`.

<!-- GETTING STARTED -->
## Использование

Сервис можно запускать 2-мя способами, с сипользованием docker и без. В обоих случаях manticore search и сервис запускаются отдельно (совместный запуск запланирован на будущее).

### Требования

Для рекомендуемой установки и запуска потребуется `python>=3.11` и `docker`.

### Установка

#### Рекомендуемый вариант установки

```
git clone https://github.com/dasha-zdrogova/spbusearch
cd spbusearch
docker run -e EXTRA=1 --name manticore -p 127.0.0.1:9306:9306 -p 127.0.0.1:9308:9308 -it manticoresearch/manticore
docker -dit --name spbusearch -p 80:80 spbusearch
docker exec -it spbusearch bash
python3 ./src/lib/parser.py
python3 ./src/lib/setup.py
exit
```

Запустятся 2 контейнера `docker`, один для `manticore search`, второй для нашего сервиса.

#### Вариант установки без Docker

Установить `manticore search` и запустить сервис по <a href="https://manual.manticoresearch.com/Installation/Installation">документации</a>
```git clone https://github.com/dasha-zdrogova/spbusearch
cd spbusearch
python -m pip install poetry
poetry install
poetry shell
python ./src/lib/parser.py
python ./src/lib/setup.py
uvicorn src.api.main:app --host 0.0.0.0 --port 80 --reload
```

<!-- USAGE EXAMPLES -->
## Использование

На http://127.0.0.1:0080/search?search_str=приказ должны появиться файлы, содержащие слово "приказ".

<!-- ROADMAP -->
## Роадмап

- [ ] Улучшить web UI
- [ ] Добавить CLI
- [ ] Контейнеризовать в один контейнер


