# 📁 Advanced File Storage Bot (Telegram)

Pyrogram + MongoDB par based ek professional File Storage Bot — permanent links, unlimited storage,
admin panel, dashboard, force-subscribe, sab kuch included.

---

## 🗂 File Structure

```
FileStoreBot/
├── main.py                 # Entry point — bot yahin se start hota hai
├── config.py                # Saare environment variables yahan load hote hain
├── keep_alive.py            # Render ke liye tiny web server (24/7 uptime)
├── requirements.txt         # Python dependencies
├── Procfile                 # Render/Heroku start command
├── render.yaml               # Render one-click blueprint
├── .env.example              # Environment variables ka sample (isko .env bana lena LOCAL testing ke liye)
├── database/
│   └── db.py                 # MongoDB ke saare queries (users + files)
├── plugins/
│   ├── start.py               # /start, /help, /about, force-subscribe, file delivery
│   ├── upload.py               # File upload handler — link generate karta hai
│   ├── myfiles.py               # My Files, Search, Favorites, Recent, Stats
│   ├── admin.py                  # Admin panel — broadcast, ban, logs, etc.
│   └── callbacks.py               # Saare inline button clicks yahan handle hote hain
└── utils/
    └── helpers.py                 # human_size, uptime, link encode/decode, category detect
```

---

## ⚙️ Step 1 — Telegram Credentials Lena

1. **API_ID / API_HASH:** https://my.telegram.org → "API Development Tools" → app create karo.
2. **BOT_TOKEN:** Telegram par [@BotFather](https://t.me/BotFather) ko `/newbot` bhejo, token milega.
3. Bot ka **username** note kar lo (bina @ ke) — ye `BOT_USERNAME` env variable mein jayega.

## ⚙️ Step 2 — Private DB Channel Banana

Bot files ko ek **private Telegram channel** mein store karta hai (isse unlimited & permanent storage milti hai, free):

1. Ek naya **private channel** banao.
2. Apne bot ko us channel mein **admin** add karo.
3. Channel ka numeric ID nikalne ke liye, channel se koi bhi message forward karo [@userinfobot](https://t.me/userinfobot) ko — ID kuch aisi dikhegi: `-1001234567890`
4. Ye ID `DB_CHANNEL` env variable mein daalo.

## ⚙️ Step 3 — MongoDB Database

1. https://cloud.mongodb.com par free account banao.
2. Ek **free M0 cluster** create karo.
3. "Connect" → "Drivers" → connection string copy karo — ye `MONGO_URI` banega.
4. Database Access mein username/password set karo, Network Access mein `0.0.0.0/0` allow karo (sab IPs).

## ⚙️ Step 4 — Apna Telegram User ID Nikalna (Admin banne ke liye)

[@userinfobot](https://t.me/userinfobot) ko koi bhi message bhejo, wo tumhari numeric **user ID** bata dega.
Ye `ADMINS` env variable mein daalo (comma se multiple admins add kar sakte ho).

---

## 🐙 GitHub Par Upload Kaise Karein

1. GitHub par naya **repository** banao (e.g. `file-storage-bot`), public ya private — dono chalega.
2. Is poore `FileStoreBot` folder ko apne computer par download/copy karo.
3. Terminal mein folder ke andar jaake:

```bash
git init
git add .
git commit -m "Initial commit - File Storage Bot"
git branch -M main
git remote add origin https://github.com/<your-username>/file-storage-bot.git
git push -u origin main
```

**⚠️ Important:** `.env` file KABHI GitHub par push mat karna (usme secret tokens hote hain).
Isliye ek `.gitignore` file bhi add kar dena:

```
.env
__pycache__/
*.pyc
FileStoreBot.session
```

---

## ☁️ Render Par 24/7 Host Kaise Karein

1. https://render.com par account banao aur GitHub connect karo.
2. **New +** → **Web Service** → apni GitHub repo select karo.
3. Settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 main.py`
   - **Instance Type:** Free
4. **Environment Variables** section mein ye sab add karo (Step 1-4 se):

   | Key | Value |
   |---|---|
   | `API_ID` | apna API ID |
   | `API_HASH` | apna API hash |
   | `BOT_TOKEN` | BotFather se mila token |
   | `BOT_USERNAME` | bot ka username (bina @) |
   | `MONGO_URI` | MongoDB connection string |
   | `DB_NAME` | `FileStoreBot` |
   | `DB_CHANNEL` | private channel ki numeric ID |
   | `ADMINS` | apni user ID (comma separated for multiple) |
   | `FORCE_SUB_CHANNELS` | (optional) channel usernames comma se, warna khali chhod do |
   | `PORT` | `8080` |

5. **Create Web Service** click karo — Render apne aap build karke deploy kar dega.
6. Deploy ke baad Render tumhe ek **live URL** dega (e.g. `https://file-storage-bot.onrender.com`) —
   ye sirf keep-alive ping ke liye hai, isko koi separate uptime service (jaise UptimeRobot) se
   har 10-14 minute mein ping karwate raho taaki free plan par bot sound rahe.

7. **Auto Deploy:** Render by default GitHub ke `main` branch par har naye push par khud-ba-khud
   redeploy kar deta hai — koi extra setting nahi chahiye (render.yaml mein already configured hai).

---

## ✅ Bot Test Karna

1. Apne bot ko Telegram par open karke `/start` bhejo.
2. Koi bhi photo/video/PDF/ZIP/APK file bhejo — bot permanent link generate karega.
3. `/myfiles`, `/search <naam>`, `/favorites`, `/recent`, `/stats` try karo.
4. Admin ho to `/admin` bhejo — poora admin panel dikh jayega.

---

## 🧩 Features Included

**User:** `/start`, `/help`, `/about`, Welcome Message, Force Subscribe, Permanent File Link,
Unlimited Storage, Photo/Video/Audio/PDF/ZIP/RAR/APK/Any File Upload, File Preview, Instant Download,
My Files, Search, File Details, Delete, Rename, Favorites ⭐, Share, Recent Uploads, Categories.

**Admin:** Upload, Delete Any File, Search All Files, User List, Total Users/Files, Broadcast,
Ban/Unban, Admin Logs, Force Join Settings (via env var).

**Dashboard:** Total Users, Total Files, Storage Used, Today's Uploads, Online Users, Bot Uptime
(via `/stats` command).

**Hosting:** GitHub-ready, Render 24/7-ready, Environment Variables based config, Auto Deploy.

---

## 🔧 Notes / Extending

- Optional file expiry, inline "beautiful menu" logos, or a full web dashboard (separate Flask
  admin site) can be added on top of this — ping me if you want that built out too.
- Rename flow uses a simple in-memory pending-state dict; for multi-instance/horizontal scaling,
  move this to Mongo/Redis instead.
