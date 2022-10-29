import os
import re
from requests import Session
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# from os.path import isfile, join, isabs, exists


# base_url = "https://manage.stg.hakuapp.com"	# Stage
base_url = "https://manage.hakuapp.com"		# Productions
login_url = "/login/marine-corps"

pages_to_scrape = [
	"https://organizer.hakuapp.com/event_masters",
	"https://organizer.hakuapp.com/events/ee0476def51166744f34/clinical/encounters/dashboard",
	"https://organizer.hakuapp.com/events/ee0476def51166744f34/clinical/encounters",
	"https://organizer.hakuapp.com/events/ee0476def51166744f34/clinical/encounters/new",
	"https://organizer.hakuapp.com/events/ee0476def51166744f34/clinical/encounters/3090/edit",
	"https://organizer.hakuapp.com/events/ee0476def51166744f34/clinical/encounters?store_last_path=false",
	"https://organizer.hakuapp.com/messages",
	"https://organizer.hakuapp.com/events?is_medical=true",
	"https://manage.hakuapp.com/session_expired",
	"https://manage.hakuapp.com/session_expired",
	"https://manage.hakuapp.com/login?source=marine-corps",
	"https://manage.hakuapp.com/login/marine-corps",
	"https://manage.hakuapp.com/login?source=marine-corps"
]

login_parms = {
	"email": "as46@mcm22.com",
	"password": "12345678",
}

static_assets = [
	{
		"url_regex": r'https?:\/\/organizer-?e?c?2?-static[^"^)]*',
		"net_loc": "https://organizer-ec2-static.hakuapp.com",
		"folder": "ec2-static"
	}, {
		"url_regex": r'https?:\/\/s3\.amazonaws\.com[^"^)]*',
		"net_loc": "https://s3.amazonaws.com/",
		"folder": "s3"
	}, {
		"url_regex": r'https?:\/\/fonts\.googleapis\.com[^"^)]*',
		"net_loc": "https://fonts.googleapis.com",
		"folder": "googlefonts"
	}, {
		"url_regex": r'https:\/\/fonts\.gstatic\.com[^"^)]*',
		"net_loc": "https://fonts.gstatic.com",
		"folder": "gstatic"
	}
]

css_replacement = {
	"Crete": "css?family=Crete+Round:400,400italic",
	"Pacifico": "css?family=Pacifico",
	"Domine": "css?family=Domine:400,700",
}

static_files = []
have_files = []


tmp_directory = "tmp"
nginx_html_directory = "/etc/nginx/html"

# Make directory structure if it does not exist
if not os.path.isabs(tmp_directory):
	tmp_directory = os.path.join(os.getcwd(), tmp_directory)

os.makedirs(tmp_directory, exist_ok=True)

# if not os.path.isabs(nginx_html_directory):
# 	nginx_html_directory = os.path.join(os.getcwd(), nginx_html_directory)

# os.makedirs(nginx_html_directory, exist_ok=True)


def get_assets(content):
	for static_asset in static_assets:
		files = re.findall(static_asset['url_regex'] , content)
		for file in files:
			if file not in have_files:	# Only add files if we don't already have them
				have_files.append(file)
				static_files.append({'url': file, 'folder': static_asset['folder']})

def get_css_assets(response):
	content = response.content.decode("utf-8")
	assets = re.findall(r'url\("?([^)^""]*)' , content)

	# Remove data encoded urls
	assets = filter(lambda asset: not asset.startswith("data:"), assets)

	for asset in assets:
		fqdn = urljoin(response.url, urlparse(asset).path)
		
		if fqdn not in have_files:
			content = content.replace(asset, fqdn)
			get_assets(fqdn)

	return content


