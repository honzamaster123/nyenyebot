import tweepy
import time
import random
from datetime import datetime
import os

# ======== Konfigurasi API (langsung di sini) ========
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEwvawEAAAAA48x7h9TUmO03p1DWXNeca1idYJs%3DqkLh2xwwW9fAAGi3goA9n2kj4SOZh9CaUyY1sSb76WEAgWzsTz"
API_KEY = "c1VvzfhWsMYHiT9t9y7MMKGMc"
API_SECRET = "mcaZNlj8UWObae7lOCICAGdQPPCX0t2zip3JV1WtYuRZMYYtyq"
ACCESS_TOKEN = "1504365905111035905-YuzXxZkS7Fp9PKuQ5WkzH7Upvf2p6v"
ACCESS_TOKEN_SECRET = "iAwbusG6H3mkw6PqtnkfML60K63ewGHVRnnSCBJoiom3H"

USERNAME_BOT = "dixpyc"  # tanpa '@'

QUEUE_FILE = "queue.txt"
LAST_ID_FILE = "last_id.txt"

# ==========================================================
#     AUTH V1 (Posting Tweet)
# ==========================================================
auth = tweepy.OAuth1UserHandler(
    API_KEY,
    API_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)
api_v1 = tweepy.API(auth)

# ==========================================================
#     AUTH V2 (Mention Checker)
# ==========================================================
client_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=False
)

# ----------------------------------------------------------
#  Fungsi Random Huruf Kapital + Ubah Vokal ke "i"
# ----------------------------------------------------------
def ubah_vokal_random_caps(teks):
    hasil = ""
    for ch in teks:
        if ch.lower() in ["a", "i", "u", "e", "o"]:
            ch = "i"
        if random.random() > 0.5:
            ch = ch.upper()
        else:
            ch = ch.lower()
        hasil += ch
    return hasil

# ----------------------------------------------------------
#  Utility: Queue System
# ----------------------------------------------------------
def add_to_queue(username, user_id, tweet_id, processed_text, original_url):
    with open(QUEUE_FILE, "a", encoding="utf8") as f:
        f.write(f"{username}|{user_id}|{tweet_id}|{processed_text}|{original_url}\n")

def read_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def remove_first_queue():
    lines = read_queue()
    if not lines:
        return
    with open(QUEUE_FILE, "w", encoding="utf8") as f:
        f.writelines(lines[1:])

# ----------------------------------------------------------
#  Save & Load last seen ID
# ----------------------------------------------------------
def get_last_seen_id():
    if not os.path.exists(LAST_ID_FILE):
        return None
    try:
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

def set_last_seen_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))

# ----------------------------------------------------------
#  STEP 1 — Cek Mention via Endpoint Mentions
# ----------------------------------------------------------
def check_mentions_primary():
    print("[INFO] Cek mentions (primary)...")

    try:
        last_id = get_last_seen_id()
        me = client_v2.get_me().data.id

        mentions = client_v2.get_users_mentions(
            id=me,
            since_id=last_id,
            max_results=10,
            tweet_fields=["referenced_tweets"]
        )

        if not mentions.data:
            return False  # tidak ada data baru

        for mention in reversed(mentions.data):
            t_id = mention.id
            u_id = mention.author_id
            username = client_v2.get_user(id=u_id).data.username

            teks_asli = mention.text

            # ambil tweet yg direply
            if mention.referenced_tweets:
                ref = mention.referenced_tweets[0]
                if ref.type == "replied_to":
                    parent = client_v2.get_tweet(ref.id, tweet_fields=["text"])
                    teks_asli = parent.data.text

            hasil = ubah_vokal_random_caps(teks_asli)
            tweet_url = f"https://twitter.com/{username}/status/{t_id}"

            add_to_queue(username, u_id, t_id, hasil, tweet_url)
            set_last_seen_id(t_id)

        return True

    except tweepy.TooManyRequests:
        print("[429] Limit endpoint mentions — switching to fallback search...")
        return None

    except Exception as e:
        print(f"[ERROR] Mentions primary gagal: {e}")
        return None

# ----------------------------------------------------------
#  STEP 2 — Fallback Search API
# ----------------------------------------------------------
def check_mentions_fallback():
    print("[INFO] Cek mentions (fallback search)...")

    try:
        query = f"@{USERNAME_BOT} -is:retweet"
        tweets = client_v2.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=["referenced_tweets", "author_id"]
        )

        if not tweets.data:
            return False

        for tw in reversed(tweets.data):
            t_id = tw.id
            u_id = tw.author_id
            username = client_v2.get_user(id=u_id).data.username

            teks_asli = tw.text

            if tw.referenced_tweets:
                ref = tw.referenced_tweets[0]
                if ref.type == "replied_to":
                    parent = client_v2.get_tweet(ref.id, tweet_fields=["text"])
                    teks_asli = parent.data.text

            hasil = ubah_vokal_random_caps(teks_asli)
            tweet_url = f"https://twitter.com/{username}/status/{t_id}"

            add_to_queue(username, u_id, t_id, hasil, tweet_url)

        return True

    except Exception as e:
        print(f"[ERROR] Search fallback gagal: {e}")
        return False

# ----------------------------------------------------------
#  STEP 3 — Posting Queue
# ----------------------------------------------------------
def process_queue():
    q = read_queue()
    if not q:
        return

    item = q[0]
    username, uid, tid, teks, url = item.split("|", 4)

    final_text = f"@{username} {teks}\n\nOriginal Tweet:\n{url}"

    try:
        api_v1.update_status(final_text)
        print(f"[POSTED] Balasan terkirim ke @{username}")
        remove_first_queue()
        time.sleep(3)
    except tweepy.TweepyException as e:
        if "429" in str(e):
            print("[429] Limit posting — tunggu 2 menit...")
            time.sleep(120)
        else:
            print(f"[ERROR POST] {e}")

# ----------------------------------------------------------
#  MAIN LOOP
# ----------------------------------------------------------
print("BOT BERJALAN — Anti 429 Mode Aktif")

while True:
    # Step 1: coba primary mentions
    result = check_mentions_primary()

    # Step 2: fallback jika limit atau gagal
    if result is None:
        check_mentions_fallback()

    # Step 3: proses queue
    process_queue()

    print("[INFO] Sleep 120 detik...")
    time.sleep(120)
