import os
import re
from requests import Session
from bs4 import BeautifulSoup
# from os.path import isfile, join, isabs, exists


base_url = "https://manage.stg.hakuapp.com"
login_url = "/login/marine-corps"

login_parms = {
	"email": "as46@mcm22.com",
	"password": "12345678",
}


tmp_directory = "tmp"
nginx_html_directory = "/Users/porcej/Downloads/hp"

# Make directory structure if it does not exist
if not os.isabs(tmp_directory):
	tmp_directory = os.join(os.getcwd(), tmp_directory)

os.makedirs(tmp_directory, exist_ok=True)

if not os.isabs(nginx_html_directory):
	nginx_html_directory = os.join(os.getcwd(), nginx_html_directory)

os.makedirs(nginx_html_directory, exist_ok=True)





with Session() as s:
	site = s.get(base_url + login_url)
	login_soup = BeautifulSoup(site.content, "html.parser")
	form_soup = login_soup.find("form")
	action_url = form_soup['action']
	inputs = form_soup.find_all("input")
	for in_put in inputs:
		if in_put.has_key('name') and in_put.has_key('value'):
			login_parms.setdefault(in_put['name'], in_put['value'])


	response = s.post("{}{}".format(base_url, action_url),data=login_parms)

	# soup = BeautifulSoup(response.content)
# https://organizer-ec2-static.hakuapp.com/assets/components/generic_modal-1471d4474d6f198b504772957a325db6.js
	ec2_static_files = re.findall(r'https?:\/\/organizer-?e?c?2?-static[^"]*', response.content.decode("utf-8") )
	for file in ec2_static_files:
		print(file)

					# 		# NOTE the stream=True parameter below
					# 		with s.get(asset_url, stream=True) as r:
					# 			print(r.request.headers)
					# 			r.raise_for_status()
					# 			with open(local_filename, 'wb') as f:
					# 				for chunk in r.iter_content(chunk_size=8192): 
					# 					# If you have chunk encoded response uncomment if
					# 					# and set chunk_size parameter to None.
					# 					#if chunk: 
					# 					f.write(chunk)




