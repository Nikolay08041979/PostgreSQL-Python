import psycopg2

conn = psycopg2.connect(database="client_db", user="postgres", password="12345")

def create_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS client (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                email VARCHAR(40) unique NOT NULL,
                phones VARCHAR);
                """)
        conn.commit()
        return 'База данных успешно создана'
    conn.close()

def add_client(first_name, last_name, email, phones = None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO client (first_name, last_name, email, phones)
            VALUES (%s, %s, %s, %s) RETURNING client_id;""", (first_name, last_name, email, phones))
        conn.commit()
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (cur.fetchone()[0],))
        print('Новый клиент был успешно добавлен в базу данных')
        added_client = list(cur.fetchone())
        return f'Данные о клиенте #{added_client[0]}: имя: {added_client[1]}, фамилия: {added_client[2]}, email: {added_client[3]}, телефон(ы): {added_client[4]}'
    conn.close()

def change_client(client_id, first_name = None, last_name = None, email = None, phones = None):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE client
            SET first_name = %s, last_name = %s, email = %s, phones = %s
            WHERE client_id = %s;""", (first_name, last_name, email, phones, client_id))
        conn.commit()
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        print('Данные о клиенте были успешно изменены в базе данных')
        updated_client = list(cur.fetchone())
        return f'Актуальные данные о клиенте #{client_id}: имя: {updated_client[1]}, фамилия: {updated_client[2]}, email: {updated_client[3]}, телефон(ы): {updated_client[4]}'
    conn.close()


def add_phone(client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        phone_list = (cur.fetchone()[4]).split(',')
        phone_list.append(phone)
        phones = ','.join(phone_list)
        cur.execute("""
            UPDATE client
            SET phones = %s
            WHERE client_id = %s;""", (phones, client_id))
        conn.commit()
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        print(f'Номер телефона {phone} был успешно добавлен в базу данных')
        updated_phones_list = list(cur.fetchone())
        return f'Актуальные номера телефонов клиента #{client_id}: {updated_phones_list[4]}'
    conn.close()

def delete_phone(client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        phone_list = (cur.fetchone()[4]).split(',')
        if phone in phone_list:
            phone_list.remove(phone)
        else:
            print('Такого номера телефона нет в базе данных')
        phones = ','.join(phone_list)
        cur.execute("""
            UPDATE client
            SET phones = %s
            WHERE client_id = %s;""", (phones, client_id))
        conn.commit()
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        print(f'Номер телефона {phone} был успешно удален из базы данных')
        updated_phones_list = cur.fetchone()[4]
        return f'Актуальные номера телефонов клиента #{client_id}: {updated_phones_list}'
    conn.close()

def delete_client(client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM client
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        return f'Клиент #{client_id} был успешно удален из базы данных'
    conn.close()

def find_client(key_word):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM client
            WHERE first_name = %s OR last_name = %s OR email = %s OR phones like %s;""",
                    (key_word, key_word, key_word, f'%{key_word}%'))
        conn.commit()
        found_client = list(cur.fetchone())
        return f'Найден клиент #{found_client[0]}: имя: {found_client[1]}, фамилия: {found_client[2]}, email: {found_client[3]}, телефон(ы): {found_client[4]}'
    conn.close()


#print(create_db())
#print(add_client('Виолетта', 'Мартыновна', 'mouse@mail.ru', '+73333333333,+7444444444'))
#print(change_client(2, 'Виолетта' , 'Мазур', 'mouse@mail.ru', '+73333333333,+7444444444'))
#print(add_phone(2, '+7111111111'))
#print(delete_phone(2, '+7111111111'))
#print(delete_client(2))
#print(find_client('Лиза'))

