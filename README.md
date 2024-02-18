## :whale: LayerZero Stats Checker
![Screenshot](https://i.imgur.com/uCeXpIC.png)  

Софт массово получает статистику по указанным кошелькам. Данные парятся с **LayerZero API** и **Copilot API**. 

| Данные                    | LayerZero API      | Copilot API        |
| :---                      |     :---:          |     :---:          |
| Ранг                      |                    | :heavy_check_mark: |
| Объем                     |                    | :heavy_check_mark: |
| Кол-во транзакций         | :heavy_check_mark: |                    |
| Уникальные контракты      |                    | :heavy_check_mark: |
| Исходящие сети            | :heavy_check_mark: |                    |
| Сети назначения           | :heavy_check_mark: |                    |
| Активные месяцы           |                    | :heavy_check_mark: |
| Последняя активность      | :heavy_check_mark: |                    |
| Транзакция в майннете     |                    |                    |


> [!NOTE]
> Исходящие сети и сети назначения парятся списком, вы сможете проверить какие сети вы использовали


## :green_book: Первый запуск
> [!TIP]
> В качестве **IDE** рекомендую использовать [**PyCharm Community Edition**](https://www.jetbrains.com/ru-ru/pycharm/)

> [!IMPORTANT]
> Для работы необходим [**Python 3.11**](https://www.python.org/downloads/release/python-3110/)  
> Установить зависимости можно командой `pip install -r requirements.txt`

1. Поместите в файл `data/wallets.txt` список кошельков
1. Укажите имена для кошельков в `data/names.txt`
1. **Обязательно** укажите прокси в файле `data/proxies.txt` :exclamation: _(формат: login:password@ip:port)_
1. После запуска в терминале вы увидите сообщение с ссылкой, перейдите по ней _(по умолчанию: http://127.0.0.1:8080)_

Для начала проверки нажмите на странице кнопку **Обновить данные**. 

> [!IMPORTANT]
> После установки софт создает базу данных, если вы хотите удалить  
> или обновить кошельки из таблицы, удалите в корне проекта файл `database.sqlite`  
> При повторном запуске софт повторно создат базу данных используя  
> кошельки и имена из папки `data/`


## :money_with_wings: Донаты

Для благодарностей можете отправить любые токены на кошелек **0x86B0ebc4F5dd71AD5ad37255681F6dc70e79D0F6**
