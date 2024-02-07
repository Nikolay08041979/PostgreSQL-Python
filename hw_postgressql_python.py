import psycopg2

conn = psycopg2.connect(database="client_db", user="postgres", password="12345")

def create_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS client (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                email VARCHAR(40) UNIQUE NOT NULL);
                """)
        conn.commit()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                phone_id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES client(client_id),
                phone1 VARCHAR(20),
                phone2 VARCHAR(20),
                phone3 VARCHAR(20),
                phone4 VARCHAR(20),
                phone5 VARCHAR(20));
                """)
        conn.commit()
        return 'База данных успешно создана'
    conn.close()

def add_client(first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        result = find_client(first_name=first_name, last_name=last_name, email=email)
        if result == 'По вашему запросу ничего не найдено':
            cur.execute("""
                INSERT INTO client (first_name, last_name, email)
                VALUES (%s, %s, %s) RETURNING client_id;""", (first_name, last_name, email))
            conn.commit()
            client_id = cur.fetchone()[0]
            if phones is not None:
                phones_list = phones.strip().split(',')
                cur.execute("""
                    INSERT INTO phones (phone1, client_id)
                    VALUES (%s, %s);""", (phones_list[0], client_id))
                conn.commit()
                if len(phones_list) > 1:
                    for idx, phone_number in enumerate(phones_list[1:]):
                        cur.execute("""
                            UPDATE phones
                            SET phone%s = %s
                            WHERE client_id = %s;""", (idx + 2, phone_number, client_id))
                        conn.commit()
            cur.execute("""
                SELECT * FROM client
                WHERE client_id = %s;""", (client_id,))
            client_new = cur.fetchone()
            cur.execute("""
                SELECT * FROM phones
                WHERE client_id = %s;""", (client_id,))
            phone_list_new = [phone for phone in list(cur.fetchone()[2:]) if phone is not None]
            print(f'Новый клиент был успешно добавлен в базу данных')
            return f'Данные о клиенте #{client_new[0]}: имя: {client_new[1]}, фамилия: {client_new[2]}, email: {client_new[3]}, телефоны: {(", ").join(phone_list_new)}'
        else: # if result != 'По вашему запросу ничего не найдено': client is already in db
            cur.execute("""
                SELECT * FROM client
                WHERE first_name = %s AND last_name = %s AND email = %s;""", (first_name, last_name, email))
            client_found = cur.fetchone()
            return f'Клиент #{client_found[0]} уже есть в базе данных'
    conn.close()

def add_phone(client_id, phone_number):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM phones
            WHERE client_id = %s;""", (client_id,))
        phone_list_check = cur.fetchone()
        if phone_list_check is not None:
            phone_list_current = [phone for phone in list(phone_list_check[2:]) if phone is not None]
            if len(phone_list_current) == 5:
                return 'Достигнуто максимальное количество номеров телефонов. Воспользуйтесь функцией удаления или изменения номера телефона'
            elif phone_number in phone_list_current:
                return f'Номер телефона {phone_number} уже есть в базе данных'
            else: # if len(phone_list_current) < 5:
                cur.execute("""
                    UPDATE phones
                    SET phone%s = %s
                    WHERE client_id = %s;""", (len(phone_list_current)+1, phone_number, client_id))
                conn.commit()
                print(f'Номер телефона {phone_number} был успешно добавлен в базу данных')
                cur.execute("""
                    SELECT * FROM phones
                    WHERE client_id = %s;""", (client_id,))
                phone_list_updated = [phone for phone in list(cur.fetchone()[2:]) if phone is not None]
                return f'Актуальные номера телефонов клиента #{client_id}: {", ".join(phone_list_updated)}'
        else: # if phone_list_check is None (client has no phone numbers):
            cur.execute("""
                INSERT INTO phones (phone1, client_id)
                VALUES (%s, %s);""", (phone_number, client_id))
            conn.commit()
            return f'Номер телефона {phone_number} был успешно внесен в базу данных'
    conn.close()


def change_client(client_id, first_name = None, last_name = None, email = None, phones = None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM client
            WHERE client_id = %s;""", (client_id,))
        client_check = cur.fetchone()
        if client_check is not None: # Client exists in db
            if first_name is not None:
                cur.execute("""
                    UPDATE client
                    SET first_name = %s
                    WHERE client_id = %s;""", (first_name, client_id))
                conn.commit()
            if last_name is not None:
                cur.execute("""
                    UPDATE client
                    SET last_name = %s
                    WHERE client_id = %s;""", (last_name, client_id))
                conn.commit()
            if email is not None:
                cur.execute("""
                    UPDATE client
                    SET email = %s
                    WHERE client_id = %s;""", (email, client_id))
                conn.commit()
        #cur.execute("""
        #     UPDATE client
        #     SET first_name = %s, last_name = %s, email = %s
        #     WHERE client_id = %s;""", (first_name, last_name, email, client_id))
        # conn.commit()
            if phones is not None:
                phones_list = phones.strip().split(',')
                for idx, phone_number in enumerate(phones_list):
                    cur.execute("""
                        UPDATE phones
                        SET phone%s = %s
                        WHERE client_id = %s;""", (idx + 1, phone_number, client_id))
                    conn.commit()
            cur.execute("""
                SELECT * FROM client
                WHERE client_id = %s;""", (client_id,))
            client_updated = cur.fetchone()
            cur.execute("""
                SELECT * FROM phones
                WHERE client_id = %s;""", (client_id,))
            phone_list_updated = [phone for phone in list(cur.fetchone()[2:]) if phone is not None]
            print(f'Данные о клиенте были успешно изменены в базе данных')
            return f'Актуальные данные о клиенте #{client_updated[0]}: имя: {client_updated[1]}, фамилия: {client_updated[2]}, email: {client_updated[3]}, телефоны: {(", ").join(phone_list_updated)}'
        else: # Client doesn't exist in db
            return 'Клиент не найден в базе данных. Уточните client_id и повторите попытку поиска'
    conn.close()

