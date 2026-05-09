# CaliStrength Backend — Full Setup Guide

## What you have now
- FastAPI backend with Firebase + Email/Password auth
- MySQL database with all tables
- Updated React auth pages wired to the real backend

---

## STEP A — Firebase Console Setup (5 minutes)

1. Go to https://console.firebase.google.com
2. Click **Add project** → name it `CaliStrength` → Continue
3. Disable Google Analytics (not needed) → Create project

### Enable Authentication providers
4. In left sidebar → **Build → Authentication → Get started**
5. Click **Sign-in method** tab
6. Enable **Email/Password** → Save
7. Enable **Google** → set your support email → Save

### Get your web app config (for React)
8. Project Overview → click the **</>** (Web) icon → Register app → name it `calistrength-web`
9. Copy the `firebaseConfig` object — you'll need these values for `.env.local`

### Get your service account key (for Python backend)
10. Project Settings (gear icon) → **Service accounts** tab
11. Click **Generate new private key** → Download the JSON file
12. Rename it `firebase-service-account.json`
13. Place it in your `calistrength-backend/` folder

---

## STEP B — MySQL Setup (2 minutes)

Open MySQL Workbench or your terminal and run:

```sql
CREATE DATABASE calistrength CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

That's it — FastAPI will create all tables automatically on first run.

---

## STEP C — Backend Setup

```bash
# 1. Go into the backend folder
cd calistrength-backend

# 2. Create a Python virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Fill in your .env file
# Open .env and set:
#   DB_PASSWORD=your actual MySQL password
#   APP_SECRET_KEY=any long random string (32+ chars)
#   FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

# 5. Start the server
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see all your API routes with a live test UI.

---

## STEP D — React Frontend Setup

```bash
# 1. Go into your React project
cd Cali-React

# 2. Install Firebase SDK
npm install firebase

# 3. Create .env.local file (copy from the template)
cp .env.local.example .env.local
# Then fill in your Firebase config values from Step A

# 4. Copy the updated files from REACT_FILES/ into your src/:
#   REACT_FILES/src/lib/api.js          → src/lib/api.js          (new file)
#   REACT_FILES/src/lib/firebase.js     → src/lib/firebase.js     (new file)
#   REACT_FILES/src/pages/auth/LoginPage.jsx   → replace existing
#   REACT_FILES/src/pages/auth/SignupPage.jsx  → replace existing
#   REACT_FILES/src/components/ui/ProtectedRoute.jsx → replace existing
#   REACT_FILES/.env.local.example      → .env.local (fill in values)

# 5. Start React
npm run dev
```

---

## How auth flows work

### Google login
```
User clicks "Continue with Google"
  → Firebase opens Google popup
  → Google verifies and returns Firebase token
  → Your backend receives token at POST /auth/firebase
  → Backend verifies token with Firebase Admin SDK
  → User is found-or-created in MySQL
  → Backend returns YOUR JWT token
  → React stores JWT, redirects to app or onboarding
```

### Email/Password signup
```
User fills name + email + password → clicks Create Account
  → React calls POST /auth/signup on your backend
  → Backend hashes password, stores user in MySQL
  → Backend returns YOUR JWT token
  → React stores JWT, redirects to onboarding
```

### Email/Password login
```
User fills email + password → clicks Sign In
  → Firebase verifies credentials (signInWithEmailAndPassword)
  → Firebase returns ID token
  → Your backend verifies ID token at POST /auth/firebase
  → Returns YOUR JWT token
  → React stores JWT, redirects to dashboard
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `CORS error` | Make sure `FRONTEND_URL=http://localhost:5173` in `.env` |
| `Firebase token invalid` | Check `firebase-service-account.json` path in `.env` |
| `Can't connect to MySQL` | Check `DB_PASSWORD` and that MySQL is running |
| `Module not found` | Run `pip install -r requirements.txt` again in the venv |
| Google popup blocked | Allow popups for localhost in browser settings |

---

## What's next (Step 3)

Once auth is working, next we build:
- `POST /workouts/session` — save completed workouts
- `GET /workouts/history` — load workout history
- `POST /skills/{id}/start` — start training a skill
- `GET /skills/user` — get user's ongoing + mastered skills
- All the progress, weight, and PR endpoints
