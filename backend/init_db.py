from flask import Flask
from flask_mysqldb import MySQL
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '6666'
app.config['MYSQL_DB'] = 'blooducate'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

def create_database():
    with app.app_context():
        try:
            # Connect to MySQL server
            conn = mysql.connection
            if not conn:
                logger.error("Database connection failed")
                return
                
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS blooducate")
            cursor.execute("USE blooducate")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    blood_group VARCHAR(10) NOT NULL,
                    last_donation_date DATE,
                    location VARCHAR(255),
                    role ENUM('donor', 'recipient') NOT NULL,
                    mobile VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            mysql.connection.commit()
            logger.info("Database and tables created successfully")
            
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
                logger.info("MySQL connection is closed")

if __name__ == "__main__":
    create_database() 