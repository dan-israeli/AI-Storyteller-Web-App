from utils import *

with get_db_connection("database.db") as db:

    db.execute(
        'create table if not exists users('
        'id integer primary key AUTOINCREMENT,'
        'username tect not null,'
        'hash TEXT not null)'
    )

    db.execute(
        'create table if not exists stories('
        'id integer primary key AUTOINCREMENT,'
        'user_id int not null,'
        'title TEXT not null,'
        'body TEXT not null,'
        'foreign key (user_id) references users(id))'
    )