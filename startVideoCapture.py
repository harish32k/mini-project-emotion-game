import os
import cv2
import numpy as np
import tensorflow as tf
from keras.preprocessing import image
print(1)
model = tf.keras.models.load_model('my_model_final.h5')
print(2)

face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print(3)
cap=cv2.VideoCapture(0)

mapping = {'angry': 0, 'fear': 1, 'happy': 2, 'sad': 3, 'surprise': 4, 'neutral': 5}
record = {'angry': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
prev = 'neutral'
precnt = 0



import sqlite3
from sqlite3 import Error
database='gamedb.db'
try:
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    #('angry', 'fear', 'happy', 'sad', 'surprise', 'neutral')

    query = """ CREATE TABLE IF NOT EXISTS emotions (
                                        angry integer,
                                        fear integer,
                                        happy integer,
                                        sad integer,
                                        surprise integer,
                                        neutral integer
                                    ); """
    cursor.execute(query)
    query = """ INSERT INTO emotions (angry, fear, happy, sad, surprise, neutral)
   			SELECT 0, 0, 0, 0, 0, 0
    		WHERE NOT EXISTS (SELECT * FROM emotions);"""
    cursor.execute(query)
    connection.commit()
except Error as e:
    print(e)


cursor = connection.cursor()
cursor.execute(f"""UPDATE emotions 
    set angry=?, fear=?, happy=?, sad=?, surprise=?, neutral=?;""", (0, 0, 0, 0, 0, 0))


print((0, 0, 0, 0, 0, 0))
connection.commit()
cursor.close()

def start_game():
	os.system('python begin_game.py')
import threading
try:
   t = threading.Thread(target = start_game)
   t.start()
except:
   print ("Error: unable to start thread")


import time
p = time.time()
all_count = 0

edata = [0, 0, 0, 0, 0, 0]
save_counter = 40
while True:
    all_count += 1
    ret,test_img=cap.read()# captures frame and returns boolean value and captured image
    if not ret:
        continue
    gray_img= cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

    faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)


    for (x,y,w,h) in faces_detected:
        cv2.rectangle(test_img,(x,y),(x+w,y+h),(255,0,0),thickness=4)
        roi_gray=gray_img[y:y+w,x:x+h]#cropping region of interest i.e. face area from  image
        roi_gray=cv2.resize(roi_gray,(48,48))
        img_pixels = image.img_to_array(roi_gray)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        img_pixels /= 255

        predictions = model.predict(img_pixels)

        #find max indexed array
        max_index = np.argmax(predictions[0])

        emotions = ('angry', 'fear', 'happy', 'sad', 'surprise', 'neutral')
        predicted_emotion = emotions[max_index]

        record[predicted_emotion] += 1
        if prev!=predicted_emotion:
            precnt = 0
            prev = predicted_emotion
        else:
            precnt += 1
        #print(record, precnt)

        cv2.putText(test_img, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        save_counter += 1
        save_counter %= 40
        if save_counter == 0:
            print("saving...")
            try:
                #connection = sqlite3.connect(database)
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM emotions;")
                row = cursor.fetchone()
                tabledata = list(row)

                for i in range(6):
                    tabledata[i] += edata[i]
                edata = [0, 0, 0, 0, 0, 0]

                edata[mapping[predicted_emotion]] += 1

                cursor.execute(f"""UPDATE emotions 
                    set angry=?, fear=?, happy=?, sad=?, surprise=?, neutral=?;""", tabledata)


                print("from predictor:", tabledata, precnt)
                connection.commit()
                cursor.close()
                #connection.close()
            except Error as e:
                print(e)
        else:
            edata[mapping[predicted_emotion]] += 1
            #print(edata, precnt)

    resized_img = cv2.resize(test_img, (400, 280))
    cv2.imshow('Facial emotion prediction ',resized_img)



    if cv2.waitKey(10) == ord('q'):#wait until 'q' key is pressed
        break
    """if time.time()-p >= 60:
                    break"""

elapsed = time.time()-p
print("per sec: ", all_count/elapsed)
print("all:", all_count)
print("time:", elapsed)

cap.release()
cv2.destroyAllWindows
print("angry: ", 10*record['angry'])
print("fear: ", 25*record['fear'])
print("surprise: ", 25*record['surprise'])
print("neutral: ", record['neutral'])
print("happy: ", record['happy'])
print("sad: ", 10*record['sad'])

connection.close()