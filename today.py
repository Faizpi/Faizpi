import os
import requests
from lxml import etree
from datetime import date, timedelta

# --- KONFIGURASI ---
USERNAME = os.getenv("USER_NAME", "Faizpi")
TOKEN = os.getenv("ACCESS_TOKEN")
BIRTH_DATE = date(2005, 3, 2)  # tanggal lahir

# --- SETUP ---
headers = {"Authorization": f"token {TOKEN}"}

# --- 1. MENGHITUNG UMUR (UPTIME) SECARA OTOMATIS ---
def calculate_age(birthdate):
    today = date.today()
    years = today.year - birthdate.year
    months = today.month - birthdate.month
    days = today.day - birthdate.day

    if days < 0:
        months -= 1
        last_month_end = today.replace(day=1) - timedelta(days=1)
        days += last_month_end.day
    
    if months < 0:
        years -= 1
        months += 12
        
    return f"{years} years, {months} months, {days} days"

# --- 2. AMBIL DATA DASAR PENGGUNA ---
print("Fetching user data...")
url_user = f"https://api.github.com/users/{USERNAME}"
r_user = requests.get(url_user, headers=headers).json()

followers = r_user.get("followers", 0)
public_repos = r_user.get("public_repos", 0)

# --- 3. AMBIL DATA REPOSITORI DAN HITUNG BINTANG (STARS) ---
print("Fetching repository data...")
url_repos = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
r_repos = requests.get(url_repos, headers=headers).json()

stars = 0
for repo in r_repos:
    stars += repo.get("stargazers_count", 0)

# --- 4. HITUNG TOTAL COMMIT DI SEMUA REPO PUBLIK ---
print("Calculating total commits...")
total_commits = 0
for repo in r_repos:
    if not repo.get("fork", False):
        repo_name = repo.get("full_name")
        url_commits = f"https://api.github.com/repos/{repo_name}/stats/contributors"
        
        try:
            r_commits = requests.get(url_commits, headers=headers).json()
            if r_commits:
                for contributor in r_commits:
                    if contributor.get('author', {}).get('login') == USERNAME:
                        total_commits += contributor.get('total', 0)
                        break
        except Exception as e:
            print(f"Commit error for repo {repo_name}: {e}")

# --- 5. HITUNG LINES OF CODE (LOC) ---
print("Calculating lines of code (added/deleted)...")
lines_added = 0
lines_deleted = 0
for repo in r_repos:
    if not repo.get("fork", False):
        repo_name = repo.get("full_name")
        url_loc = f"https://api.github.com/repos/{repo_name}/stats/code_frequency"
        try:
            r_loc = requests.get(url_loc, headers=headers).json()
            if isinstance(r_loc, list):
                for week in r_loc:
                    lines_added += week[1]
                    lines_deleted += abs(week[2])
        except Exception as e:
            print(f"LOC error for repo {repo_name}: {e}")

# --- 6. UPDATE FILE SVG ---
print("Updating SVG files...")
parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse("dark_mode.svg", parser)

def set_text_by_id(tid, value):
    el = tree.xpath(f"//*[@id='{tid}']")
    if el:
        el[0].text = str(value)

# Mengisi data ke SVG
set_text_by_id("age_data", calculate_age(BIRTH_DATE))
set_text_by_id("repo_data", public_repos)
set_text_by_id("star_data", stars)
set_text_by_id("follower_data", followers)
set_text_by_id("commit_data", total_commits)
set_text_by_id("loc_data", lines_added + lines_deleted)
set_text_by_id("loc_add", lines_added)
set_text_by_id("loc_del", lines_deleted)

tree.write("dark_mode.svg", pretty_print=True, encoding="utf-8", xml_declaration=True)
tree.write("light_mode.svg", pretty_print=True, encoding="utf-8", xml_declaration=True)

print("SVG files updated successfully!")