with Session() as s:
	site = s.get(base_url + login_url)
	
	# Scrape the login page
	get_assets(site.content.decode("utf-8")) # Get any static assets

	login_soup = BeautifulSoup(site.content, "html.parser")
	form_soup = login_soup.find("form")
	action_url = form_soup['action']
	inputs = form_soup.find_all("input")
	for in_put in inputs:
		if in_put.has_key('name') and in_put.has_key('value'):
			login_parms.setdefault(in_put['name'], in_put['value'])


	# Login and scrape that page too
	response = s.post("{}{}".format(base_url, action_url),data=login_parms)
	get_assets(response.content.decode("utf-8"))

	for page_to_scrape in pages_to_scrape:
		response = s.get(page_to_scrape)
		get_assets(response.content.decode("utf-8"))

	fdx = 0
	while fdx < len(static_files):
		file = static_files[fdx]
	# for file in static_files:
		try:
			response = s.get(file['url'])
		except:
			print("************************ {}".format(file['url']))
			fdx += 1
			continue
			# print("*_"*80)
			# print("-*"*80)
			# print("*_"*80)
			# print("-*"*80)
			# print("*_"*80)
			# print("-*"*80)
			# print("*_"*80)
			# print("-*"*80)
			# print("*_"*80)
			# print("-*"*80)
			# print("*_"*80)
			# print("-*"*80)
			# print(file['url'])
			# print(urlparse(file['url']))

		parsed_url = urlparse(file['url'])
		local_filename = parsed_url.path[1:]
		if local_filename.endswith("css") and parsed_url.query != '':
			for font in css_replacement.keys():
				if font in parsed_url.query:
					local_filename = font


			# local_filename = "{}?{}".format(local_filename, parsed_url.query)
		local_filename = os.path.join(tmp_directory, file['folder'], local_filename)
		print(local_filename)
		os.makedirs(os.path.dirname(local_filename), exist_ok=True)

		if "image" in response.headers['Content-Type'] or "font" in response.headers['Content-Type'] or file['url'].endswith("png") or file['url'].endswith("woff2") or file['url'].endswith("ttf") or file['url'].endswith("otf"):
			with open(local_filename, 'wb') as f:
				f.write(response.content)

		else:
			if "css" in response.headers['Content-Type'] or file['url'].endswith("css"):
				content = get_css_assets(response)
			else:
				print("{}:{}".format(response.headers['Content-Type'], response.url))
				content = response.content.decode("utf-8")
			
			get_assets(content)
			for static_asset in static_assets:
				content = content.replace(static_asset['net_loc'], "/{}".format(static_asset['folder']))
				for font, font_string in css_replacement.items():
					content = content.replace(font_string, font)
			with open(local_filename, 'w') as f:
				f.write(content)

		fdx += 1;
				
	# for folder in nested_static_files:
	# 	for file in nested_static_files[folder]:
	# 		response = s.get(file)
	# 		local_filename = os.path.join(tmp_directory, folder ,local_filename)
	# 		print(local_filename)
	# 		os.makedirs(os.path.dirname(local_filename), exist_ok=True)

	# 		if "image" in response.headers['Content-Type'] or "font" in response.headers['Content-Type']:
	# 			with open(local_filename, 'wb') as f:
	# 				f.write(response.content)
	# 		else:
	# 			content = response.content.decode("utf-8")
	# 			for static_asset in static_assets:
	# 				content = content.replace(static_asset['net_loc'], "/{}".format(static_asset['folder']))
	# 			with open(local_filename, 'w') as f:
	# 				f.write(content)


			# print("{} - {}".format(response.headers, file))


	# soup = BeautifulSoup(response.content)
# https://organizer-ec2-static.hakuapp.com/assets/components/generic_modal-1471d4474d6f198b504772957a325db6.js
	# for static_asset in static_assets:
	# 	static_files[static_asset['folder']] = re.findall(static_asset['url_regex'] , response.content.decode("utf-8") )


	# # print(pprint(static_files))

	# 	# ec2_static_files = re.findall(r'https?:\/\/organizer-?e?c?2?-static[^"]*', response.content.decode("utf-8") )
	# for folder in static_files:
	# 	for file in static_files[folder]:
	# 		pass
			# print("{} - {}".format(folder, file))

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




