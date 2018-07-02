import base64
import configparser
import json
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib import request


def get_user_commit_info(usr: str):
    """
        Gets the the latest commit information for a user, per day.
        :param usr: A string of the username
        :return A dictionary of tuples containing information about the commits
    """
    info = {}
    try:
        # TODO: Add auth token because without it, the rate limit is extremely low
        response = request.urlopen("https://api.github.com/users/{user}/events".format(user=usr))
        events = json.load(response)

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
                author = commits[0].get("author").get("name").split(" ")[0]

                if commits_count > 0:
                    if repo_url in info:
                        auth, count = info[repo_url]

                        if auth == author:
                            info.update({repo_url: (author, count + 1)})
                        break

                    info[repo_url] = (author, commits_count)

    except HTTPError as e:
        print(e)

    return info


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("users.conf")

    users = json.loads(config.get("Default", "users"))
    for user in users:
        commit_info = get_user_commit_info(user)
        if commit_info is not None:
            for r, (a, c) in commit_info.items():
                print("{0} pushed {1} commits to {2}".format(a, c, r))
