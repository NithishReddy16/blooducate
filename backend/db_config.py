import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='6666',
        database='blooducate',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
