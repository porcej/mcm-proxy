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
	# http://docs.python.org/library/re.html#re.findall

	# print(soup.prettify())


	

	# ###############

	# # REMOVE ME

	# video_links = video_links[:1]


	# ##############
	# for video_link in video_links:
	# 	video_page_url = video_link.get('href')
	# 	video_title = video_link.get('title')

	# 	# open video page
	# 	video_page = s.get(video_page_url)
	# 	soup = BeautifulSoup(video_page.content, 'html.parser')
	# 	scripts = soup.find_all('script', {'type': 'text/javascript'})
	# 	file_links = []
	# 	for script in scripts:
	# 		script_contents = script.string
	# 		if script_contents is not None:
	# 			if "get_file" in script_contents:
	# 				# print(script_contents)
	# 				js_code = "{}\n\n{}".format(kt_player_js, script_contents)
	# 				result_js = js2py.eval_js(kt_player_js)
	# 				print(result_js)

	# 				# https://www.xmegadrive.com/get_file/1/4b4dc7b855a20d90db6debaaf41645fe77bdc03697/133000/133958/133958_720p.mp4/?rnd=1665944191554
	# 				# https://www.xmegadrive.com/get_file/1/a8fb0255d61bd9e54a4fab7b6d4c40de77bdc03697/133000/133958/133958_720p.mp4/
					
	# 				# file_links = re.findall(r"https:\/\/www\.xmegadrive\.com\/get_file\/[^']+", script_contents.strip())
	# 				# rnd = re.findall(r'\d+', re.findall(r"rnd: '\d+'", script_contents.strip())[0])[0]
					
	# 				# for file_link in file_links:
	# 				# 	print(file_link)
	# 				# 	if "_720p.mp4" in file_link:

	# 				# 		video_url = "{}?rnd={}".format(file_link, rnd)

	# 				# 		local_filename = join(output_directory, "{}.mp4".format(video_title) )
	# 				# 		print("{} -> {}".format(file_link, local_filename))
							
					# 		# NOTE the stream=True parameter below
					# 		with s.get(video_url, stream=True) as r:
					# 			print(r.request.headers)
					# 			r.raise_for_status()
					# 			with open(local_filename, 'wb') as f:
					# 				for chunk in r.iter_content(chunk_size=8192): 
					# 					# If you have chunk encoded response uncomment if
					# 					# and set chunk_size parameter to None.
					# 					#if chunk: 
					# 					f.write(chunk)





				# print(script_contents.strip())
				# print("\n\n\n==========\t\t\t==========\t\t\t==========\t\t\t==========\t\t\t==========\t\t\t==========\n\n\n")
		# print(soup.prettify())

	# print(videos)


