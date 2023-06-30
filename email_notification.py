from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import sys
from weather import getWeatherData, getWeeklyWeatherAndAlerts


def send_emails(sender:str, password:str, host:str, port:str, recipients:list[str], 
                weekly_alerts:list[dict], subject_line:str="Rainfall Alert!") -> None:
    '''Sends Rainfall Alert! emails for the upcoming week to the recipients'''
    server = None
    try:
        server = smtplib.SMTP(host=host, port=port)
        server.starttls()

        server.login(sender, password)

        weather_table ='''
        <head>
        <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }

        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }

        tr:nth-child(even) {
        background-color: #dddddd;
        }
        </style>
        </head>
        <table>
            <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Time (hrs)</th>
                <th>Inference</th>
                <th>Precipitation (mm)</th>
                <th>Chances (%)</th>
            </tr>
        '''
        
        location = weekly_alerts[0]['location']
        next_monday = datetime.today().date() + timedelta(days=3)
        for daily_alert in weekly_alerts:
            # Get weekly_alert only for upcoming week i.e., upcoming Monday to Friday
            if datetime.strptime(daily_alert['day'], "%Y-%m-%d").date() < next_monday:
                continue

            weather_table_row = f'''
            <tr>
                <td>{daily_alert['day']}</td>
                <td>{datetime.strptime(daily_alert['day'], "%Y-%m-%d").strftime('%A')}</td>
                <td>{daily_alert['time']}</td>
                <td>{daily_alert['condition']}</td>
                <td>{daily_alert['precip_mm']}</td>
                <td>{daily_alert['chance_of_rain']}</td>
            </tr>
            '''
            weather_table += weather_table_row
        weather_table += '</table>'
        
        message = MIMEMultipart("alternative")
        message['From'] = sender
        recipients = ", ".join(recipients) # Convert recipients list to comma separated values
        message['To'] = recipients
        message["Subject"] = subject_line
        organization_name = 'Rout Brothers Pvt Ltd'

        # Message body
        email_body = f'''
        <html>
        <body>
                <p>Hello there,<br>
                This is to warn you that there are chances of rainfall at {location} on the following days of the upcoming week:<br>
                <br>{weather_table}<br>
                Please plan your days accordingly. You may consider working from home (WFH) for the above mentioned dates post confirmation with your respective managers.<br>
                <br><b>Important:</b> <i>This is a system generated e-mail, kindly do not reply to this e-mail.</i><br><br>
                Thank You<br><br>
                Regards<br>
                Team HR,<br>
                {organization_name}.<br>
                </p>
        </body>
        </html>
        '''
        body = MIMEText(email_body, 'html')
        message.attach(body)

        server.send_message(message)
        
        print("Mail Sent")

    except Exception as e:
        print('Error occured while sending email:', e)

    finally:
        if server is not None:
            server.quit()
    
    return None


if __name__=="__main__":
    
    sender: str = os.environ.get('EMAIL')
    password: str = os.environ.get('EMAIL_PASSWORD')
    
    host: str = "smtp.gmail.com"
    port: str = 587

    # Ideally the recipents list is supposed to be fetched from some db
    recipients: list[str] = ['sample_email_1@sample.com', 'sample_email_2@sample.com']
    
    city: str = input('Enter the name of the city:').strip()
    work_hours_str: str = input('Enter work hrs in 24hr format separated by , as start,end:')
    try:
        work_hours: tuple = tuple(int(i) for i in work_hours_str.strip().split(','))
    except Exception as e:
        print('Invalid Input for work hours:', e)

    API_KEY = os.environ.get('API_KEY')
    
    weather_data: dict = getWeatherData(city=city, api_key=API_KEY)
    if 'error' in weather_data:
        print('No matching location found.')
        sys.exit(1)
    
    _, weekly_alerts = getWeeklyWeatherAndAlerts(weather_data, work_hours, alert_mode=1)
    if not weekly_alerts:
        print('No Rainfall Alerts! for the upcoming week for the provided work hours.')
        sys.exit(0)
    
    send_emails(sender, password, host, port, recipients, weekly_alerts)
