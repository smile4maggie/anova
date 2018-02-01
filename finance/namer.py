# brew install tesseract
# python3 -m pip install Pillow

from PIL import Image
from pytesseract import image_to_string
import re
import datetime
import os


first_name = str(input('What is your first name? ')).title()
last_name = str(input('What is your last name? ')).title()
site = str(input('What site are you submitting reimbursements for? ')).title()


images = list()
for filename in os.listdir('images'):
    if filename.endswith('.png'): 
        images.append(os.path.join('images', filename))

min_iso_calendar = float("inf")
data = dict()
for image in images:
	text_in_image = image_to_string(Image.open(image))

	date = re.search(r'(\d+/\d+/\d+)', text_in_image).group(0)
	date_time = datetime.datetime.strptime(date, '%m/%d/%y')
	
	if date_time.isocalendar()[1] < min_iso_calendar:
		min_iso_calendar = date_time.isocalendar()[1]

	price = re.search(r'\$[0-9]+.[0-9]+', text_in_image).group(0)[1:]

	data[image] = [date_time, price]

	print(date)
	print(price)

if not os.path.exists('renamed'):
    os.makedirs('renamed')

for key, value in data.items():
	os.rename(key, 'renamed/' + first_name + '_' + last_name + '_' + site + '_' + 'Week' + str(value[0].isocalendar()[1] - min_iso_calendar) + '_' + value[1] + ".png")
