#!/usr/bin/python3

# Copyright Amar Tumballi <amarts@gmail.com>
# Under Apache License v2.0

import requests, json, re

# This app needs permission of users.list (user:read) and permission to read public channels
# Visit https://api.slack.com/apps to get the TOKEN

# TODO: consider taking token as an argument so one needn't modify the code
TOKEN="xoxp-NNNN-NNNN-NNNN-Hex"

def get_channel_list():
    r = requests.get("https://slack.com/api/conversations.list?token=%s" % TOKEN)
    return r.json()

def get_user_list():
    users = {}
    url = "https://slack.com/api/users.list?token=%s&limit=200" % TOKEN
    while True:
        r = requests.get(url)
        user_json = r.json()
        for m in user_json["members"]:
            users[m['id']] = m['name']
        cursor = user_json["response_metadata"]["next_cursor"]
        if cursor == "":
            break
        url = "https://slack.com/api/users.list?token=%s&limit=200&cursor=%s" % (TOKEN, cursor)
        
    return users

def get_channel_messages(channel):
    print ("==== %s ====" % channel['name'])
    url = "https://slack.com/api/conversations.history?token=%s&channel=%s" % (TOKEN, channel["id"])
    while True:
        r = requests.get(url)
        channel_data = r.json()
        for msg in channel_data["messages"]:
            if msg['type'] != "message":
                continue
            if 'subtype' in msg:
                continue
            text = msg['text']
            # Check for any user reference, and replace them with actual username
            if "<@" in text:
                mentions = re.findall(r'<@[A-Z0-9]*>', text)
                for u in mentions:
                    usr = re.sub('[@<>]', '', u)
                    text = re.sub(u, '@%s' % user_list[usr], text)
            # TODO: timestamp should be converted to proper human readable time
            print("%s: <%s>: %s" % (msg['ts'], user_list[msg['user']], text))

        # Check for this key, if there is more message, this key will be set to 'true'
        if not channel_data['has_more']:
            break
        cursor = channel_data["response_metadata"]["next_cursor"]
        url = "https://slack.com/api/conversations.history?token=%s&channel=%s&cursor=%s" % (TOKEN, channel["id"], cursor)


def main():
    if TOKEN == "xoxp-NNNN-NNNN-NNNN-Hex":
        print("You have not set proper auth TOKEN, visit https://api.slack.com/apps to get one")
        exit(1)

    list_of_channels = get_channel_list()
    user_list = get_user_list()
    for c in list_of_channels:
        get_channel_messages(c)

# this is global info
user_list = {}

main()
