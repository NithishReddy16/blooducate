from db_config import get_db_connection

def create_user(name, email, password, blood_group, last_donation_date, location, role, gender, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO users (name, gender, email, password, blood_group, last_donation_date, location, role, mobile)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (name, gender, email, password, blood_group, last_donation_date, location, role, phone))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def find_donors(blood_group, location, min_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if min_date:
            cursor.execute("""
                SELECT * FROM donors 
                WHERE blood_group = %s 
                AND location = %s 
                AND (last_donation_date IS NULL OR last_donation_date < %s)
            """, (blood_group, location, min_date))
        else:
            cursor.execute("""
                SELECT * FROM donors 
                WHERE blood_group = %s 
                AND location = %s
            """, (blood_group, location))
        
        donors = cursor.fetchall()
        return donors
    except Exception as e:
        print(f"Error in find_donors: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()
