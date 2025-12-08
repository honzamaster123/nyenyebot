import tweepy
import os
import time
from datetime import datetime, timedelta
import shutil
import random

# ======== Konfigurasi API dari environment variable ========
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=False)

# ======== Folder & file ========
BASE_FOLDER = "queue_bot"
os.makedirs(BASE_FOLDER, exist_ok=True)
QUEUE_FILE = os.path.join(BASE_FOLDER, "queue.txt")
LOG_FILE = os.path.join(BASE_FOLDER, "log.txt")
BACKUP_FOLDER = os.path.join(BASE_FOLDER, "backup")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

for f in [QUEUE_FILE, LOG_FILE]:
    if not os.path.exists(f):
        open(f, "w", encoding="utf-8").close()

# ======== Fungsi ubah vokal + random kapitalisasi ========
def ubah_vokal_dan_random_caps(teks):
    vokal = "aiueoAIUEO"
    hasil = ""
    for c in teks:
        if c in vokal:
            c = 'i'
        if c.isalpha():
            c = c.upper() if random.choice([True, False]) else c.lower()
        hasil += c
    return hasil

# ======== Tambahkan mention ke queue ========
def add_to_queue(tweet_id, username, user_id, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}|{tweet_id}|{username}|{user_id}|{text}\n")
        print(f"[QUEUE] Ditambahkan @{username}")
    except Exception as e:
        print(f"[ERROR] Gagal menambah queue: {e}")

# ======== Log ========
def log_reply(status, tweet_id, username, user_id, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}|{status}|{tweet_id}|{username}|{user_id}|{text}\n")
    except Exception as e:
        print(f"[ERROR] Gagal menulis log: {e}")

# ======== Backup queue ========
def backup_queue():
    try:
        if os.path.exists(QUEUE_FILE):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"queue_{timestamp}.txt")
            shutil.copy2(QUEUE_FILE, backup_file)
            print(f"[BACKUP] Queue dibackup: {backup_file}")
    except Exception as e:
        print(f"[ERROR] Backup gagal: {e}")

# ======== Proses queue ========
def process_queue(max_batch=5):
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        batch_count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if batch_count >= max_batch:
                new_lines.append(line)
                continue
            try:
                timestamp, tweet_id, username, user_id, text = line.split("|", 4)
                api.update_status(
                    status=f"@{username} {text}",
                    in_reply_to_status_id=int(tweet_id)
                )
                print(f"[OK] Berhasil reply @{username}")
                log_reply("SUCCESS", tweet_id, username, user_id, text)
                batch_count += 1
                time.sleep(random.uniform(1,3))
            except tweepy.TweepyException as e:
                print(f"[LIMIT] Masih limit, tetap di queue @{username}: {e}")
                new_lines.append(line)
                log_reply("FAILED_LIMIT", tweet_id, username, user_id, text)
                break
            except Exception as e:
                print(f"[ERROR] {e}, hapus baris rusak @{username}")
                log_reply("FAILED_ERROR", tweet_id, username, user_id, text)

        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            for l in new_lines:
                f.write(l + "\n")
    except Exception as e:
        print(f"[ERROR] Proses queue gagal: {e}")

# ======== Ambil mention baru ========
last_seen_id = 1
def check_mentions():
    global last_seen_id
    try:
        mentions = api.mentions_timeline(since_id=last_seen_id, tweet_mode="extended")
        for mention in reversed(mentions):
            last_seen_id = mention.id
            parent_id = mention.in_reply_to_status_id
            if not parent_id:
                continue
            try:
                parent = api.get_status(parent_id, tweet_mode="extended")
                hasil = ubah_vokal_dan_random_caps(parent.full_text)
                add_to_queue(mention.id, mention.user.screen_name, mention.user.id_str, hasil)
            except Exception as e:
                print(f"[ERROR] Gagal ambil tweet parent @{mention.user.screen_name}: {e}")
    except Exception as e:
        print(f"[ERROR] Gagal cek mention: {e}")

# ======== Loop utama ========
backup_timer = datetime.now()
print("[START] Bot berjalan...")
while True:
    try:
        check_mentions()
        process_queue(max_batch=5)
        if datetime.now() - backup_timer > timedelta(hours=1):
            backup_queue()
            backup_timer = datetime.now()
    except Exception as e:
        print(f"[ERROR] Loop utama: {e}")
    time.sleep(20)
