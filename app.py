from flask import Flask, render_template, make_response,request,redirect,url_for
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import base64
from PIL import Image
from io import BytesIO
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from httplib2 import Http
from oauth2client import file
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
gauth = GoogleAuth()
# gauth.LocalWebserverAuth()  # Initiates the web-based Google Drive authentication flow
drive = GoogleDrive(gauth)
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDS_FILE = 'token.json'
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Function to upload a file to Google Drive
def upload_to_drive(pdf_path):
    creds = authenticate()
    DRIVE = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': os.path.basename(pdf_path),
        'parents': ["1V7cQ4hX8YrzEyL5xITNE9pdIl-MmA1rY"]
    }
    media = MediaFileUpload(pdf_path, mimetype='application/pdf')
    file = DRIVE.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return file

@app.route('/save_image', methods=['POST'])
def save_image():
    image_data_url = request.form['imageBase64']
    print("AAAAAA"+image_data_url)
    image_data = image_data_url.split(',')[1]

    image = Image.open(BytesIO(base64.b64decode(image_data)))


    image_path = 'static/saved_image.png'
    image.save(image_path)


    return f'Image saved successfully at {image_path}'
def send_email(pdf_filename, recipient_email):
    sender_email = 'madckkim@gmail.com'  # Replace with your email address
    sender_password = 'akim sbbg ixpt somm'  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = '[한국 이주 노동 재단] 자동이체후원신청서'  # Replace with your email subject

    body = '[한국 이주 노동 재단] 자동이체후원신청서'
    msg.attach(MIMEText(body, 'plain'))

    filename = pdf_filename
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

@app.route('/', methods=['GET',"POST"])
def index():
    # Render the HTML content with the appropriate variables
    if request.method == "POST":
        name = request.form.get("name")
        phone1 = request.form.get("phone_num1")
        phone2 = request.form.get("phone_num2")
        phone3 = request.form.get("phone_num3")
        phone = str(phone1) + "-" + str(phone2) + "-" + str(phone3)
        email = request.form.get("member_email")
        birth_year = request.form.get("birth_year")
        birth_month = request.form.get("birth_month")
        birth_day = request.form.get("birth_day")
        try:
            birth = str(birth_year[2:])+str(birth_month)+str(birth_day)
        except TypeError:
            birth = "20210101"

        payment_type = request.form.get('payment_type')
        payment_date = request.form.get('payment_date')
        payment_yyyymmdd1 = request.form.get('Payment_yyyymmdd1')
        payment_yyyymmdd2 = request.form.get('Payment_yyyymmdd2')
        agreement1 = request.form.get('agreement1')
        agreement2 = request.form.get('agreement2')
        account_owner = request.form.get('account_owner')
        account_num = request.form.get('account_num')
        custom_won = request.form.get('custom_won')
        canvas_image_data = request.form.get('canvas_image_data')
        address = request.form.get('address')
        current_date = datetime.now()
        current_year = str(current_date.year)[-2:]
        current_month = str(current_date.month).zfill(2)
        current_day = str(current_date.day).zfill(2)

        selected_bank = request.form.get('bank_name')
        formatted_date = current_year + current_month + current_day
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day
        image_path = 'static/saved_image.png'

        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            image_data = base64.b64encode(img_data).decode('utf-8')
        rendered_html = render_template('auto_debit_pay_form.html',
                                        name=name,
                                        phone=phone,
                                        email=email,
                                        image_data = image_data,
                                        bank_name = selected_bank,
                                        formatted_date = formatted_date,
                                        current_year = current_year,
                                        current_month =  current_month,
                                        current_day = current_day,
                                        birth_year=birth_year,
                                        birth_day=birth_day,
                                        birth_month=birth_month,
                                        birth=birth,
                                        payment_type=payment_type,
                                        payment_date=payment_date,
                                        payment_yyyymmdd1=payment_yyyymmdd1,
                                        payment_yyyymmdd2=payment_yyyymmdd2,
                                        agreement1=agreement1,
                                        agreement2=agreement2,
                                        address = address,
                                        account_owner=account_owner,
                                        account_num=account_num,
                                        custom_won=custom_won,
                                        canvas_image_data=canvas_image_data)

        pdf_options = {
            'quiet': '',
            'page-size': 'A4',
            'margin-top': '0.5cm',
            'margin-bottom': '0cm',
            'margin-left': '0.5cm',
            'margin-right': '0.5cm'
            # Add any other options you may need here
        }

        # Convert HTML to PDF
        pdf_data = pdfkit.from_string(rendered_html, False, options=pdf_options)

        # Save PDF to a file
        pdf_filename = 'auto_debit_form_'+name+"_"+birth+'.pdf'
        pdf_path = f"./{pdf_filename}"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        send_email(pdf_filename, email)
        store = file.Storage('storage.json')
        creds = store.get
        upload_to_drive(pdf_path)
        # Redirect user to the success page after saving PDF
        return redirect(url_for('success', filename=pdf_filename))
    else:
        return render_template("index.html")
@app.route('/success', methods=['GET',"POST"])
def success():
    return render_template("success.html")
if __name__ == '__main__':
    app.run(debug=True)
