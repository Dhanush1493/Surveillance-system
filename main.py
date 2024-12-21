import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import argparse
import os
from pytube import YouTube
import subprocess

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

def play_youtube_video(video_url):
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').first()
        if video_stream:
            # Download the video
            video_stream.download(output_path=".", filename="temp_video.mp4")
            # Play the video using default media player
            # You can change "xdg-open" to "open" if you're on macOS
            # subprocess.call(["open", "temp_video.mp4"]) 
            subprocess.call(["start", "temp_video.mp4"], shell=True)
            # Cleanup: Remove the downloaded video
        else:
            print("No mp4 format available for the video.")
    except Exception as e:
        print("An error occurred:", str(e))

def send_email(sender_email, sender_password, recipient_email, subject, body, image_file):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the text body
    message.attach(MIMEText(body, 'plain'))

    # Attach the image file
    with open(image_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {image_file}')
    message.attach(part)

    # Connect to SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
    finally:
        server.quit()


video = cv2.VideoCapture(0)
video_played = False  # Flag to track if the video has been played

while True:
    check, frame = video.read()
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)
        for x, y, w, h in faces:
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            exact_time = datetime.now().strftime('%Y-%b-%d-%H-%M-%S-%f')
            image_path = "face_detected_" + str(exact_time) + ".jpg"
            cv2.imwrite(image_path, img)
            # Send email with the attached image
            sender_email = 'dhanushnatarayadurai@gmail.com'
            sender_password = 'lihptqsppdgpndia'
            recipient_email = 'dhanushnatarayadurai@gmail.com'
            subject = 'Face Detected'
            body = 'A face has been detected. Please find the attached image.'
            send_email(sender_email, sender_password, recipient_email, subject, body, image_path)
            # Play video only once when face is detected
            if not video_played:
                video_url = "https://www.youtube.com/watch?v=5nRgCabardA"  # Example YouTube video URL
                play_youtube_video(video_url)
                video_played = True
	
        cv2.imshow("home surv", frame)
        key = cv2.waitKey(1)

        if key == ord('q'):
            ap = argparse.ArgumentParser()
            ap.add_argument("-ext", "--extension", required=False, default='jpg')
            ap.add_argument("-o", "--output", required=False, default='output.mp4')
            args = vars(ap.parse_args())

            dir_path = '.'
            ext = args['extension']
            output = args['output']

            images = []

            for f in os.listdir(dir_path):
                if f.endswith(ext):
                    images.append(f)

            image_path = os.path.join(dir_path, images[0])
            frame = cv2.imread(image_path)
            height, width, channels = frame.shape

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output, fourcc, 5.0, (width, height))

            for image in images:
                image_path = os.path.join(dir_path, image)
                frame = cv2.imread(image_path)
                out.write(frame)

            break

video.release()
cv2.destroyAllWindows()
