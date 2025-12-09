🐙 Mention-Reply Bot



   

> A tiny, silly bot that replies to mentions by turning all vowels into i and playing caps roulette. Perfect for chaos, pranks, or just a little Twitter/X mischief. 🎲💬


example:

![example.png](example.png)

---

✨ Features

Automatically fetches the original tweet text (uses parent tweet if the mention is a reply)

Converts all vowels → i (preserves case as i / I)

Randomizes capitalization for other letters (caps roulette!)

Simple queueing via last_id.txt, built-in logging to console

Ready for deployment on Railway and Heroku

Lightweight and easy to customize



---

📁 What’s included

app.py — main bot script (your provided script)

requirements.txt — dependencies

Procfile — for Heroku/Procfile-compatible platforms


---

🚀 Quick look — important snippet (Procfile)

worker: python app.py


---

🛠️ Installation (local)

> Run locally to test before pushing to Railway / Heroku.



1. Clone your repo (or create one):



git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Create & activate a virtual environment (recommended):



python -m venv .venv
# mac / linux
source .venv/bin/activate
# windows (powershell)
.venv\Scripts\Activate.ps1

3. Install dependencies:



pip install -r requirements.txt

> Tip: consider adding python-dotenv for local .env handling, and add it to requirements.txt if you use it.



---

⚙️ Configuration (ENV vars)

Do NOT hardcode API keys in the repo. Use environment variables.

Create a file named .env.example (DO NOT commit your real .env):

BEARER_TOKEN=your_bearer_token_here
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
ACCESS_TOKEN=your_access_token_here
ACCESS_TOKEN_SECRET=your_access_token_secret_here
USERNAME_BOT=dixpyc

Set the real values in your environment (or use Railway / Heroku config vars / secrets).

Important: Remove any hard-coded tokens from app.py — instead read them from os.environ:

import os

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
USERNAME_BOT = os.getenv("USERNAME_BOT", "dixpyc")


---

▶️ Usage (run locally)

# make sure env vars are set, then:
python app.py

You should see colorful console logs like:

=== BOT TWITTER/X AKTIF (INTERVAL 2 MENIT) ===
[SCAN] Memindai mention terbaru...
[READY] Siap membalas @randomuser dengan teks: i WiNNi...
[REPLY SENT] Berhasil membalas @randomuser
[WAIT] Istirahat selama 120 detik...


---

📦 Deployment — Railway (step-by-step)

Railway is super convenient for running background workers.

1. Create GitHub repo and push your code:



git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main

2. Create Railway account (if you don't have one) and log in.


3. New Project → Deploy from GitHub

Choose your repo.

Railway will detect the project and create a service.



4. Configure service

If Railway asks: set the Start Command to python app.py (or choose Worker type if available).

Set the Port only if you run a web service (not needed for a pure worker).

Set the Env Variables (in Railway: Variables / Secrets) with the exact names from .env.example and your real values.



5. Deploy

Trigger a deploy (Railway will build and run python app.py).

Check the Logs tab — you’ll see the same console output as local.



6. Scale / Stop

To stop the worker, set replicas to 0 or suspend the deployment from the service settings.





---

🪄 Deployment — Heroku (quick)

1. Create app on Heroku dashboard.


2. In your repo include Procfile:



worker: python app.py

3. Set Config Vars on Heroku (Settings → Config Vars) using the same env names as .env.example.


4. Deploy via GitHub integration or git push heroku main.


5. Scale the worker on Heroku:



heroku ps:scale worker=1 --app your-app-name

To stop the bot:

heroku ps:scale worker=0 --app your-app-name


---

🧰 Notes, suggestions & improvements

Security: Remove all API keys from app.py — keep them only in env vars / Railway / Heroku settings.

Logging: Consider replacing print with Python’s logging module for leveled logs and file handlers.

Rate-limits: The script uses wait_on_rate_limit=True but you should add better error handling and exponential backoff.

Graceful shutdown: Catch KeyboardInterrupt and clean up before exit.

Queue/backup: last_id.txt keeps a simple pointer to avoid double replies. For more reliable queueing use a DB (Redis / PostgreSQL).

Optional deps: python-dotenv for local env loading, gunicorn only if you later serve a web endpoint.



---

❓ FAQ

Q: Why does the bot sometimes reply with gibberish or short text?
A: If the parent tweet can't be retrieved, the bot falls back to the mention text. Also tweets with links or media can shorten visible text.

Q: Can I change the vowel replacement or randomness?
A: Yep — edit ubah_vokal or random_caps functions inside app.py.

Q: Is this allowed by Twitter/X rules?
A: Be mindful of platform rules and rate limits — avoid spamming and respect user privacy.


---

🧾 License

This project is released under the MIT License — feel free to tweak and remix. ❤️


---
