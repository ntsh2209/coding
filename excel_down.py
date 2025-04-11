import os
import requests
import smtplib
import filecmp
from email.message import EmailMessage

# === Configuration ===
URL = "https://example.com/path/to/file.xlsx"
SAVE_DIR = "/path/to/save/location"
FILENAME = "downloaded_file.xlsx"
TEMP_FILE = os.path.join("/tmp", "temp_file.xlsx")
FINAL_FILE = os.path.join(SAVE_DIR, FILENAME)

EMAIL_FROM = "your_email@example.com"
EMAIL_TO = "recipient@example.com"
EMAIL_SUBJECT = "Excel File Updated"
EMAIL_BODY = f"The Excel file from {URL} has changed and has been updated at {FINAL_FILE}."
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_password"

# === Step 1: Download the Excel file ===
print("Downloading the Excel file...")
response = requests.get(URL)
with open(TEMP_FILE, "wb") as f:
    f.write(response.content)

# === Step 2: Compare with existing file ===
def files_are_different(file1, file2):
    return not os.path.exists(file2) or not filecmp.cmp(file1, file2, shallow=False)

# === Step 3: Send email if file changed ===
if files_are_different(TEMP_FILE, FINAL_FILE):
    print("File has changed. Saving new file and sending email.")

    # Move new file to destination
    os.replace(TEMP_FILE, FINAL_FILE)

    # Prepare email
    msg = EmailMessage()
    msg.set_content(EMAIL_BODY)
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
else:
    print("No changes detected.")
    os.remove(TEMP_FILE)
