#!/usr/bin/env python3
# Instagramer by Codelatte

"""
  _           _                                            
 (_)         | |                                           
  _ _ __  ___| |_ __ _  __ _ _ __ __ _ _ __ ___   ___ _ __ 
 | | '_ \/ __| __/ _` |/ _` | '__/ _` | '_ ` _ \ / _ \ '__|
 | | | | \__ \ || (_| | (_| | | | (_| | | | | | |  __/ |   
 |_|_| |_|___/\__\__,_|\__, |_|  \__,_|_| |_| |_|\___|_|   
                        __/ |                              
                       |___/    https://dev.codelatte.net       
"""

import json
import os
import sys
import time
import urllib.request
from optparse import OptionParser
from typing import (
	AnyStr
)

import requests


def getUserDetails(username: AnyStr) -> None:
	with requests.get("https://www.instagram.com/" + username + "/?__a=1") as response:
		try:
			assert response.status_code != 404
		except AssertionError:
			raise BaseException("Error: User Not Found!")
		except requests.ConnectionError:
			raise ConnectionError("Error: Connnection Error")
		finally:
			data = response

	output = json.loads(data.content)

	if not os.path.exists(username):
		os.makedirs(username)

	info = {
		'user_id': output["graphql"]["user"]["id"],
		'username': output["graphql"]["user"]["username"],
		'full_name': output["graphql"]["user"]["full_name"],
		'biography': str(output["graphql"]["user"]["biography"].replace("\n", " | ")),
		'profile_pic_url_hd': output["graphql"]["user"]["profile_pic_url_hd"],
		'highlight_story': output["graphql"]["user"]["highlight_reel_count"],
		'external_url': output["graphql"]["user"]["external_url"],
		'followers': output["graphql"]["user"]["edge_followed_by"]["count"],
		'followings': output["graphql"]["user"]["edge_follow"]["count"],
		'media_count': output["graphql"]["user"]["edge_owner_to_timeline_media"]["count"],
		'is_joined_recently': output["graphql"]["user"]["is_joined_recently"],
		'is_business_account': output["graphql"]["user"]["is_business_account"],
		'business_category_name': output["graphql"]["user"]["business_category_name"],
		'is_private': output["graphql"]["user"]["is_private"],
		'connected_fb_page': output["graphql"]["user"]["connected_fb_page"],
		'is_verified': output["graphql"]["user"]["is_verified"]
	}

	with open(username + "/info.json", "w") as file:
		try:
			file.write(json.dumps(info, indent=4) + "\n")
		finally:
			file.close()

	if options.getmedia is None:
		print("USER INFORMATION")
		print("----------------------")

		print("User ID \t\t: " + str(output["graphql"]["user"]["id"]))
		print("Username \t\t: " + str(output["graphql"]["user"]["username"]))
		print("Full Name \t\t: " + str(output["graphql"]["user"]["full_name"]))
		print("Biography \t\t: " + str(output["graphql"]["user"]["biography"].replace("\n", " | ")))
		text = "Profile Picture URL (HD)"
		target = output["graphql"]["user"]["profile_pic_url_hd"]
		print("Profile Picture \t: " + str(f"\u001b]8;;{target}\u001b\\{text}\u001b]8;;\u001b\\"))
		print("Highlight Story \t: " + str(output["graphql"]["user"]["highlight_reel_count"]))
		print("External URL \t\t: " + str(output["graphql"]["user"]["external_url"]))
		print("Followers / Followings \t: " + str(
			output["graphql"]["user"]["edge_followed_by"]["count"]) + " Followers / " + str(
			output["graphql"]["user"]["edge_follow"]["count"]) + " Followings")
		print("Total Media(s) \t\t: " + str(output["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]))
		print("Joined Recently \t: " + str(output["graphql"]["user"]["is_joined_recently"]))
		print("Bussines Account \t: " + str(output["graphql"]["user"]["is_business_account"]))
		print("Bussines Category \t: " + str(output["graphql"]["user"]["business_category_name"]))
		print("Private Account \t: " + str(output["graphql"]["user"]["is_private"]))
		print("Connect to FB \t\t: " + str(output["graphql"]["user"]["connected_fb_page"]))
		print("Verified \t\t: " + str(output["graphql"]["user"]["is_verified"]))

		print("\n\nOutput File: " + username + "/info.json")
		print("Note: Use \"--get-media\" to download all " + str(output["graphql"]["user"]["username"]) + "'s media.")
	else:
		print("\n")
		if output["graphql"]["user"]["edge_owner_to_timeline_media"]["count"] > 50:
			next_page = 1
		else:
			next_page = 0

		getUserMedia(output["graphql"]["user"]["id"], str(output["graphql"]["user"]["username"]),
					 str(output["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]),
					 output["graphql"]["user"]["is_private"], next_page)


def getUserMedia(user_id: AnyStr, username: AnyStr, media_count: AnyStr, is_private: AnyStr,
				 next_page: int = 0, end_cursor: AnyStr = "", itung: int = 0):
	if is_private:
		raise "Error: Private User detected! Can't get " + username + "'s media!"

	if itung == 0:
		print("GET USER's MEDIA " + "(" + media_count + ")")
		print("Note: Downloading video file will take longer than image.")
		print("----------------------")
		time.sleep(3)

	if next_page == 1:
		with requests.get(
				"https://www.instagram.com/graphql/query/?query_id=17888483320059182&id=" + user_id + "&first=50&after=" + str(
					end_cursor)) as response:
			try:
				data = response
			except requests.ConnectionError:
				raise ConnectionError("Error: Connection Error")

		output = json.loads(data.content)
	else:
		with requests.get(
				"https://www.instagram.com/graphql/query/?query_id=17888483320059182&id=" + user_id + "&first=50&after=") as response:
			try:
				data = response
			except requests.ConnectionError:
				raise ConnectionError("Error: Connection Error")

		output = json.loads(data.content)

	for x in output["data"]["user"]["edge_owner_to_timeline_media"]["edges"]:
		media_type = "Image" if x["node"]["is_video"] == False else "Video"

		if media_type == "Video":
			data_video = urllib.request.urlopen(
				"https://www.instagram.com/p/" + str(x["node"]["shortcode"]) + "/?__a=1").read()
			output_video = json.loads(data_video)
			filename = output_video["graphql"]["shortcode_media"]["video_url"].split('?')[0]
			filename = filename.split('/')[-1]
			urllib.request.urlretrieve(output_video["graphql"]["shortcode_media"]["video_url"],
									   username + "/" + filename)
		else:
			filename = str(x["node"]["thumbnail_src"]).split('?')[0]
			filename = filename.split('/')[-1]
			urllib.request.urlretrieve(str(x["node"]["thumbnail_src"]), username + "/" + filename)

		itung = itung + 1

		print("Media Count \t: " + str(itung) + " / " + str(media_count))
		print("Timestamp \t: " + time.ctime(int(x["node"]["taken_at_timestamp"])))
		text = "Post URL"
		target = "https://www.instagram.com/p/" + str(x["node"]["shortcode"])
		print("Shortcode \t: " + str(x["node"]["shortcode"]) + " | " + str(
			f"\u001b]8;;{target}\u001b\\{text}\u001b]8;;\u001b\\"))
		if media_type == "Video":
			print("Media Type \t: Video")
			print("Video View \t: " + str(x["node"]["video_view_count"]))
		else:
			print("Media Type \t: Image")
		print("Like(s) \t: " + str(x["node"]["edge_media_preview_like"]["count"]))
		print("Comment(s) \t: " + str(x["node"]["edge_media_to_comment"]["count"]))
		print("Saved Media \t: " + username + "/" + filename)
		print("------------------------------------------")

	if output["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"] == 1:
		getUserMedia(user_id, username, media_count, 1, output["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"], itung)
	else:
		print("\nGet " + username + "'s " + media_count + " Media(s) Success")


banner = """  _           _                                            
 (_)         | |                                           
  _ _ __  ___| |_ __ _  __ _ _ __ __ _ _ __ ___   ___ _ __ 
 | | '_ \/ __| __/ _` |/ _` | '__/ _` | '_ ` _ \ / _ \ '__|
 | | | | \__ \ || (_| | (_| | | | (_| | | | | | |  __/ |   
 |_|_| |_|___/\__\__,_|\__, |_|  \__,_|_| |_| |_|\___|_|   
                        __/ |                              
                       |___/    https://dev.codelatte.net       """

parser = OptionParser(usage="Usage: python3 %prog -u [username]")
parser.add_option("-u", dest='username', help="Get Account Details")
parser.add_option("--get-media", action='store_true', dest='getmedia', help="Get All User's Media")
(options, args) = parser.parse_args()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print(banner)
		parser.print_help()
		sys.exit()
	else:
		print(banner)

	try:
		if options.username:
			getUserDetails(options.username)
		elif options.getmedia:
			getUserDetails(options.username)
	except KeyboardInterrupt:
		print("\nExiting...")
