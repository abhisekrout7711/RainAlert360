from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
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
        print(e)

    finally:
        if server is not None:
            server.quit()
    
    return None


if __name__=="__main__":
    APP_PASSWORD = 'bjqdluwxxskaunqy'
    sender = "abhisekroutwrites@gmail.com"
    password = APP_PASSWORD
    host = "smtp.gmail.com"
    port = 587
    recipients = ['myandroidplaystore@gmail.com', 'abhisekrout7711@gmail.com']
    
    API_KEY = 'c392cc5f74cb43ddb4334337233006'
    city = 'Bhubaneswar'
    work_hours = (7,19)

    weather_data = getWeatherData(city=city, api_key=API_KEY)
    weekly_weather, weekly_alerts = getWeeklyWeatherAndAlerts(weather_data, work_hours, alert_mode=0)
    send_emails(sender, password, host, port, recipients, weekly_alerts)
    