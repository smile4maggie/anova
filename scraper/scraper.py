from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
from nltk.corpus import wordnet
import nltk
import csv


def extract_url_parts(url):
	parts = urlsplit(url)
	base_url = "{0.scheme}://{0.netloc}".format(parts)
	path = url[:url.rfind('/')+1] if '/' in parts.path else url
	return base_url, path

def update_csv(emails, existing_emails):
	for email in emails:
		if not wordnet.synsets(email.split("@")[0]) and email not in existing_emails:
			fd = open('emails.csv','a')
			fd.write(email + '\n')
			fd.close()
			existing_emails.add(email)
	return existing_emails

def get_existing_emails():
	with open('emails.csv', 'r') as f:
		reader = csv.reader(f)
		list_emails = [item for sublist in list(reader) for item in sublist]
		return set(list_emails)

def main():
	with open('berkeley_urls.txt', 'r') as f:
	    urls_list = f.read().splitlines()

	# a queue of urls to be crawled
	new_urls = deque(urls_list)

	# a set of urls that we have already crawled
	processed_urls = set()

	# a set of scraped urls
	emails = get_existing_emails()

	# process urls one by one until we exhaust the queue
	while len(new_urls):
	    # move next url from the queue to the set of processed urls
		try:
			url = new_urls.popleft()
			processed_urls.add(url)

			if len(url) > 75:
				continue

			# extract base url to resolve relative links
			base_url, path = extract_url_parts(url)
			# get url's content
			print("Processing %s" % url)
			try:
			    response = requests.get(url)
			except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
			    # ignore pages with errors
			    continue

			# extract all email addresses and add them into the resulting set, but check if first part is a word (filters out random emails)
			if base_url == "https://www2.eecs.berkeley.edu":
				modified_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+", response.text, re.I))
				new_emails = set()
				for email in modified_emails:
					email += ".berkeley.edu"
					new_emails.add(email)
				new_emails.update(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
			else:
				new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
			emails = update_csv(new_emails, emails)

			# create a beutiful soup for the html document
			soup = BeautifulSoup(response.text, "lxml")

			# find and process all the anchors in the document
			for anchor in soup.find_all("a"):
			    # extract link url from the anchor
			    link = anchor.attrs["href"] if "href" in anchor.attrs else ''
			    # resolve relative links
			    if link.startswith('/'):
			        link = base_url + link
			    elif not link.startswith('http'):
			        link = path + link
			    # add the new url to the queue if it was not enqueued nor processed yet
			    if not link in new_urls and not link in processed_urls and base_url == "{0.scheme}://{0.netloc}".format(urlsplit(link)):
			        new_urls.append(link)
			        
		except Exception as e:
			print(e)

if __name__ == "__main__":
    main()