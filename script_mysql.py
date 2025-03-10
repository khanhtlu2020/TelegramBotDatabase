### Importing necessary libraries

import configparser # pip install configparser
from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
import MySQLdb # pip install mysqlclient
import time
import threading
import asyncio

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


import re

@client.on(events.NewMessage(pattern="(?i)/insert"))
async def insert(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id

        # Example command: /insert "Nguyen Van A" "nguyenvana@example.com" "0912345678" "123 Đường ABC" "Hanoi" "100000" "Vietnam" "1990-01-01" "Male" "2023-02-20"
        
        # Use regular expression to extract data between quotes
        pattern = r'"([^"]+)"'
        list_of_words = re.findall(pattern, event.message.text)
        
        if len(list_of_words) != 10:
            text = "Please provide all required fields: FullName, Email, Phone, Address, City, PostalCode, Country, DateOfBirth, Gender, JoinDate."
            await client.send_message(SENDER, text, parse_mode='html')
            return

        full_name = list_of_words[0].strip()
        email = list_of_words[1].strip()
        phone = list_of_words[2].strip()
        address = list_of_words[3].strip()
        city = list_of_words[4].strip()
        postal_code = list_of_words[5].strip()
        country = list_of_words[6].strip()
        date_of_birth = list_of_words[7].strip()
        gender = list_of_words[8].strip()
        join_date = list_of_words[9].strip()

        # Create the tuple "params" with all the parameters inserted by the user
        params = (full_name, email, phone, address, city, postal_code, country, date_of_birth, gender, join_date)
        sql_command = """
            INSERT INTO customer (FullName, Email, Phone, Address, City, PostalCode, Country, DateOfBirth, Gender, JoinDate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """ # Prepare the SQL command

        crsr.execute(sql_command, params) # Execute the query
        conn.commit() # commit the changes

        # If at least 1 row is affected by the query we send specific messages
        if crsr.rowcount < 1:
            text = "Something went wrong, please try again."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = "Customer record correctly inserted."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return





# Function that creates a message containing a list of all the customers
def create_message_select_query(ans):
    text = ""
    for i in ans:
        customer_id = i[0]
        full_name = i[1]
        email = i[2]
        phone = i[3]
        address = i[4]
        city = i[5]
        postal_code = i[6]
        country = i[7]
        date_of_birth = i[8]
        gender = i[9]
        join_date = i[10]
        text += (
            f"<b>{customer_id}</b> | <b>{full_name}</b> | <b>{email}</b> | <b>{phone}</b> | "
            f"<b>{address}</b> | <b>{city}</b> | <b>{postal_code}</b> | <b>{country}</b> | "
            f"<b>{date_of_birth}</b> | <b>{gender}</b> | <b>{join_date}</b>\n"
        )
    message = "<b>Received 📖 </b> Information about customers:\n\n" + text
    return message

### SELECT COMMAND
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        # Execute the query and get all (*) the oders
        crsr.execute("SELECT * FROM customer")
        res = crsr.fetchall() # fetch all the results
        # If there is at least 1 row selected, print a message with the list of all the oders
        # The message is created using the function defined above
        if(res):
            text = create_message_select_query(res) 
            await client.send_message(SENDER, text, parse_mode='html')
        # Otherwhise, print a default text
        else:
            text = "No orders found inside the database."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return



### UPDATE COMMAND
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        # Example command: /update 1 "Nguyen Van B" "nguyenvanb@example.com" "0912345678" "456 Đường ABC" "Hanoi" "100000" "Vietnam" "1980-02-20" "Male" "2023-03-10"
        
        # Use regular expression to extract data between quotes
        pattern = r'"([^"]+)"'
        list_of_words = re.findall(pattern, event.message.text)
        
        if len(list_of_words) != 11:
            text = "Please provide all required fields: ID, FullName, Email, Phone, Address, City, PostalCode, Country, DateOfBirth, Gender, JoinDate."
            await client.send_message(SENDER, text, parse_mode='html')
            return

        id = int(list_of_words[0].strip())
        full_name = list_of_words[1].strip()
        email = list_of_words[2].strip()
        phone = list_of_words[3].strip()
        address = list_of_words[4].strip()
        city = list_of_words[5].strip()
        postal_code = list_of_words[6].strip()
        country = list_of_words[7].strip()
        date_of_birth = list_of_words[8].strip()
        gender = list_of_words[9].strip()
        join_date = list_of_words[10].strip()

        # Create the tuple "params" with all the parameters inserted by the user
        params = (full_name, email, phone, address, city, postal_code, country, date_of_birth, gender, join_date, id)

        # Create the UPDATE query, we are updating the customer with a specific id so we must put the WHERE clause
        sql_command = """
            UPDATE customer SET FullName=%s, Email=%s, Phone=%s, Address=%s, City=%s, PostalCode=%s, Country=%s, DateOfBirth=%s, Gender=%s, JoinDate=%s
            WHERE CustomerID=%s
        """
        crsr.execute(sql_command, params) # Execute the query
        conn.commit() # Commit the changes

        # If at least 1 row is affected by the query we send a specific message
        if crsr.rowcount < 1:
            text = f"Customer with ID {id} is not present."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = f"Customer with ID {id} correctly updated."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e:
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return



### DELETE COMMAND
@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        #/ delete 1

        # Get list of words inserted by the user
        list_of_words = event.message.text.split(" ")
        id = int(list_of_words[1])  # The second (1) element is the CustomerID

        # Create the DELETE query passing the id as a parameter
        sql_command = "DELETE FROM customer WHERE CustomerID = (%s);"

        # ans here will be the number of rows affected by the delete
        ans = crsr.execute(sql_command, (id,))
        conn.commit()

        # If at least 1 row is affected by the query we send a specific message
        if crsr.rowcount < 1:
            text = f"Customer with ID {id} is not present."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = f"Customer with ID {id} was correctly deleted."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e:
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return



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

        await asyncio.sleep(5)

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


