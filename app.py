from flask import Flask, render_template, make_response,request,redirect,url_for
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import base64
from weasyprint import HTML, CSS

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
num = 1
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
    msg['Subject'] = '[한국 이주 노동 재단] 자동이체후원신청서'

    body = '[한국 이주 노동 재단] 자동이체후원신청서'
    msg.attach(MIMEText(body, 'plain'))

    pdf_path = pdf_filename

    try:
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {pdf_filename}")
            msg.attach(part)
            print(f"Attach")

    except FileNotFoundError:
        print(f"AAAAAAAAAAAAAAAAAAAFile '{pdf_filename}' not found in the specified folder.")
        return

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"sent")


@app.route('/', methods=['GET',"POST"])
def index():
    # Render the HTML content with the appropriate variables
    if request.method == "POST":
        name = request.form.get("name")
        phone1 = request.form.get("phone_num1")
        phone2 = request.form.get("phone_num2")
        phone3 = request.form.get("phone_num3")
        phone = str(phone1) + "-" + str(phone2) + "-" + str(phone3)
        # email = request.form.get("member_email")
        birth = request.form.get("birth")

        # try:
        #     birth = str(birth[]2:])+str(birth_month)+str(birth_day)
        # except TypeError:
        #     birth = "20210101"

        payment_type = request.form.get('payment_type')
        # payment_yyyymmdd1 = request.form.get('Payment_yyyymmdd1')
        # payment_yyyymmdd2 = request.form.get('Payment_yyyymmdd2')
        agreement1 = request.form.get('agreement1')
        agreement2 = request.form.get('agreement2')
        account_owner = request.form.get('account_owner')
        account_num = request.form.get('account_num')
        custom_won = request.form.get('custom_won')
        canvas_image_data = request.form.get('canvas_image_data')
        # address = request.form.get('address')
        current_date = datetime.now()
        current_year = str(current_date.year)
        current_month = str(current_date.month).zfill(2)
        current_day = str(current_date.day).zfill(2)

        selected_bank = request.form.get('bank_name')
        formatted_date = current_year + current_month + current_day
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day
        image_path = 'static/saved_image.png'
        payment_date = request.form.get('payment_date')
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            image_data = base64.b64encode(img_data).decode('utf-8')
        rendered_html = render_template('auto_debit_pay_form.html',
                                        name=name,
                                        phone=phone,
                                        payment_date= payment_date,
                                        image_data = image_data,
                                        bank_name = selected_bank,
                                        formatted_date = formatted_date,
                                        current_year = current_year,
                                        current_month =  current_month,
                                        current_day = current_day,
                                        birth=birth,
                                        payment_type=payment_type,
                                        # payment_yyyymmdd1=payment_yyyymmdd1,
                                        # payment_yyyymmdd2=payment_yyyymmdd2,
                                        agreement1=agreement1,
                                        agreement2=agreement2,
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
        # pdf_data = pdfkit.from_string(rendered_html, False, options=pdf_options)
        # Save PDF to a file
        global num
        pdf_filename = 'auto_debit_form_'+str(num)+"_"+birth+'.pdf'
        num += 1
        # HTML(string=rendered_html).write_pdf(pdf_filename)
        custom_css = """
            table {
                border-collapse: collapse; /* Ensure single borders for table cells */
                width: 100%;
            }
            th, td {
                border: 1px solid black; /* Add borders to table cells */
                padding: 8px;
            }
            @page {
                margin: 4mm; /* Set margin for the entire page */
            }
            body {
                font-size: 10px;
            }
            .doc_title{
                font-size: 20px;
                text-align: center;
            }
            .doc_center{
                text-align: center;
            }
        """
        HTML(string=rendered_html).write_pdf(pdf_filename, stylesheets=[CSS(string=custom_css)])
        # pdf_path = f"./{pdf_filename}"
        # with open(pdf_path, 'wb') as f:
        #     f.write(pdf_data)
        # send_email(pdf_filename, "nhv4825@gmail.com")
        # send_email(pdf_filename, "scott2008@naver.com")

        store = file.Storage('storage.json')
        creds = store.get
        upload_to_drive(pdf_filename)
        # Redirect user to the success page after saving PDF
        return redirect(url_for('success', filename=pdf_filename))
    else:
        return render_template("index.html")
@app.route('/success', methods=['GET',"POST"])
def success():
    return render_template("success.html")
if __name__ == '__main__':
    app.run(debug=True)
