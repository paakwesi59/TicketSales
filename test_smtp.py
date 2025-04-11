import smtplib

server = "smtp.gmail.com"
port = 587
username = "asmahpaakwesi59@gmail.com"
password = "mpnw meyk nebj linf"  # Your current App Password

try:
    smtp = smtplib.SMTP(server, port)
    print("Connected to SMTP server")
    smtp.starttls()
    print("Started TLS")
    smtp.login(username, password)
    print("Logged in successfully!")
    smtp.quit()
except Exception as e:
    print(f"Error: {e}")