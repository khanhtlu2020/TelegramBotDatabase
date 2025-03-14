import configparser  # pip install configparser
from telethon import TelegramClient, events  # pip install telethon
from datetime import datetime, timedelta
import MySQLdb  # pip install mysqlclient
import pyodbc  # pip install pyodbc
import time
import threading
import asyncio
import csv
import re

### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

# Read values for Telethon and set session name
API_ID = config.get('default', 'api_id')
API_HASH = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'bot_token')
session_name = "sessions/Bot"

# Read values for MySQLdb
hostname = config.get('default', 'hostname')
port = config.get('default', 'port')
username = config.get('default', 'username')
password = config.get('default', 'password')
database = config.get('default', 'database')

# Start the Client (telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)


### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id
    
    # set text and send message
    text = "Hello i am a bot that can do CRUD operations and data report inside a SQL Server database"
    await client.send_message(SENDER, text)
    
    
### INSERT COMMAND
@client.on(events.NewMessage(pattern="(?i)/insert"))
async def insert(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        
        # Use regular expression to extract data between quotes
        pattern = r'"([^"]+)"'
        list_of_words = re.findall(pattern, event.message.text)
        
        if len(list_of_words) != 6:
            text = "Please provide all required fields: ItemCode, ItemName, Description, Price, SendingTime, SectionCode."
            await client.send_message(SENDER, text, parse_mode='html')
            return

        item_code = list_of_words[0].strip()
        item_name = list_of_words[1].strip()
        description = list_of_words[2].strip()
        price = list_of_words[3].strip()
        sending_time = list_of_words[4].strip()
        section_code = list_of_words[5].strip()

        # Create the tuple "params" with all the parameters inserted by the user
        params = (item_code, item_name, description, price, sending_time, section_code)
        sql_command = """
            INSERT INTO item (ItemCode, ItemName, Description, Price, SendingTime, SectionCode)
            VALUES (%s, %s, %s, %s, %s, %s);
        """ # Prepare the SQL command

        crsr.execute(sql_command, params) # Execute the query
        conn.commit() # Commit the changes

        # If at least 1 row is affected by the query we send specific messages
        if crsr.rowcount < 1:
            text = "Something went wrong, please try again."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = "Item record correctly inserted."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something wrong happened... Check your code!", parse_mode='html')
        return

# Function that creates a message containing a list of all the items
def create_message_select_query(ans):
    text = ""
    for i in ans:
        item_code = i[0]
        item_name = i[1]
        description = i[2]
        price = i[3]
        sending_time = i[4]
        section_code = i[5]
        text += (
            f"ItemCode: {item_code}\nItemName: {item_name}\nDescription: {description}\n"
            f"Price: {price}\nSendingTime: {sending_time}\nSectionCode: {section_code}\n\n"
        )
    message = f"<b>Received 📖</b> Information about items:\n\n<b>{text}</b>"
    return message



### SELECT COMMAND
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        # Execute the query and get all (*) the items
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={hostname};DATABASE={database};UID={username};PWD={password}')
        crsr = conn.cursor()
        crsr.execute("SELECT * FROM item")
        res = crsr.fetchall()  # fetch all the results
        # If there is at least 1 row selected, print a message with the list of all the items
        # The message is created using the function defined above
        if res:
            text = create_message_select_query(res)
            await client.send_message(SENDER, text, parse_mode='html')
        # Otherwise, print a default text
        else:
            text = "No items found inside the database."
            await client.send_message(SENDER, text, parse_mode='html')
        conn.close()
    except Exception as e:
        print(e)
        await client.send_message(SENDER, "Something wrong happened... Check your code!", parse_mode='html')
        return


### UPDATE COMMAND
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        # Use regular expression to extract data between quotes
        pattern = r'"([^"]+)"'
        list_of_words = re.findall(pattern, event.message.text)
        
        if len(list_of_words) != 6:
            text = "Please provide all required fields: ID, ItemCode, ItemName, Description, Price, SendingTime, SectionCode."
            await client.send_message(SENDER, text, parse_mode='html')
            return

        # Assign values to variables
        id = int(list_of_words[0].strip())
        item_code = list_of_words[1].strip()
        item_name = list_of_words[2].strip()
        description = list_of_words[3].strip()
        price = list_of_words[4].strip()
        sending_time = list_of_words[5].strip()
        section_code = list_of_words[6].strip()

        # Create the tuple "params" with all the parameters inserted by the user
        params = (item_code, item_name, description, price, sending_time, section_code, id)

        # Create the UPDATE query, updating the item with a specific id
        sql_command = """
            UPDATE item SET ItemCode=%s, ItemName=%s, Description=%s, Price=%s, SendingTime=%s, SectionCode=%s
            WHERE ItemID=%s
        """
        crsr.execute(sql_command, params) # Execute the query
        conn.commit() # Commit the changes

        # If at least 1 row is affected by the query we send a specific message
        if crsr.rowcount < 1:
            text = f"Item with ID {id} is not present."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = f"Item with ID {id} correctly updated."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e:
        print(e)
        await client.send_message(SENDER, "Something wrong happened... Check your code!", parse_mode='html')
        return


### DELETE COMMAND
@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        # Example command: /delete 1

        # Get list of words inserted by the user
        list_of_words = event.message.text.split(" ")
        id = int(list_of_words[1])  # The second (1) element is the ItemID

        # Create the DELETE query passing the id as a parameter
        sql_command = "DELETE FROM item WHERE ItemID = (%s);"

        # ans here will be the number of rows affected by the delete
        ans = crsr.execute(sql_command, (id,))
        conn.commit()

        # If at least 1 row is affected by the query we send a specific message
        if crsr.rowcount < 1:
            text = f"Item with ID {id} is not present."
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = f"Item with ID {id} was correctly deleted."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e:
        print(e)
        await client.send_message(SENDER, "Something wrong happened... Check your code!", parse_mode='html')
        return


# Create database function
def create_database(query):
    try:
        crsr_mysql.execute(query)
        print("Database created successfully")
    except Exception as e:
        print(f"WARNING: '{e}'")


### MAIN
async def monitor_database():
    previous_data = None  

    while True:
        try:
            print("Checking database for changes...")
            conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={hostname};DATABASE={database};UID={username};PWD={password}'
            )
            cursor = conn.cursor()

            query1 = f"SELECT * FROM item WITH (NOLOCK) WHERE SectionCode='CAS'"
            cursor.execute(query1)
            current_data = cursor.fetchall()

            if previous_data is None:
                previous_data = current_data
            elif sorted(current_data) != sorted(previous_data):
                changes_message = "Data report:\n"
                for row in current_data:
                    if row not in previous_data:
                        changes_message += f"New data detected: {row}\n"
                for row in previous_data:
                    if row not in current_data:
                        changes_message += f"Data removed: {row}\n"

                # CSV
                report_filename = f"item_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(report_filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ItemCode", "ItemName", "Description", "Price", "SendingTime", "SectionCode"])
                    writer.writerows(current_data)

                print(changes_message)
                try:
                    await client.send_message(6507260169, changes_message)
                    await client.send_file(6507260169, report_filename, caption="Attached monitoring report")
                    print("Message and report sent successfully.")
                except Exception as e:
                    print(f"Error sending message or file: {e}")

                previous_data = current_data

            cursor.close()
            conn.close()
            await asyncio.sleep(120)

        except Exception as e:
            print(f"Error in monitoring: {e}")


async def main():
    await client.start()
    monitor_task = asyncio.create_task(monitor_database())
    await monitor_task

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())

    except Exception as error:
        print('Cause: {}'.format(error))




