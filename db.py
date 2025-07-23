import psycopg2
from decouple import config

DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')


def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def create_table_users():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(14) UNIQUE NOT NULL,
            language VARCHAR(10) DEFAULT 'uz' -- Til uchun ustun
        );
        """)
        conn.commit()
        cur.close()
        conn.close()


def save_user(user_id, name, phone, language):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (user_id, name, phone, language)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, name, phone, language))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            cur.close()
            conn.close()



def check_user_language(user_id):
    try:
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT language FROM users WHERE user_id = %s;", (user_id,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            if result:
                return result[0]  # language qiymati
        return False

    except Exception as e:
        print(f"Xatolik: {e}")
        return None



def update_user_field(tg_id, field_name, new_value):
    allowed_fields = ['language', 'name', 'phone']  # faqat shu ustunlarga ruxsat
    if field_name not in allowed_fields:
        print("Xato: noto‘g‘ri ustun nomi")
        return False

    try:
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            query = f"UPDATE users SET {field_name} = %s WHERE user_id = %s"
            cur.execute(query, (new_value, tg_id))
            conn.commit()
            cur.close()
            conn.close()
            return True
        return False
    except Exception as e:
        print(f"Error updating {field_name}: {e}")
        return False



def create_table():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS masters (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE,
            name VARCHAR(100),
            phone VARCHAR(20),
            ustaxona_nomi TEXT,
            moljal TEXT,
            address TEXT,
            hours VARCHAR(50),
            min VARCHAR(50),
            language VARCHAR(10),
            service_type VARCHAR(50),
            status BOOLEAN DEFAULT FALSE,
            rating NUMERIC(2,1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Jadval yaratildi yoki mavjud!")
    except Exception as e:
        print(f"Jadval yaratishda xato: {e}")



def insert_master(user_id, name, phone, ustaxona_nomi, moljal, address, hours, min_time, language, service_type, rating=0.0):
    try:
        conn = connect_db()
        cur = conn.cursor()
        query = """
        INSERT INTO masters (user_id, name, phone, ustaxona_nomi, moljal, address, hours, min, language, service_type, rating, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
        ON CONFLICT (user_id) DO UPDATE SET
            name = EXCLUDED.name,
            phone = EXCLUDED.phone,
            ustaxona_nomi = EXCLUDED.ustaxona_nomi,
            moljal = EXCLUDED.moljal,
            address = EXCLUDED.address,
            hours = EXCLUDED.hours,
            min = EXCLUDED.min,
            language = EXCLUDED.language,
            service_type = EXCLUDED.service_type,
            rating = EXCLUDED.rating,
            status = FALSE;
        """
        cur.execute(query, (user_id, name, phone, ustaxona_nomi, moljal, address, hours, min_time, language, service_type, rating))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB insert error: {e}")



def get_master_name_and_rating_by_id(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, rating FROM masters
            WHERE user_id = %s;
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            name, rating = row
            return f"{name} {rating}/10"
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None




def get_masters_names_by_service_type(service_type):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT name FROM masters
            WHERE service_type = %s
            ORDER BY name;
        """, (service_type,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Faqat ismlar ro'yxatini qaytaramiz
        return [row[0] for row in rows] if rows else []

    except Exception as e:
        print(f"Error: {e}")
        return []


def update_master_info(user_id, **kwargs):
    try:
        conn = connect_db()
        cur = conn.cursor()

        fields = []
        values = []

        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)

        if not fields:
            return False

        query = f"UPDATE masters SET {', '.join(fields)} WHERE user_id = %s"
        values.append(user_id)

        cur.execute(query, tuple(values))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False





# ✅ Statusni yangilash
def update_status(user_id, status):
    try:
        conn = connect_db()
        cur = conn.cursor()
        query = "UPDATE masters SET status = %s WHERE user_id = %s"
        cur.execute(query, (status, user_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB update error: {e}")



def get_user_language(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT language FROM masters WHERE user_id = %s", (user_id,))
        lang = cur.fetchone()
        cur.close()
        conn.close()
        if lang:
            return lang[0]
        return None
    except Exception as e:
        print(f"DB select error: {e}")
        return None




def get_user_status_and_language(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT status, language FROM masters WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0], result[1]  # status, language
        return False, None  # ✅ doim ikki qiymat qaytar
    except Exception as e:
        print(f"DB select error: {e}")
        return False, None  # ✅ bu yerda ham



def get_master_data(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, phone, ustaxona_nomi, moljal, address, hours, min, language
            FROM masters WHERE user_id = %s
        """, (user_id,))
        data = cur.fetchone()
        cur.close()
        conn.close()
        if data:
            return {
                "name": data[0],
                "phone": data[1],
                "ustaxona_nomi": data[2],
                "moljal": data[3],
                "address": data[4],
                "hours": data[5],
                "min": data[6],
                "language": data[7],
            }
        return None
    except Exception as e:
        print(f"DB select error (get_master_data): {e}")
        return None



def create_bookings_table():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                master_id BIGINT NOT NULL,  -- Ustaning ID'si
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                booking_date DATE NOT NULL,
                booking_time TIME NOT NULL,
                rating NUMERIC(2,1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ 'bookings' jadvali yaratildi (master_id bilan).")
    except Exception as e:
        print(f"Jadval yaratishda xato: {e}")




def insert_booking(master_id, name, phone, booking_date, booking_time, rating=0):
    try:
        conn = connect_db()
        cur = conn.cursor()
        query = """
            INSERT INTO bookings (master_id, name, phone, booking_date, booking_time, rating)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (master_id, name, phone, booking_date, booking_time, rating))
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Bron ma'lumotlari qo'shildi.")
        return True
    except Exception as e:
        print(f"Ma'lumot qo'shishda xato: {e}")
        return False


def get_master_rating(master_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT AVG(rating) FROM bookings WHERE master_id = %s
        """, (master_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and result[0] is not None:
            return round(result[0], 1)  # O‘rtacha reytingni qaytaradi
        return False  # Agar reyting topilmasa
    except Exception as e:
        print(f"Xato: {e}")
        return False


def get_all_customer_bookings(master_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        query = """
            SELECT name, phone, booking_date, booking_time
            FROM bookings
            WHERE master_id = %s
            ORDER BY booking_date, booking_time
        """
        cur.execute(query, (master_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()

        if results:
            bookings = []
            for row in results:
                bookings.append({
                    "name": row[0],
                    "phone": row[1],
                    "booking_date": str(row[2]),
                    "booking_time": str(row[3])
                })
            return bookings
        return False  # Agar bronlar yo'q bo'lsa
    except Exception as e:
        print(f"Xato: {e}")
        return False



def create_appointments_table():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                user_name VARCHAR(100),
                master_id INT NOT NULL,
                service_name VARCHAR(100),
                date DATE NOT NULL,
                time TIME NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (master_id) REFERENCES masters (id) ON DELETE CASCADE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ 'appointments' jadvali yaratildi yoki mavjud!")
    except Exception as e:
        print(f"❌ Jadval yaratishda xato: {e}")



def get_user_appointments(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.date, a.time, a.service_name, m.name AS master_name
            FROM appointments a
            JOIN masters m ON a.master_id = m.id
            WHERE a.user_id = %s
            ORDER BY a.date, a.time;
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Agar yozuvlar bo'lmasa
        if not rows:
            return False

        # Ma'lumotlarni o'qish
        result = []
        for row in rows:
            result.append({
                "date": row[0].strftime("%d-%m-%Y"),
                "time": row[1].strftime("%H:%M"),
                "service": row[2],
                "master_name": row[3]
            })
        return result

    except Exception as e:
        print(f"❌ Ma'lumotlarni olishda xato: {e}")
        return None








