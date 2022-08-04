# Парсер Google таблицы с отправкой уведомлений в Телеграм.

- Получать данные с GoogleSheets
- Создать поле "Стоимость в рублях", производить конвертацию по курсу [ЦБ РФ](https://www.cbr.ru/development/SXML/)
- Дополнительно
    - [&check;] Упаковка решения в docker контейнер.
    - [&check;] Разработка функционала проверки соблюдения «срока поставки» из таблицы. В случае, если срок прошел, скрипт отправляет уведомление в Telegram.
    - [&check;] Разработка одностраничного web-приложения на основе Django или Flask. [Front-end React](https://github.com/ysur67/orders-front).


## Установка и запуск

1. Скопировать репозиторий.
1. Создать файл `.env` в корневой директории проекта. Изменить значения, заполнить токен для телеграм бота - `TELEGRAM_TOKEN`.
1. Скопировать `docker-compose.template.yml` в `docker-compose.yml`, если необходимо - внести изменения в конфиг.
1. Выполнить все шаги из [Инструкции по созданию credentials.json](/docs/GOOGLE.md)
1. Запустить
    ```bash
    docker compose up --build
    ```
1. После запуска создать суперюзера для административной панели.
    ```bash
    docker exec -it container-name python manage.py createsuperuser
    ```
1. Отправить любое сообщение вашему боту, токен которого вы используете. Иначе бот не сможет отправить вам сообщение.
1. Скопировать свой идентификатор из телеграм, создать запись получателя в административной панели.
    ![Создание получателя, шаг 1](/docs/images/6.png)
    ![Создание получателя, шаг 2](/docs/images/7.png)