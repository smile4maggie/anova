import csv
import random
import airtable
import collections
from secrets import *

TOTAL_YES = 40
DECISION_TABLE_NAME = 'Decisions'
APPLICATION_TABLE_NAME = 'All%20Applications'

# Colors for printing
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# The reason we need this is because the shitty airtable API doesn't keep the questions in order...
def reorder_dict(ordered_dict):
	new_ordered_dict = collections.OrderedDict()
	fields = ['Name', \
				'Email', \
				'Phone Number', \
				'Year', \
				'Why do you want to join ANova? How do you personally resonate with ANova\'s mission statement? (max 300 words)', \
				'Tell us about your most memorable teaching or mentorship experience. (max 150 words)', \
				'What does addressing systemic issues and inequality in education look like to you? (max 150 words)', \
				'Which committee is your first choice?', \
				'Explain why the committee above is your first choice. (max 100 words)', \
				'Which committee is your second choice?', \
				'Explain why the committee above is your second choice. (max 100 words)', \
				'Which of these classes have you completed or are currently enrolled in?', \
				'Which of these languages do you know?', \
				'What are your other commitments this semester? (classes, extracurriculars, work, etc.)', \
				'Please indicate ALL your availabilities (allocate 30 minutes before and after the time slots for travel).', \
				'Can you attend orientation and retreat on 2/9 - 2/11?', \
				'Do you have any other comments or questions for us?', \
				'Time Submitted'
			]

	for field in fields:
		if field in ordered_dict.keys():
			new_ordered_dict[field] = ordered_dict[field]

	return new_ordered_dict\

# This is to ensure everyone uses the same name to review if they close the app based on the issues we ran into last semester
reviewer_names = ['Aditya', \
				'Ana', \
				'Aydin', \
				'Dakota', \
				'David', \
				'Dorothy', \
				'Franco', \
				'Helen', \
				'Jonathan', \
				'Joy', \
				'Katie', \
				'Maggie', \
				'Richard', \
				'Sai', \
				'Sunny', \
				'Thu', \
				'Will'
			]

reviewer_name = str(input('What is your name? ')).title()
if reviewer_name not in reviewer_names:
	print('The inputted name is not valid. Please provide your full first name. (i.e. Kevin)')
	quit()
print('\n')

# Creates airtable object for use with API
application_at = airtable.Airtable(APPLICATION_BASE_ID, API_KEY)
decision_at = airtable.Airtable(DECISION_BASE_ID, API_KEY)

# Adding reviewed applicants to list so we don't have to re-review them
# Get all applications that have a decision
decisions_list = decision_at.get(DECISION_TABLE_NAME)
decisions = decisions_list['records']
while 'offset' in decisions_list.keys():
	decisions_list = decision_at.get(DECISION_TABLE_NAME, offset=decisions_list['offset'])
	decisions += decisions_list['records']

reviewed_applications = set()
for decision in decisions:
	if decision['fields']['Reviewer Name'] == reviewer_name:
		reviewed_applications.add(decision['fields']['Applicant Name'])
		if decision['fields']['Interview'] == 'Yes':
			TOTAL_YES -= 1
			if TOTAL_YES <= 0:
				print("You have run out of Y's! Please manually go into the AirTable to reverse some of your decisions.")
				quit()



applications_list = application_at.get(APPLICATION_TABLE_NAME)
applications = applications_list['records']
while 'offset' in applications_list.keys():
	applications_list = application_at.get(APPLICATION_TABLE_NAME, offset=applications_list['offset'])
	applications += applications_list['records']
random.shuffle(applications)

'''AUTO REJECTION LOGIC - SKIP FOR SPRING 2018'''
# # Add auto rejected applicants to reviewed applicants
# for application in applications:
# 	if 'Status' in application['fields'].keys() and application['fields']['Status'] == 'Auto-Rejection':
# 		reviewed_applications.add(application['fields']['Name'])

committees = set(['Community', 'Curriculum', 'External Relations', 'GM Advisors', 'Professional Development', 'Publicity', 'Technology', 'Finance'])
word_count_fields = set([
						'Explain why the committee above is your first choice. (max 100 words)', \
						'Explain why the committee above is your second choice. (max 100 words)', \
						'Why do you want to join ANova? How do you personally resonate with ANova\'s mission statement? (max 300 words)', \
						'Tell us about your most memorable teaching or mentorship experience. (max 150 words)', \
						'What does addressing systemic issues and inequality in education look like to you? (max 150 words)'
					])

i = 0
while len(applications) != len(reviewed_applications) + 1:
	application = applications[i % len(applications)]
	# Printing application
	application = application['fields']

	if application['Name'] not in reviewed_applications:
		application = reorder_dict(application)
		for key, value in application.items():
			if str(value) in committees:
				print(color.BOLD + key + color.END + ' -- ' + color.RED + str(value).lstrip() + color.END + '\n')
			elif str(key) in word_count_fields:
				print(color.BOLD + key + color.END + ' -- ' + str(value).lstrip())
				print(color.BOLD + "Word Count: " + color.END + color.DARKCYAN + str(len(value.split(" "))) + color.END + '\n')
			else:
				print(color.BOLD + key + color.END + ' -- ' + str(value).lstrip() + '\n')

# 		# Prompting for decision
		decision = ''
		while decision != 'y' and decision != 'n' and decision != 's':
			decision = str(input('You have ' + color.BLUE + str(len(applications) - len(reviewed_applications) - 1) + color.END + ' applications left with ' + color.BLUE + str(TOTAL_YES) + color.END + ' more applicants you can accept. Do you want to give this applicant an interview? (y/n/s) ')).lower()

# 		# Saving data to airtable
		data = dict()
		data['Applicant Name'] = application['Name']
		data['Reviewer Name'] = reviewer_name
		if decision == 'y':
			data['Interview'] = 'Yes'
			decision_at.create('Decisions', data)
			reviewed_applications.add(application['Name'])
			TOTAL_YES -= 1
			if TOTAL_YES <= 0:
				print("You have run out of Y's! Please manually go into the AirTable to reverse some of your decisions.")
				quit()
		elif decision == 'n':
			data['Interview'] = 'No'
			decision_at.create('Decisions', data)
			reviewed_applications.add(application['Name'])
		elif decision == 's':
			i = i + 1
		print('\n\n\n')

	else:
		i = i + 1

print(color.RED + 'You have no more applications left to review! Please check back periodically for more applications.' + color.END)
