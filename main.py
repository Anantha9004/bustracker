import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import cv2
import imutils
import sys
import pytesseract
import pandas as pd
import time
import datetime

image = cv2.imread("C:\\Users\\91773\\PycharmProjects\\pythonProject\\venv\\Scripts\\R.jpg")

image = imutils.resize(image, width=500)

#cv2.imshow("Original Image", image)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#cv2.imshow("1 - Grayscale Conversion", gray)

gray = cv2.bilateralFilter(gray, 11, 17, 17)
#cv2.imshow("2 - Bilateral Filter", gray)

edged = cv2.Canny(gray, 170, 200)
#cv2.imshow("4 - Canny Edges", edged)

(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts=sorted(cnts, key = cv2.contourArea, reverse = True)[:30]
NumberPlateCnt = None

count = 0
for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            NumberPlateCnt = approx
            break

# Masking the part other than the number plate
mask = np.zeros(gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[NumberPlateCnt],0,255,-1)
new_image = cv2.bitwise_and(image,image,mask=mask)
#cv2.namedWindow("Final_image",cv2.WINDOW_NORMAL)
#cv2.imshow("Final_image",new_image)

# Configuration for tesseract
config = ('-l eng --oem 1 --psm 3')

# Run tesseract OCR on image
text = pytesseract.image_to_string(new_image, config=config)

#Data is stored in CSV file
raw_data = {'date': [time.asctime( time.localtime(time.time()) )],
        'v_number': [text]}

df = pd.DataFrame(raw_data, columns = ['date', 'v_number'])
df.to_csv('data.csv')

# Print recognized text
print(text)

cv2.waitKey(0)

scopes=["https://www.googleapis.com/auth/spreadsheets"]
creds=Credentials.from_service_account_file("bt.json", scopes=scopes)
client=gspread.authorize(creds)
sheet_id="1IqF6JCycTRYcduDjchx5JJ3kfwFb3ARmX-Lv-eyyifI"
workbook=client.open_by_key(sheet_id)
sheet=workbook.worksheet("Sheet1")
for i in range(2,6):
    value = workbook.sheet1.cell(i,2).value
    print("value :",value)
    print("text :",text)
    if text.strip() == value:
        print("hello")
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        sheet.update_cell(i, 5, time_string)