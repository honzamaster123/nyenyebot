import tweepy
import time
import random
from datetime import datetime
import os

# --------------------------------------------------
#  =============== KONFIGURASI API ===============
# --------------------------------------------------

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEwvawEAAAAA48x7h9TUmO03p1DWXNeca1idYJs%3DqkLh2xwwW9fAAGi3goA9n2kj4SOZh9CaUyY1sSb76WEAgWzsTz"
API_KEY = "c1VvzfhWsMYHiT9t9y7MMKGMc"
API_SECRET = "mcaZNlj8UWObae7lOCICAGdQPPCX0t2zip3JV1WtYuRZMYYtyq"
ACCESS_TOKEN = "1504365905111035905-YuzXxZkS7Fp9PKuQ5WkzH7Upvf2p6v"
ACCESS_TOKEN_SECRET = "iAwbusG6H3mkw6PqtnkfML60K63ewGHVRnnSCBJoiom3H"
USERNAME_BOT = "dixpyc"  # tanpa '@'

# --------------------------------------------------
#  ========= SISTEM FILE QUEUE & LAST ID ==========
# --------------------------------------------------

QUEUE_FILE = "queue.txt"
LAST_ID_FILE = "last_id.txt"

if not os.path.exists(QUEUE_FILE):
    open(QUEUE_FILE, "w").close()

if not os.path.exists(LAST_ID_FILE):
    open(LAST_ID_FILE, "w").close()

# --------------------------------------------------
#  ================ TEXT PROCESSOR ================
# --------------------------------------------------

def ubah_vokal(teks):
    vokal = "aiueoAIUEO"
    hasil = ""
    for c in teks:
        if c in vokal:
            hasil += "i" if c.islower() else "I"
        else:
            hasil += c
    return hasil

def random_caps(teks):
    out = ""
    for c in teks:
        if c.isalpha():
            out += c.upper() if random.random() < 0.5 else c.lower()
        else:
            out += c
    return out

def proses_teks_full(teks):
    return random_caps(ubah_vokal(teks))


# --------------------------------------------------
#  ================= QUEUE SYSTEM =================
# --------------------------------------------------

def add_to_queue(username, user_id, original_id, text):
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        entry = {
            "username": username,
            "user_id": user_id,
            "tweet_id": original_id,
            "text": text
        }
        f.write(json.dumps(entry) + "\n")
    print(f"[QUEUE] Ditambahkan → @{username} : {text[:30]}...")

def pop_queue():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return None

    first = json.loads(lines[0])

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines[1:])

    return first


# --------------------------------------------------
#  ================ LAST ID SYSTEM ================
# --------------------------------------------------

def get_last_seen_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            data = f.read().strip()
            return int(data) if data else None
    except:
        return None

def set_last_seen_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))


# --------------------------------------------------
#  =================== AUTH API ===================
# --------------------------------------------------

client_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
client_v1 = tweepy.API(auth)


# --------------------------------------------------
#  ========= CEK MENTIONS SETIAP 10 MENIT =========
# --------------------------------------------------

def check_mentions():
    print("[SCAN] Mengecek mentions...")

    last_id = get_last_seen_id()

    try:
        mentions = client_v2.get_users_mentions(
            id=client_v2.get_me().data.id,
            since_id=last_id,
            max_results=10,
            tweet_fields=["author_id", "referenced_tweets", "text"]
        )

    except tweepy.TooManyRequests:
        print("[LIMIT] get_users_mentions 429 → skip satu siklus")
        return

    except Exception as e:
        print("[ERROR] Mention:", e)
        return

    if not mentions.data:
        print("[SCAN] Tidak ada mentions baru.")
        return

    for m in reversed(mentions.data):
        teks = m.text
        user_id = m.author_id
        username = client_v2.get_user(id=user_id).data.username

        # jika mention adalah reply → ambil parent
        if m.referenced_tweets:
            ref = m.referenced_tweets[0]
            if ref.type == "replied_to":
                try:
                    parent = client_v2.get_tweet(ref.id, tweet_fields=["text"])
                    teks = parent.data.text
                except:
                    pass

        hasil = proses_teks_full(teks)
        add_to_queue(username, user_id, m.id, hasil)
        set_last_seen_id(m.id)


# --------------------------------------------------
#  ================= POST QUEUE ===================
# --------------------------------------------------

def process_queue():
    item = pop_queue()
    if not item:
        return

    username = item["username"]
    teks = item["text"]
    tweet_id = item["tweet_id"]

    tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
    final_post = f"@{username} {teks}\n\nSource: {tweet_url}"

    try:
        client_v1.update_status(final_post)
        print(f"[POSTED] → @{username} : {teks[:30]}...")

    except tweepy.RateLimitError:
        print("[LIMIT POST] Posting 429 → skip siklus, tidak retry")

    except Exception as e:
        print("[ERROR] Post:", e)


# --------------------------------------------------
#  ======== MAIN LOOP 10 MENIT (600 DETIK) ========
# --------------------------------------------------

print("=== BOT TWITTER/X AKTIF (INTERVAL 10 MENIT, NO FALLBACK) ===\n")

while True:
    check_mentions()
    process_queue()
    print("[WAIT] 600 detik (10 menit)...\n")
    time.sleep(600)
