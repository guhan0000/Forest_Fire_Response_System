from flask import Flask, render_template, flash, request, session, send_file
from flask import render_template, redirect, url_for, request
import warnings
import datetime
import cv2
import time
import cv2
import os
import numpy as np
import threading
import mysql.connector
app = Flask(__name__)
# app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


@app.route("/")
def homepage():
    return render_template('index.html')

@app.route("/Test")
def Test():
    return render_template('Test.html')
@app.route("/AdminLogin")
def AdminLogin():

    return render_template('AdminLogin.html')




@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')

@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
       if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

           conn = mysql.connector.connect(user='root', password='', host='localhost', database='1firetb')
           cur = conn.cursor()
           cur.execute("SELECT * FROM regtb ")
           data = cur.fetchall()
           return render_template('AdminHome.html' , data=data)

       else:
        return render_template('index.html', error=error)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':

        name1 = request.form['name']
        gender1 = request.form['gender']
        Age = request.form['age']
        email = request.form['email']
        pnumber = request.form['phone']
        address = request.form['address']

        uname = request.form['uname']
        password = request.form['psw']


        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1firetb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO regtb VALUES ('" + name1 + "','" + gender1 + "','" + Age + "','" + email + "','" + pnumber + "','" + address + "','" + uname + "','" + password + "')")
        conn.commit()
        conn.close()
        # return 'file register successfully'


    return render_template('UserLogin.html')



@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():

    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1firetb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            alert = 'Username or Password is wrong'
            render_template('goback.html', data=alert)



        else:
            print(data[0])
            session['uid'] = data[0]
            session['mob'] = data[4]
            session['mail'] = data[3]
            
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1firetb')
            # cursor = conn.cursor()
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and Password='" + password + "'")
            data = cur.fetchall()

            return render_template('UserHome.html', data=data )



