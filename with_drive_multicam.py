from __future__ import print_function
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.discovery import build
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httplib2
import os
import time
import cv2
import auth
import numpy as np
import smtplib

start = time.time()
time_period = 30

sender = 'unpluggedengineers@gmail.com'
receiver = 'machine.learners1@gmail.com'
subject = 'Intruder Alert'

# For study room
msg1 = MIMEMultipart()
msg1['From'] = sender
msg1['To'] = receiver
msg1['Subject'] = subject
body1 = "Someone has entered in your study room. Please open Google Drive to see the image samples"
msg1.attach(MIMEText(body1, 'plain'))
text1 = msg1.as_string()

# For drawing room
msg2 = MIMEMultipart()
msg2['From'] = sender
msg2['To'] = receiver
msg2['Subject'] = subject
body2 = "Someone has entered in your drawing room. Please open Google Drive to see the image samples"
msg2.attach(MIMEText(body2, 'plain'))
text2 = msg2.as_string()

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(sender, 'R72527744')

SCOPES = 'http://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.getCredentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)


def upload_file(filename, filepath, mimetype):
    file_metadata = {'name': filename}
    media = MediaFileUpload(filename, mimetype = 'image/jpeg', resumable = True)
    file = service.files().create(body = file_metadata, media_body = media, fields = 'id').execute()
    print('File ID: %s' % file.get('id'))


static_back1 = None
motion_list1 = [None, None]

static_back2 = None
motion_list2 = [None, None]

cap1 = cv2.VideoCapture("http://rajarshi:R72527744@192.168.0.2:8080/video")
cap2 = cv2.VideoCapture("http://rajarshi:R72527744@192.168.0.3:8080/video")

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    motion = 0
    
    if ret1:
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        blur1 = cv2.GaussianBlur(gray1, (21, 21), 0)

        if static_back1 is None:
            static_back1 = gray1
            continue

        diff_frame1 = cv2.absdiff(static_back1, blur1)
        thresh_frame1 = cv2.threshold(diff_frame1, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame11 = cv2.dilate(thresh_frame1, None, iterations = 2)

        cnts1 = cv2.findContours(thresh_frame11.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        for contour in cnts1:
            if cv2.contourArea(contour) < 10000:
                continue
            motion = 1

            (x,y,w,h) = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 3)

        if motion == 1:
            print("Motion Detected")
            name = 'intruder.jpg'
            print("Creating..." + name)
            cv2.imwrite(name, frame1)
            server.sendmail(sender, receiver, text1)
            upload_file('intruder.jpg', 'intruder.jpg', 'image/jpeg')
        
    if ret2:
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        blur2 = cv2.GaussianBlur(gray2, (21, 21), 0)

        if static_back2 is None:
            static_back2 = gray2
            continue

        diff_frame2 = cv2.absdiff(static_back2, blur2)
        thresh_frame2 = cv2.threshold(diff_frame2, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame21 = cv2.dilate(thresh_frame2, None, iterations = 2)

        cnts2 = cv2.findContours(thresh_frame21.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        for contour in cnts2:
            if cv2.contourArea(contour) < 10000:
                continue
            motion = 2

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame2, (x,y), (x+w, y+h), (0,255,0), 3)

        if motion == 2:
            print("Motion Detected")
            name = 'intruder.jpg'
            print("Creating..." + name)
            cv2.imwrite(name, frame2)
            server.sendmail(sender, receiver, text2)
            upload_file('intruder.jpg', 'intruder.jpg', 'image/jpeg')
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap1.release()
cap2.release()
cv2.destroyAllWindows()
