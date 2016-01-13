#! /usr/bin/python
# -*- coding: utf-8-*-

print "Content-type: application/json\n\n"

import json
import oauth_load
import requests


get_creds = oauth_load.loadSecret()

account_id = get_creds["account_id"]

token = oauth_load.getAuthToken(get_creds)

tag = "smgvfb"


def basic_search(token, tag, account_id):

    url = "https://cms.api.brightcove.com/v1/accounts/{}/videos?q=tags:{}".format(
        account_id, tag)
    print url
    headers = {"Authorization": "Bearer %s" % token}
    r = requests.get(url, headers=headers)
    res = json.loads(r.text)
    # a list of tuples containing video ID, title, and description
    video_asset_ids = []
    print len(res)
    for index, item in enumerate(res):
        print type(item)
        print index, item
        # get info from each dictionary item
        id = item.get('id')
        title = item.get('name')
        description = item.get('description')
        print id
        video_asset_ids.append((id, title, description))
    print video_asset_ids
    return video_asset_ids


cms_response = basic_search(token, tag)


def get_asset_data(token, asset_id, account_id):
    url = "https://cms.api.brightcove.com/v1/accounts/{}/videos/{}".format(
        account_id, asset_id)
    headers = {"Authorization": "Bearer %s" % token}
    r = requests.get(url, headers=headers)
    res = json.loads(r.text)
    return res


def get_asset_data(token, video_id, account_id):
    """ returns JSON object that contains a bunch of
    asset-related data for a specific video, but not
    metadata """
    url = "https://cms.api.brightcove.com/v1/accounts/{}/videos/{}/sources".format(
        account_id, video_id)
    headers = {"Authorization": "Bearer %s" % token}
    r = requests.get(url, headers=headers)
    res = json.loads(r.text)
    return res


def parse_asset_data(get_asset_data):
    """ parsing get_asset_data JSON object
    containing video asset data, specifically for mp4 source URL """
    for index, item in enumerate(get_asset_data):
        mp4_url = 0
        # look for the dictionary in the API response (type(get_source)==list)
        # that contains both 1280 width (which is the value to key 'width')
        # and src (which is the key, whose value is the file source URL)
        if 1280 in item.values() and 'src' in item:
            mp4_url = item.get('src')
          # print "This is the mp4_url: %s" % mp4_url
            return mp4_url


# iterating through cms_response object, which is a list of tuples
for index, item in enumerate(cms_response):
    video_id = item[0]
    videoName = item[1]
    videoDescription = item[2]
    get_assets = get_asset_data(token, video_id)
    videoUrl = parse_asset_data(get_assets)
    #print "TITLE: %s" % videoName
    #print "DESCRIPTION: %s" % videoDescription
    #print "VIDEO URL: %s" % videoUrl
    #print "\n"

    if videoExists(videoUrl):
        print "This video has already been uploaded to Facebook."

    if not videoExists(videoUrl):
        print "Haven't seen", videoUrl, "before, adding it to Facebook!"

        # Make our POST request to Facebook Graph API:
        access = '[Insert Your Permanent Page Access Token here]'
        # SMGV Video Dev
        fburl = 'https://graph-video.facebook.com/v2.3/[Insert Facebook Page ID here]/videos?access_token=' + str(
            access)
        payload = {
            'name': '%s' % (videoName),
            'description': '%s' % (videoDescription),
            'file_url': '%s' % (videoUrl)}
        flag = requests.post(fburl, data=payload).text
        print flag
        fb_res = json.loads(flag)
        if not "error" in fb_res:
            addVideo(videoUrl)
        else:
            print "An error occured uploading to facebook for ", videoUrl
