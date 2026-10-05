# Download Telegram Bot

![Python Version](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## Функционал

* **Скачивания фото , аудио , видео на популярных платформах**
* **Без водяных знаков**
* **Разделение формата скачивания**

## Поддерживаемые платформы

* **TikToK**
* **Instagram**
* **YouTube**
* **SoundCloud**

## Важно!

**Чтобы бот работал стабильно, админу надо обновлять куки-файл боту в соответствии с платформой:**
* **TikTok** — `tt_cookie.txt`
* **Instagram** — `ig_cookie.txt`
* **YouTube** — `yt_cookie.txt`



## Установка и запуск

### 1)Клонирование репозитория
 ```bash 
 git clone https://github.com/tishetishe/download-bot 
 cd download-bot 
 ``` 

 ### 2)Настройка токена 
 Создайте файл `.env` в корневой папке проекта: 
 ```env 
 BOT_TOKEN=ваш_токен_от_botfather 
 ADMIN_ID=ваш_айди_телеграма
 ``` 

 ### 3)Запуск бота 
 ```bash python main.py ```
