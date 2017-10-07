import csv
import random
import airtable

# Airtable keys
API_KEY = 'keyd6qkfF0Q6csT9G'
APPLICATION_BASE_ID = 'apppVfnNT3wEXplHg'
DECISION_BASE_ID = 'appo9HwPc9Oy8IZcG'

TOTAL_YES = 50

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

reviewer_name = str(input('What is your name? '))
print('\n')

# Creates airtable object for use with API
application_at = airtable.Airtable(APPLICATION_BASE_ID, API_KEY)
decision_at = airtable.Airtable(DECISION_BASE_ID, API_KEY)

# Adding reviewed applicants to list so we don't have to re-review them
decisions_list = decision_at.get('Decisions')
decisions = decisions_list['records']
while 'offset' in decisions_list.keys():
	decisions_list = decision_at.get('Decisions', offset=decisions_list['offset'])
	decisions += decisions_list['records']

reviewed_applications = set()
for decision in decisions:
	if decision['fields']['Reviewer Name'] == reviewer_name:
		reviewed_applications.add(decision['fields']['Applicant Name'])
		if decision['fields']['Interview'] == 'Yes':
			TOTAL_YES -= 1

# Add auto rejected applicants to reviewed applicants
applications_list = application_at.get('Applications')
applications = applications_list['records']
while 'offset' in applications_list.keys():
	applications_list = application_at.get('Applications', offset=applications_list['offset'])
	applications += applications_list['records']
random.shuffle(applications)

for application in applications:
	if 'Status' in application['fields'].keys() and application['fields']['Status'] == 'Auto-Rejection':
		reviewed_applications.add(application['fields']['Name'])

skipped_fields = ['Email', 'Phone Number', 'Time Submitted', 'Please indicate ALL your availabilities (allocate 45 minutes before and after the time slots for travel).']
committees = set(['Community', 'Curriculum', 'DeCal Advisor', 'Events', 'External Relations', 'Finance', 'Professional Development', 'Publicity'])
word_count_fields = set(['Explain why the committee above is your first choice. (minimum 100 words)', 'Explain why the committee above is your second choice. (minimum 100 words)', 'Why do you want to join ANova? How do you personally resonate with ANova\'s mission statement? (minimum 300 words)', 'As a member of our club, how will you contribute to our organization? (minimum 200 words)'])
for application in applications:
	# Printing application
	application = application['fields']

	if application['Name'] not in reviewed_applications:
		for key, value in application.items():
			if key not in skipped_fields:
				if str(value) in committees:
					print(color.BOLD + key + color.END + ' -- ' + color.RED + str(value).lstrip() + color.END + '\n')
				elif str(key) in word_count_fields:
					print(color.BOLD + key + color.END + ' -- ' + str(value).lstrip())
					print(color.BOLD + "Word Count: " + color.END + color.DARKCYAN + str(len(value.split(" "))) + color.END + '\n')
				else:
					print(color.BOLD + key + color.END + ' -- ' + str(value).lstrip() + '\n')

# 		# Prompting for decision
		decision = ''
		while decision != 'y' and decision != 'n':
			decision = str(input('You have ' + color.BLUE + str(len(applications) - len(reviewed_applications)) + color.END + ' applications left with ' + color.BLUE + str(TOTAL_YES) + color.END + ' more applicants you can accept. Do you want to give this applicant an interview? (y/n) '))

		reviewed_applications.add(application['Name'])

# 		# Saving data to airtable
		data = dict()
		data['Applicant Name'] = application['Name']
		data['Reviewer Name'] = reviewer_name
		if decision == 'y':
			data['Interview'] = 'Yes'
			TOTAL_YES -= 1
		else:
			data['Interview'] = 'No'
		decision_at.create('Decisions', data)

		print('\n\n\n')
