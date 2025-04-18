# О проекте

Данное приложение является фронтендом для микросервиса https://github.com/armsmaster/candlestick-service (далее - **API**) и позволяет визуализировать графики котировок ценных бумаг.

Непосредственно **фронт** реализован на реакте (vite+react, директория `./react`), **backend for frontend** (далее - **бэкенд**) реализован на фреймворке fastapi (директория `./fastapi`).

# Live Demo

https://candlestick.armsmaster.ru/

# Функционал

Приложение позволяет визуализировать графики котировок ценных бумаг, имеющихся в базе API.

Пользователь может выбрать бумагу, период и таймфрейм.

Для анонимных пользователей доступен ограниченный набор данных, для авторизованных пользователей - полный.

Авторизоваться можно с помощью Oauth серверов **Google** и **Yandex**.

# Архитектура бэкенда

<img src="https://storage.yandexcloud.net/armsmaster/candlestick-service-ui-bff.drawio.png">

Full size:

- .drawio: https://storage.yandexcloud.net/armsmaster/candlestick-service-ui-bff.drawio
- .png: https://storage.yandexcloud.net/armsmaster/candlestick-service-ui-bff.drawio.png

Комментарии:

* **IAuthProcessor** - сервис для формирования ссылки внешнего Oauth сервиса авторизации
* **ICodeProcessor** - сервис для обработки ответа с секретным кодом от внешнего Oauth сервиса авторизации