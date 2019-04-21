# social_networks_smm_analyzer
Проект предназначен для

### Как установить


5. Скачиваем файлы в папку all_reposts_by_the_schedule. В этой же папке создаем .env файл. Ваш .env должен содержать строки:

```
LOGIN_INST
PASSWORD_INST
TOKEN_VK=токен_вашего приложения_в_контакте
TOKEN_FB=токен_вашего_приложения_в_фейсбуке
TARGET_GROUP_NAME_INST
TARGET_GROUP_NAME_VK
TARGET_GROUP_ID_FB
```



"""		
### Тестовый режим

В работе программы для ускорения используются временные файлы .pickle. По умолчанию они очищаются. 
Если требуется протестировать программу для проверки работы с одинаковыми данными, то первым аргументом 
передаем название социальной сети, а дополнительным вторым аргументом после пробела передаем test.

Используем консольный ввод. Аргументом передаем название социальной сети.
Примеры запуска из консоли -

python3 main.py vkontakte test
python3 main.py instagram test
python3 main.py facebook test

python3 main.py vkontakte
python3 main.py instagram
python3 main.py facebook
"""

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
