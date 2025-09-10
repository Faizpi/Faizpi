import os
import requests
from lxml import etree

USERNAME = os.getenv("USER_NAME", "Faizpi")
TOKEN = os.getenv("ACCESS_TOKEN")

headers = {"Authorization": f"token {TOKEN}"}

# ====== GET BASIC USER DATA ======
url_user = f"https://api.github.com/users/{USERNAME}"
r_user = requests.get(url_user, headers=headers).json()

followers = r_user.get("followers", 0)
public_repos = r_user.get("public_repos", 0)

# ====== GET REPOS DATA ======
url_repos = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
r_repos = requests.get(url_repos, headers=headers).json()

stars = 0
for repo in r_repos:
    stars += repo.get("stargazers_count", 0)

# Placeholder (karena GitHub API untuk commit & LOC butuh looping semua repo)
total_commits = 0  # bisa ditambahin nanti
lines_added = 0
lines_deleted = 0

# ====== UPDATE SVG ======
parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse("dark_mode.svg", parser)

def set_text_by_id(tid, value):
    el = tree.xpath(f"//*[@id='{tid}']")
    if el:
        el[0].text = str(value)

set_text_by_id("repo_data", public_repos)
set_text_by_id("star_data", stars)
set_text_by_id("follower_data", followers)
set_text_by_id("commit_data", total_commits)
set_text_by_id("loc_data", lines_added + lines_deleted)
set_text_by_id("loc_add", lines_added)
set_text_by_id("loc_del", lines_deleted)

tree.write("dark_mode.svg", pretty_print=True, encoding="utf-8", xml_declaration=True)
tree.write("light_mode.svg", pretty_print=True, encoding="utf-8", xml_declaration=True)
