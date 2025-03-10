### Importing necessary libraries
import configparser  # pip install configparser
from telethon import TelegramClient, events  # pip install telethon
from datetime import datetime
import pyodbc  # pip install pyodbc
import asyncio
import csv

### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

# Read values for Telethon and set session name
API_ID = config.get('default', 'api_id') 
API_HASH = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'bot_token')
session_name = "sessions/Bot"

# Read values for SQL Server from config.ini
HOSTNAME = config.get('default', 'hostname')
PORT = config.get('default', 'port')
USERNAME = config.get('default', 'username')
PASSWORD = config.get('default', 'password')
DATABASE = config.get('default', 'database')

# Connection string for SQL Server
CONNECTION_STRING = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={HOSTNAME},{PORT};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"

# Start the Client (Telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id

    # set text and send message
    text = "Hello! I am a bot that can do CRUD operations inside a SQL Server database."
    await client.send_message(SENDER, text)

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
    return f"<b>Received 📖 </b> Information about items:\n\n<b>{text}</b>"

### SELECT COMMAND
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id

        # Connect to SQL Server
        conn = pyodbc.connect(CONNECTION_STRING)
        crsr = conn.cursor()

        # Execute the query and get all (*) the items
        crsr.execute("SELECT * FROM item")
        res = crsr.fetchall()

        if res:
            text = create_message_select_query(res)
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = "No items found inside the database."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something went wrong... Check your code!", parse_mode='html')

##### MAIN FUNCTION
async def monitor_database():
    previous_data = None

    while True:
        print("Checking database for changes...")
        conn = pyodbc.connect(CONNECTION_STRING)
        crsr = conn.cursor()
        crsr.execute("SELECT * FROM item")  # Monitor table item
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
                    changes_message += f"Old data removed: {old_row}\n"

        if changes_detected:
            # Send monitoring report
            try:
                await client.send_message(6507260169, changes_message)  # Replace with actual chat ID
                print("Message sent successfully.")
            except Exception as e:
                print(f"Error sending message: {e}")

            # Create CSV report
            report_filename = f"item_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(report_filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                # Write headers
                writer.writerow(["ItemCode", "ItemName", "Description", "Price", "SendingTime", "SectionCode"])

                # Write rows
                for row in current_data:
                    writer.writerow(row)

            try:
                await client.send_file(6507260169, report_filename, caption="New item monitoring report")
                print("Report sent successfully.")
            except Exception as e:
                print(f"Error sending report: {e}")

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
        
        # Test connection
        conn = pyodbc.connect(CONNECTION_STRING)
        crsr = conn.cursor()
        print("Database connected successfully.")

        # Start bot
        print("Bot Started...")
        asyncio.run(main())

    except Exception as error:
        print(f'Error: {error}')
