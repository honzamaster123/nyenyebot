import tweepy
import time
import random
from datetime import datetime
import os

# ======== Konfigurasi API (langsung di sini) ========
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEE%2BawEAAAAACCoslwkWGtWLwXCBwWvAVN3vvl4%3DwcpKnLbHJZJShH1b2O9wXeJiNIebyQPaamq47IjgqKtIZO0WnO"
API_KEY = "WTabYMJnQ4A7bmhCd25iu1PCj"
API_SECRET = "azfV03WWpHFgEGIC7RXMzczQgMEMtIKvEGQHMpDScbtW7xud7j"
ACCESS_TOKEN = "1504365905111035905-JFqPbuEb7TlpwLLXcBpHsmcHAOQSHW"
ACCESS_TOKEN_SECRET = "rbugFTxZB0QY5nVJaxxz0YqNeRqqldafNN5DclrW7Zbc8"

# OAuth1 untuk posting tweet
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Client v2 untuk baca mention
client_v2 = tweepy.Client(bearer_token=BEARER_TOKEN)

# ======== Folder & file ========
BASE_FOLDER = "queue_bot"
os.makedirs(BASE_FOLDER, exist_ok=True)
QUEUE_FILE = os.path.join(BASE_FOLDER, "queue.txt")
LOG_FILE = os.path.join(BASE_FOLDER, "log.txt")
LAST_SEEN_FILE = os.path.join(BASE_FOLDER, "last_seen_id.txt")

for f in [QUEUE_FILE, LOG_FILE, LAST_SEEN_FILE]:
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

# ======== Queue ========
def add_to_queue(username, user_id, tweet_id, teks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}|{username}|{user_id}|{tweet_id}|{teks}\n")

def log_post(status, username, user_id, tweet_id, teks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}|{status}|{username}|{user_id}|{tweet_id}|{teks}\n")

# ======== Last seen ========
def get_last_seen_id():
    with open(LAST_SEEN_FILE, "r") as f:
        val = f.read().strip()
        return int(val) if val else 0

def set_last_seen_id(tweet_id):
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(str(tweet_id))

# ======== Ambil mention baru via v2 ========
def check_mentions():
    last_seen_id = get_last_seen_id()
    try:
        mentions = client_v2.get_users_mentions(
            id=client_v2.get_me().data.id,
            since_id=last_seen_id,
            max_results=20,
            tweet_fields=["referenced_tweets"]
        )
        if not mentions.data:
            return
        for mention in reversed(mentions.data):
            tweet_id = mention.id
            user_id = mention.author_id
            username = client_v2.get_user(id=user_id).data.username

            # Ambil teks tweet asli jika reply
            teks_asli = mention.text
            if mention.referenced_tweets:
                ref = mention.referenced_tweets[0]
                if ref.type == "replied_to":
                    try:
                        parent_tweet = client_v2.get_tweet(ref.id, tweet_fields=["text"])
                        teks_asli = parent_tweet.data.text
                    except:
                        pass

            teks_baru = ubah_vokal_dan_random_caps(teks_asli)
            add_to_queue(username, user_id, tweet_id, teks_baru)
            set_last_seen_id(tweet_id)
    except Exception as e:
        print(f"[ERROR] Gagal cek mentions: {e}")

# ======== Proses queue (posting baru) ========
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
                timestamp, username, user_id, tweet_id, teks = line.split("|", 4)
                postingan = f"@{username} {teks}\nLink asli: https://twitter.com/i/web/status/{tweet_id}"
                api.update_status(postingan)
                print(f"[OK] Berhasil posting @{username}")
                log_post("SUCCESS", username, user_id, tweet_id, teks)
                batch_count += 1
                time.sleep(random.uniform(1,3))
            except Exception as e:
                print(f"[ERROR] Gagal posting @{username}: {e}")
                new_lines.append(line)
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            for l in new_lines:
                f.write(l + "\n")
    except Exception as e:
        print(f"[ERROR] Proses queue gagal: {e}")

# ======== Loop utama ========
print("[START] Bot berjalan...")
while True:
    try:
        check_mentions()
        process_queue(max_batch=5)
    except Exception as e:
        print(f"[ERROR] Loop utama: {e}")
    time.sleep(20)
