import threading
import asyncio
import MySQLdb
from datetime import datetime

import csv

async def monitor_database():
    previous_data = None

    while True:
        print("Checking database for changes...")
        conn = MySQLdb.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE, charset='utf8mb4')
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

        if changes_detected:
            # Tạo file báo cáo giám sát dưới dạng CSV
            report_filename = f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(report_filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                # Ghi tiêu đề
                writer.writerow(["CustomerID", "FullName", "Email", "Phone", "Address", "City", "PostalCode", "Country", "DateOfBirth", "Gender", "JoinDate"])

                # Ghi dữ liệu
                for row in current_data:
                    row = list(row)

                    # Chuyển đổi ngày tháng về định dạng chuẩn nếu cần
                    for i in [8, 10]:  # Giả sử DateOfBirth & JoinDate ở cột 9 & 11 (index bắt đầu từ 0)
                        if isinstance(row[i], str) and "/" in row[i]:  
                            try:
                                row[i] = datetime.strptime(row[i], "%m/%d/%Y").strftime("%Y-%m-%d")
                            except ValueError:
                                pass  # Nếu không chuyển được, giữ nguyên

                    writer.writerow(row)

            try:
                await client.send_file(6507260169, report_filename, caption="📊 Báo cáo giám sát mới:")
                print("Report sent successfully.")
            except Exception as e:
                print(f"Error sending report: {e}")

        previous_data = current_data
        crsr.close()
        conn.close()

        await asyncio.sleep(5)