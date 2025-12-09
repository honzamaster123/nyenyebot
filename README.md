# 🐙 **Mention Reply Bot**


[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Deploy on Railway](https://img.shields.io/badge/deploy-railway-purple)](#deploy-to-railway)
[![Deploy on Heroku](https://img.shields.io/badge/deploy-heroku-663399.svg)](#deploy-to-heroku)

> A tiny chaotic bot that replies to Twitter/X mentions by converting every vowel into **“i”** and randomizing capitalization.  

---

## ✨ Features

- Automatically replies to mentions  
- Fetches parent tweet text if the mention is a reply  
- Converts **all vowels → `i`** (`I` for uppercase)  
- Randomizes capitalization  
- Built-in simple queue system  
- Ready for Railway & Heroku deployment  

---

## 📁 Included Files

```
app.py
requirements.txt
Procfile
```

---

## 🚀 Installation (Local)

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create `.env`:

```env
BEARER_TOKEN=your_token_here
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
ACCESS_TOKEN=your_access_token_here
ACCESS_TOKEN_SECRET=your_access_token_secret_here
USERNAME_BOT=your_username_bot_without_@
```

Modify `app.py`:

```python
import os

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
USERNAME_BOT = os.getenv("USERNAME_BOT")
```

---

## ▶️ Run Locally

```bash
python app.py
```

---

# 🛤️ Deploy to Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 2. Railway → New Project → Deploy from GitHub  
### 3. Add Variables `app.py`:

```
BEARER_TOKEN=your_token_here
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
ACCESS_TOKEN=your_access_token_here
ACCESS_TOKEN_SECRET=your_access_token_secret_here
USERNAME_BOT=your_username_bot_without_@
```

### 4. Set Start Command:

```
python app.py
```

### 5. Check Logs to confirm running  
### 6. To stop: scale replicas to **0** or suspend.

---

# ☁️ Deploy to Heroku

Ensure `Procfile` exists:

```
worker: python app.py
```

Add config vars, then:

```bash
git push heroku main
heroku ps:scale worker=1
```

Stop:

```bash
heroku ps:scale worker=0
```

---

## 📸 Screenshot

![banner](example.png)

---

## 🧾 License

This project is released under the MIT License — feel free to tweak and remix❤️

---

## 🙌 Credits

Crafted with chaos & love.
