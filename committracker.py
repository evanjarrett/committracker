import configparser
import json
from datetime import datetime, timezone
from urllib import request

config = configparser.ConfigParser()
config.read("users.conf")

users = json.loads(config.get("Default", "users"))

for user in users:
    response = request.urlopen('https://api.github.com/users/{user}/events'.format(user=user))
    events = json.load(response)
    if "message" in events:
        print(events.get("message"))
        break
    for event in events:
        if event.get("type") != "PushEvent":
            continue

        created = datetime.strptime(event.get("created_at"), '%Y-%m-%dT%H:%M:%SZ')
        created = created.replace(tzinfo=timezone.utc).astimezone()
        if created.date() == datetime.today().date():
            payload = event.get("payload")
            repo_url = "https://github.com/" + event.get("repo").get("name")
            commits = payload.get("commits")
            commits_count = len(commits)
            if commits_count > 0:
                author = commits[0].get("author").get("name")
                print("Today, {0} pushed {1} commits to {2}".format(author, commits_count, repo_url))
