### Importing necessary libraries

import configparser # pip install configparser
from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
import MySQLdb # pip install mysqlclient
import time

### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

# Read values for Telethon and set session name
API_ID = config.get('default','api_id') 
API_HASH = config.get('default','api_hash')
BOT_TOKEN = config.get('default','bot_token')
session_name = "sessions/Bot"

# Read values for MySQLdb
HOSTNAME = config.get('default','hostname')
USERNAME = config.get('default','username')
PASSWORD = config.get('default','password')
DATABASE = config.get('default','database')
 
# Start the Client (telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)


### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id
    
    # set text and send message
    text = "Hello i am a bot that can do CRUD operations inside a MySQL database"
    await client.send_message(SENDER, text)


### INSERT COMMAND
# code insert





# Function that creates a message containing a list of all the customers
#code

### SELECT COMMAND
#code select



### UPDATE COMMAND
#code update



### DELETE COMMAND
#code delete



# Create database function
def create_database(query):
    try:
        crsr_mysql.execute(query)
        print("Database created successfully")
    except Exception as e:
        print(f"WARNING: '{e}'")

##### MAIN
import threading
import asyncio

async def monitor_database():
    previous_data = None

    while True:
        print("Checking database for changes...")
        conn = MySQLdb.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE)
        crsr = conn.cursor()
        crsr.execute("SELECT * FROM customer")  # Chỉ giám sát bảng customer
        current_data = crsr.fetchall()

        if previous_data is None:
            previous_data = current_data

        changes_detected = False
        changes_message = ""

        if current_data != previous_data:
            for new_row in current_data:
                if new_row not in previous_data:
                    changes_detected = True
                    changes_message += f"New data detected: {new_row}\n"
                    
            for old_row in previous_data:
                if old_row not in current_data:
                    changes_detected = True
                    changes_message += f"Data removed: {old_row}\n"
        
        message = "No data change in the customer table." if not changes_detected else changes_message

        try:
            await client.send_message(6507260169, message)  # Thay thế bằng chat ID thực tế
            print("Message sent successfully.")
        except Exception as e:
            print(f"Error sending message: {e}")

        previous_data = current_data
        crsr.close()
        conn.close()

        await asyncio.sleep(60)

async def main():
    await client.start()
    monitor_task = asyncio.create_task(monitor_database())
    await monitor_task

if __name__ == '__main__':
    try:
        print("Initializing Database...")
        conn_mysql = MySQLdb.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD)
        crsr_mysql = conn_mysql.cursor()

        query = "CREATE DATABASE " + str(DATABASE)
        create_database(query)
        conn = MySQLdb.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE)
        crsr = conn.cursor()

        # Command that creates the "customer" table 
        sql_command = """CREATE TABLE IF NOT EXISTS customer ( 
            CustomerID INTEGER PRIMARY KEY AUTO_INCREMENT, 
            FullName VARCHAR(255) NOT NULL,
            Email VARCHAR(255) NOT NULL,
            Phone VARCHAR(20),
            Address TEXT,
            City VARCHAR(100),
            PostalCode VARCHAR(20),
            Country VARCHAR(100),
            DateOfBirth DATE,
            Gender ENUM('Male', 'Female', 'Other'),
            JoinDate DATE NOT NULL);"""

        crsr.execute(sql_command)
        print("All tables are ready")

        print("Bot Started...")
        
        # Chạy hàm main trong event loop của Telethon client
        client.loop.run_until_complete(main())

    except Exception as error:
        print('Cause: {}'.format(error))
