![name_workflow Actions Status](https://github.com/frolkit/yamdb_final/workflows/Yamdb/badge.svg)

# API YamDB
Это проект для обмена рецензий на произведения.Произведения можно разделить на категории: песни, фильмы, книги.
Так же можно разделить и на жанры: rock, rap - для музыки; comedy, thriller - для фильмов.
Произведения, категории и жанры создает администратор.
Рецензии на произведения могут создать авторизованные пользователи.

## Запуск приложения
Нужно собрать и запустить два докер контейнера.
```
docker-compose build
docker-compose up
```
Запустить миграции.
```
docker exec -it <container id> python manage.py migrate
```


### Настройка приложения
Создать суперпользователя
```
docker exec -it <container id> python manage.py createsuperuser
```

Загрузить данные в базу данных
```
docker cp ./dump.json <container id>:code/fixtures.json
docker exec -it  <container id> python manage.py loaddata < fixtures.json
```
