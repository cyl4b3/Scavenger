#!/usr/bin/python

import time
import tweepy
import os
import httplib2
import sys
from bs4 import BeautifulSoup, SoupStrainer

iterator = 1

#Twitter API credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

if sys.argv[1] == "api":
	print "[#] Using API to gather pastes."
else:
	print "[#] Using website scraping to gather pastes."

while 1:
	# check if enough files are in raw_pastes
	DIR = "data/raw_pastes"
	pasteCount = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
	# if number of pastes > 48.000 save them to the archive and execute filter script
	if pasteCount > 48000:
		print "*** Processing Raw Pastes ***"
		print "[+] Filter for passwords"
		os.system("python filter.py")
		print "[+] Zip raw pastes and copy them to archive"
		archiveFileName = str(time.time()) + ".zip"
		os.system("zip -r " + archiveFileName + " " + DIR)
		os.system("mv " + archiveFileName + " archive/.")
		print "[+] Removing raw pastes"
		os.system("rm " + DIR + "/*")
		
	print str(iterator) + ". iterator:"
	iterator += 1
	http = httplib2.Http()
	try:
		status, response = http.request('http://pastebin.com/archive')
		time.sleep(120)
		print "[#] Waiting..."

		for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
			if "HTML" not in link:
				if link.has_attr('href'):
					if len(link['href']) == 9 and link['href'][0] == '/' and link['href'] != '/messages' and link['href'] != '/settings' and link['href'] != '/scraping':
						print "[*] Crawling " + link['href']
						if sys.argv[1] != "api":
							binStatus, binResponse = http.request('http://pastebin.com/raw' + link['href'])
						else:
							# Use Pastebin.com API. Remember to whitelist your IP in your pastebin PRO account
							# This change was implemented because it seems that Pastebin.com recently changed their IP block policy when you simply scrape their site
							scrapingID = link['href'].replace("/", "")
							binStatus, binResponse = http.request('http://scrape.pastebin.com/api_scrape_item.php?i=' + scrapingID)
						try:
							file_ = open('data/raw_pastes' + link['href'], 'w')
							file_.write(binResponse)
							file_.close()
						
							emailPattern = os.popen("grep -l -E -o \"\\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z0-9.-]+\\b\" data/raw_pastes/" + link['href']).read()
							emailPattern = emailPattern.split("\n")
							for file in emailPattern:
								if file != "":
									with open("data/raw_pastes/" + link['href']) as f:
										pasteContent = f.readlines()
									skip = 0
									for line in pasteContent:
										curLine = line.strip()
										if (":" in curLine or ";" in curLine or "," in curLine) and "://" not in curLine and len(curLine) <=100 and "android:" not in curLine and "#EXTINF" not in curLine:
											pass
										else:
											skip = 1
									if skip == 0:
										print "Found credentials. Posting on twitter..."
										api.update_status ("")
									#continue
						
							time.sleep(2)
						except:
							print "[-] File error!"
							continue

		print "++++++++++"
		print ""
	except:
		print "[-] Connection error!"
		continue