@app.route("/testimage", methods=['GET', 'POST'])
def testimage():
    if request.method == 'POST':
        if request.form['button']=="start":
            import numpy as np
            args = {"confidence": 0.2, "threshold": 0.3}
            flag = False

            labelsPath = "./yolov/obj.names"
            LABELS = open(labelsPath).read().strip().split("\n")
            final_classes = ['Fire']

            np.random.seed(42)
            COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
                                       dtype="uint8")

            weightsPath = os.path.abspath("./yolov/yolovcustom1_1000.weights")
            configPath = os.path.abspath("./yolov/yolov_custom.cfg")

            # print(configPath, "\n", weightsPath)

            net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
            ln = net.getLayerNames()
            ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

            vs = cv2.VideoCapture(0)
            writer = None
            (W, H) = (None, None)

            flag = True

            flagg = 0

            while True:
                # read the next frame from the file
                (grabbed, frame) = vs.read()

                # if the frame was not grabbed, then we have reached the end
                # of the stream
                if not grabbed:
                    break

                # if the frame dimensions are empty, grab them
                if W is None or H is None:
                    (H, W) = frame.shape[:2]

                blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                             swapRB=True, crop=False)
                net.setInput(blob)
                start = time.time()
                layerOutputs = net.forward(ln)
                end = time.time()

                # initialize our lists of detected bounding boxes, confidences,
                # and class IDs, respectively
                boxes = []
                confidences = []
                classIDs = []

                # loop over each of the layer outputs
                for output in layerOutputs:
                    # loop over each of the detections
                    for detection in output:
                        # extract the class ID and confidence (i.e., probability)
                        # of the current object detection
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]

                        # filter out weak predictions by ensuring the detected
                        # probability is greater than the minimum probability
                        if confidence > args["confidence"]:
                            # scale the bounding box coordinates back relative to
                            # the size of the image, keeping in mind that YOLO
                            # actually returns the center (x, y)-coordinates of
                            # the bounding box followed by the boxes' width and
                            # height
                            box = detection[0:4] * np.array([W, H, W, H])
                            (centerX, centerY, width, height) = box.astype("int")

                            # use the center (x, y)-coordinates to derive the top
                            # and and left corner of the bounding box
                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))

                            # update our list of bounding box coordinates,
                            # confidences, and class IDs
                            boxes.append([x, y, int(width), int(height)])
                            confidences.append(float(confidence))
                            classIDs.append(classID)

                # apply non-maxima suppression to suppress weak, overlapping
                # bounding boxes
                idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
                                        args["threshold"])

                # ensure at least one detection exists
                if len(idxs) > 0:
                    # loop over the indexes we are keeping
                    for i in idxs.flatten():
                        # extract the bounding box coordinates
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])

                        if (LABELS[classIDs[i]] in final_classes):

                            flagg += 1
                            # print(flag)

                            if (flagg == 5):
                                flagg = 0
                                import winsound

                                filename = 'alert.wav'
                                winsound.PlaySound(filename, winsound.SND_FILENAME)

                                cv2.imwrite("alert.jpg", frame)
                                sendmail()

                                sendmsg(session['mob'], " Fire Detected ")

                            color = [int(c) for c in COLORS[classIDs[i]]]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            text = "{}: {:.4f}".format(LABELS[classIDs[i]],
                                                       confidences[i])
                            cv2.putText(frame, text, (x, y - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                else:
                    flag = True

                cv2.imshow("Output", frame)

                if cv2.waitKey(1) == ord('q'):
                    break

            # release the webcam and destroy all active windows
            vs.release()
            cv2.destroyAllWindows()
            return render_template('Test.html')
        else:
            file = request.files['fileupload']
            file.save('static/Out/Test.jpg')

            img = cv2.imread('static/Out/Test.jpg')
            if img is None:
                print('no data')

            img1 = cv2.imread('static/Out/Test.jpg')
            print(img.shape)
            img = cv2.resize(img, ((int)(img.shape[1] / 5), (int)(img.shape[0] / 5)))
            original = img.copy()
            neworiginal = img.copy()
            cv2.imshow('original', img1)
            gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

            img1S = cv2.resize(img1, (960, 540))

            cv2.imshow('Original image', img1S)
            grayS = cv2.resize(gray, (960, 540))
            cv2.imshow('Gray image', grayS)

            gry = 'static/Out/gry.jpg'

            cv2.imwrite(gry, grayS)
            from PIL import ImageOps, Image

            im = Image.open(file)

            im_invert = ImageOps.invert(im)
            inv = 'static/Out/inv.jpg'
            im_invert.save(inv, quality=95)

            dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
            cv2.imshow("Nosie Removal", dst)
            noi = 'static/Out/noi.jpg'

            cv2.imwrite(noi, dst)

            import warnings
            warnings.filterwarnings('ignore')

            import tensorflow as tf
            classifierLoad = tf.keras.models.load_model('firemodel.h5')

            import numpy as np
            from keras.preprocessing import image

            test_image = image.load_img('static/Out/Test.jpg', target_size=(200, 200))
            img1 = cv2.imread('static/Out/Test.jpg')
            test_image = np.expand_dims(test_image, axis=0)
            result = classifierLoad.predict(test_image)

            out = ''
            pre = ''
            if result[0][0] == 1:

                out = "Fire"

                sendmsg(session['mob'],"Fire Detected")
                sendmail1()



            elif result[0][1] == 1:

                out = "Nofire"


            org = 'static/Out/Test.jpg'
            gry = 'static/Out/gry.jpg'
            inv = 'static/Out/inv.jpg'
            noi = 'static/Out/noi.jpg'

            return render_template('Test.html', result=out, org=org, gry=gry, inv=inv, noi=noi)




def sendmsg(targetno, message):
    import requests
    requests.post(
        "http://smsserver9.creativepoint.in/api.php?username=fantasy&password=596692&to=" + targetno + "&from=FSSMSS&message=Dear user  your msg is " + message + " Sent By FSMSG FSSMSS&PEID=1501563800000030506&templateid=1507162882948811640")

def sendmail():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders


    fromaddr = "projectmailm@gmail.com"
    toaddr = session['mail']

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = "Fire  Detection"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "alert.jpg"
    attachment = open("alert.jpg", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "qmgn xecl bkqv musr")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

def sendmail1():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders


    fromaddr = "projectmailm@gmail.com"
    toaddr = session['mail']

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = "Fire  Detection"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = 'static/Out/Test.jpg'
    attachment = open("alert.jpg", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "qmgn xecl bkqv musr")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
