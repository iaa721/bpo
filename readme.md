Эндпоинты

№	Метод	Эндпоинт	Описание
1	POST	/register	Регистрация пользователя
2	POST	/login	Вход пользователя
3	GET	/logout	Выход из аккаунта
4	POST	/games/new	Создать новую игру
5	GET	/games	Получить список всех игр
6	GET	/games/int:game_id	Просмотреть информацию о игре
7	GET	/myprofile	Выдает информацию о текущем пользователе
8	POST	/games/int:game_id/delete	Удалить игру
9	POST	/games/int:game_id/comment/add	Добавить комментарий к игре
10	POST	/games/int:game_id/comment/delete	Удалить комментарий
11	POST	/games/int:game_id/download	Скачать игру
12	GET	/myprofile/favorites	Выдает информацию о том какие игры в избранном у текущего пользователя
13	POST	/games/int:game_id/report	Сообщить о проблеме или нарушении
14	POST	/games/int:game_id/like	Поставить лайк игре
15	POST	/games/int:game_id/unlike	Убрать лайк
16	POST	/games/int:game_id/favorite	Добавить игру в избранное
17	POST	/games/int:game_id/unfavorite	Убрать из избранного
18	GET	/user/int:user_id/games	Посмотреть все игры пользователя
19	POST	/game/int:game_id/report	Пожаловаться на игру
20	POST	/game/int:game_id/comment/report	Пожаловаться на комментарий
