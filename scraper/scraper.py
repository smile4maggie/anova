import requests
import requests.exceptions
from bs4 import BeautifulSoup as bp
from urllib.parse import urlsplit
import re

emails = set()
processed_urls = set()

urls = ['http://www.hepbproject.org/contact-us.html']

for url in urls:

	# Getting base url as well as path to url
	parts = urlsplit(url)
	base_url = "{0.scheme}://{0.netloc}".format(parts)
	path = url[:url.rfind('/')+1] if '/' in parts.path else url

	# We don't want to process the same base url (we will recurse through all subdomains)
	if base_url in processed_urls:
		continue
	
	processed_urls.add(base_url)

	print("Processing %s" % url)

	# Getting response from webpage
	try:
		response = requests.get(url)
	except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
		# ignore pages with errors
		continue

	# extract all email addresses and add them into the resulting set
	new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
	emails.update(new_emails)

print(emails)