import psycopg2


def create_db(cursor):
    cursor.execute("""
        CREATE TABLE IF not EXISTS client_info(
        client_id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        surname VARCHAR(40) NOT NULL,
        email VARCHAR(40) NOT NULL UNIQUE
        );
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phone_number(
        id SERIAL PRIMARY KEY,
        number VARCHAR(40),
        client_id INTEGER NOT NULL REFERENCES client_info(client_id)            
        );
        """)


def find_client(cursor):
    column = input('Введите название столбца для поиска \n'
                   '(имя, фамилия, email, телефон): ')
    dict_column = {'имя': 'name', 'фамилия': 'surname', 'email': 'email',
                   'телефон': 'number'}
    key = dict_column[column]
    value = input('Введите значение этого столбца: ')
    cursor.execute(f"""SELECT * FROM client_info c
                    JOIN phone_number p ON c.client_id = p.client_id
                    WHERE {key}=%s;
                    """, (value, ))
    return print(cursor.fetchall())


class Client:
    def __init__(self, client_id, first_name, last_name, email, phone=None):
        self.client_id = client_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

    def add_new_client(self, cursor):
        cursor.execute("""
                INSERT INTO client_info(client_id, name, surname, email)
                VALUES(%s, %s, %s, %s);
                """, (self.client_id, self.first_name, self.last_name, self.email,))
        cursor.execute("""
                INSERT INTO phone_number(number, client_id)
                VALUES(%s, %s);
                """, (self.phone, self.client_id))

    def add_phone(self, cursor, new_phone, client_id):
        cursor.execute("""
                 INSERT INTO phone_number(number, client_id)
                 VALUES(%s, %s);
                 """, (new_phone, client_id))

    def update_client(self, cursor):
        column = input('Введите название столбца, значение в котором хотите изменить \n'
                       '(имя, фамилия, email, телефон): ')
        dict_column = {'имя': 'name', 'фамилия': 'lastname', 'email': 'Email',
                       'телефон': 'phone'}
        key = dict_column[column]
        value = input('Введите новое значение для этого столбца: ')
        if key != 'phone':
            cursor.execute(f"""
                UPDATE client_info SET {key}=%s WHERE client_id=%s;
                        """, (value, self.client_id))
        else:
            cursor.execute(f"""
                UPDATE phone_number SET {key}=%s WHERE client_id=%s;
                        """, (value, self.client_id))

    def del_client_phone(self, cursor, phone: str):
        cursor.execute("""
                DELETE FROM phone_number WHERE client_id=%s and number=%s;
                        """, (self.client_id, phone))

    def del_client(self, cursor):
        cursor.execute("""
                DELETE FROM phone_number WHERE client_id=%s;
                        """, (self.client_id,))
        cursor.execute("""
                DELETE FROM client_info WHERE client_id=%s;
                        """, (self.client_id,))


if __name__ == '__main__':
    with psycopg2.connect(database="client_manager", user="postgres", password="123456") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    DROP TABLE phone_number;
                    DROP TABLE client_info;
                    """)
            create_db(cur)
            client1 = Client(1, "Anna", "Nikitina", "nikitina_anna08@list.ru", "911148696")
            client2 = Client(2, "Petr", "Ivanov", "9117405659@mail.ru", "9117405659")
            client1.add_new_client(cur)
            client2.add_new_client(cur)
            client1.add_phone(cur, "9111484606", 1)
            client2.add_phone(cur, "9115562545", 2)
            client2.update_client(cur)
            client2.del_client_phone(cur, "9111484606")
            client2.del_client(cur)
            find_client(cur)

conn.close()
