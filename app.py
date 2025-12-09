import tweepy
import time
import random
from datetime import datetime
import os

# ==================================================
#  =================  WARNA ANSI  =================
# ==================================================

W = "\033[0m"   # reset
R = "\033[91m"  # merah
G = "\033[92m"  # hijau
Y = "\033[93m"  # kuning
B = "\033[94m"  # biru
C = "\033[96m"  # cyan
P = "\033[95m"  # ungu

# ==================================================
# ===============  KONFIGURASI API  ================
# ==================================================

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEwvawEAAAAA48x7h9TUmO03p1DWXNeca1idYJs%3DqkLh2xwwW9fAAGi3goA9n2kj4SOZh9CaUyY1sSb76WEAgWzsTz"
API_KEY = "c1VvzfhWsMYHiT9t9y7MMKGMc"
API_SECRET = "mcaZNlj8UWObae7lOCICAGdQPPCX0t2zip3JV1WtYuRZMYYtyq"
ACCESS_TOKEN = "1504365905111035905-YuzXxZkS7Fp9PKuQ5WkzH7Upvf2p6v"
ACCESS_TOKEN_SECRET = "iAwbusG6H3mkw6PqtnkfML60K63ewGHVRnnSCBJoiom3H"

USERNAME_BOT = "dixpyc"  # tanpa '@'

# ==================================================
#  =============== FILE LAST SEEN ID ==============
# ==================================================

LAST_ID_FILE = "last_id.txt"

if not os.path.exists(LAST_ID_FILE):
    open(LAST_ID_FILE, "w").close()

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


# ==================================================
# ================  TEXT PROCESSOR  ================
# ==================================================

def ubah_vokal(teks):
    vokal = "aiueoAIUEO"
    out = ""
    for c in teks:
        if c in vokal:
            out += "i" if c.islower() else "I"
        else:
            out += c
    return out

def random_caps(teks):
    result = ""
    for c in teks:
        if c.isalpha():
            result += c.upper() if random.random() < 0.5 else c.lower()
        else:
            result += c
    return result

def proses_teks(teks):
    return random_caps(ubah_vokal(teks))


# ==================================================
# ===================== AUTH =======================
# ==================================================

client_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
client_v1 = tweepy.API(auth, wait_on_rate_limit=True)


# ==================================================
# ===============  SCAN MENTIONS  ==================
# ==================================================

def check_mentions():
    print(f"{B}[SCAN]{W} Memindai mention terbaru...")

    last_id = get_last_seen_id()

    try:
        mentions = client_v2.get_users_mentions(
            id=client_v2.get_me().data.id,
            since_id=last_id,
            max_results=10,
            tweet_fields=["author_id", "referenced_tweets", "text"]
        )
    except Exception as e:
        print(f"{R}[ERROR]{W} Gagal mengambil mentions:", e)
        return None

    if not mentions.data:
        print(f"{Y}[INFO]{W} Tidak ada mention baru.")
        return None

    results = []

    for m in reversed(mentions.data):
        user = client_v2.get_user(id=m.author_id)
        username = user.data.username
        teks = m.text

        # Jika ini reply, gunakan isi tweet parent
        if m.referenced_tweets:
            ref = m.referenced_tweets[0]
            if ref.type == "replied_to":
                try:
                    parent = client_v2.get_tweet(ref.id, tweet_fields=["text"])
                    teks = parent.data.text
                    print(f"{C}[INFO]{W} Mention dari @{username} adalah reply → teks parent digunakan.")
                except:
                    print(f"{Y}[WARN]{W} Tidak dapat mengambil teks parent, gunakan teks mention.")

        hasil = proses_teks(teks)

        results.append({
            "username": username,
            "reply_to": m.id,
            "text": hasil
        })

        print(f"{G}[READY]{W} Siap membalas @{username} dengan teks: {hasil[:40]}...")

        set_last_seen_id(m.id)

    return results


# ==================================================
# ===================  POST REPLY  =================
# ==================================================

def reply_to_tweet(data):
    username = data["username"]
    reply_to = data["reply_to"]
    teks = data["text"]

    final = f"@{username} {teks}"

    try:
        client_v1.update_status(
            status=final,
            in_reply_to_status_id=reply_to,
            auto_populate_reply_metadata=True
        )
        print(f"{G}[REPLY SENT]{W} Berhasil membalas @{username}")
    except Exception as e:
        print(f"{R}[ERROR]{W} Gagal mengirim balasan:", e)


# ==================================================
#  =================== MAIN LOOP ==================
# ==================================================

print(f"{P}=== BOT TWITTER/X AKTIF (INTERVAL 2 MENIT) ==={W}\n")

while True:
    mentions = check_mentions()

    if mentions:
        for item in mentions:
            reply_to_tweet(item)

    print(f"{C}[WAIT]{W} Istirahat selama 120 detik...\n")
    time.sleep(120)