def delete_phone(client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM phones
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        phone_list_current = list(cur.fetchone()[2:])
        if phone not in phone_list_current:
            return f'Такой номер телефона не закреплен за клиентом {client_id}. Воспользуйтесь функцией поиска по базе данных'
        else:
            phone_list_current.remove(phone)
        cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        cur.execute("""
            INSERT INTO phones (phone1, client_id)
            VALUES (%s, %s);""", (phone_list_current[0], client_id))
        conn.commit()
        if len(phone_list_current) > 1:
            for idx, phone_number in enumerate(phone_list_current[1:]):
                cur.execute("""
                    UPDATE phones
                    SET phone%s = %s
                    WHERE client_id = %s;""", (idx + 2, phone_number, client_id))
                conn.commit()
        cur.execute("""
            SELECT * FROM phones
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        print(f'Номер телефона {phone} был успешно удален из базы данных')
        phone_list_updated = [phone for phone in list(cur.fetchone()[2:]) if phone is not None]
        return f'Актуальные номера телефонов клиента #{client_id}: {", ".join(phone_list_updated)}'
    conn.close()

def delete_client(client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        cur.execute("""
            DELETE FROM client
            WHERE client_id = %s;""", (client_id,))
        conn.commit()
        return f'Клиент #{client_id} был успешно удален из базы данных'
    conn.close()

def find_client(first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        search_dict = {}
        if first_name is not None:
            search_dict['first_name'] = first_name
        if last_name is not None:
            search_dict['last_name'] = last_name
        if email is not None:
            search_dict['email'] = email

        if len(search_dict) > 0:
            search_query = ' AND '.join(f'{key} = %s' for key in search_dict)
            cur.execute(f"""
                SELECT * FROM client
                WHERE {search_query};""", tuple(search_dict.values()))
            client_found_all = cur.fetchall()

            if len(client_found_all) == 0:
                    return f'По вашему запросу ничего не найдено'

            elif len(client_found_all) == 1:
                client_id = client_found_all[0][0]
                cur.execute("""
                    SELECT * FROM phones
                    WHERE client_id = %s;""", (client_id,))
                phone_list_check = cur.fetchone()
                phone_found = [phone for phone in list(phone_list_check[2:]) if phone is not None]
                return f'По вашему запросу найден клиент #{client_found_all[0][0]}: имя: {client_found_all[0][1]}, фамилия: {client_found_all[0][2]}, email: {client_found_all[0][3]}, телефоны: {(", ").join(phone_found)}'

            else: # if len(client_found_all) > 1:
                if phone is not None:
                    phone_clientid_match_all = []
                    for client in client_found_all:
                        cur.execute("""
                            SELECT * FROM phones
                            WHERE client_id = %s
                            and (phone1 = %s
                            or phone2 = %s
                            or phone3 = %s
                            or phone4 = %s
                            or phone5 = %s);""", (client[0], phone, phone, phone, phone, phone))
                        conn.commit()
                        phone_clientid_match = cur.fetchone()
                        if phone_clientid_match is not None:
                            phone_clientid_match_all.append(phone_clientid_match)
                    if len(phone_clientid_match_all) == 1:
                        phone_clientid_match_filled = [phone for phone in list(phone_clientid_match_all[0][2:]) if phone is not None]
                        cur.execute("""
                            SELECT * FROM client
                            WHERE client_id = %s;""", (phone_clientid_match_all[0][1],))
                        client_details = cur.fetchone()
                        return f'По Вашему запросу найден клиент #{client_details[0]}: имя: {client_details[1]}, фамилия: {client[2]}, email: {client[3]}, телефоны: {(", ").join(phone_clientid_match_filled)}'

                else: # if phone is None:
                    return f'По вашему запросу найдено {len(client_found_all)} клиента(ов). Уточните данные клиента и повторите поиск'

        else: # if len(search_dict) == 0:
            if phone is not None:
                cur.execute("""
                     SELECT * FROM phones
                     WHERE phone1 = %s
                     OR phone2 = %s
                     OR phone3 = %s
                     OR phone4 = %s
                     OR phone5 = %s;""", (phone, phone, phone, phone, phone))
                phone_found_all = cur.fetchall()

                if len(phone_found_all) == 0:
                     return f'По вашему запросу ничего не найдено'

                elif len(phone_found_all) == 1:
                    client_id = phone_found_all[0][1]
                    cur.execute("""
                        SELECT * FROM client
                        WHERE client_id = %s;""", (client_id,))
                    client_found = cur.fetchone()
                    return f'По вашему запросу найден клиент #{client_found[0]}: имя: {client_found[1]}, фамилия: {client_found[2]}, email: {client_found[3]}, телефоны: {", ".join (phone_found_all[0][2:])}'

                else: # if len(phone_found_all) > 1:
                    return f'По вашему запросу найдено {len(phone_found_all)} клиента(ов). Уточните данные клиента и повторите поиск'
    conn.commit()

if __name__ == '__main__':
    #print(create_db())
    #print(add_client('Виолетта' , 'Мазур', 'mouse3000@gmail.com', '+73333333333,+7444444444,+7222222222'))
    #print(change_client(58, 'Виолетта' , 'Мартыновка', 'mouse000000@mail.ru', '+7000000000,+7123456789,+7987654321'))
    #print(add_phone(59, '+7555555555'))
    #print(delete_phone(58, '+7222222222'))
    #print(delete_client(58))
    #print(find_client('Виолетта', None, None, None))

