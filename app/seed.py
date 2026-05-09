"""
Seed the skills table with all 27 calisthenics skills.
Runs once at startup — skips if already seeded.
Mirrors src/data/skillsData.js exactly.
"""
from app.database import SessionLocal
from app.models.skill import Skill

SKILLS_SEED = [
    # ── Beginner ──────────────────────────────────────────────────────────────
    {"skill_key": "pushups",          "name": "Push Ups",           "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/Pushups.png",           "requirements": ["Plank Hold — 20s", "Knee Push Ups — 10 reps", "Core Awareness — basic"]},
    {"skill_key": "squats",           "name": "Squats",             "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/Squats.png",            "requirements": ["Hip Mobility — basic", "Ankle Mobility — basic", "Bodyweight Balance — stable"]},
    {"skill_key": "dead-hang",        "name": "Dead Hang",          "category": "beginner",     "freq": "4x per week", "img_path": "/Assets/DeadHang.png",          "requirements": ["Grip Strength — basic", "Shoulder Awareness — basic"]},
    {"skill_key": "glute-bridge",     "name": "Glute Bridge",       "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/Glutebridge.png",       "requirements": ["Hip Hinge — basic", "Glute Activation — basic", "Core Control — basic"]},
    {"skill_key": "elbow-plank",      "name": "Elbow Plank",        "category": "beginner",     "freq": "4x per week", "img_path": "/Assets/Elbow pank.png",        "requirements": ["Core Awareness — basic", "Shoulder Stability — basic"]},
    {"skill_key": "hollow-body",      "name": "Hollow Body Hold",   "category": "beginner",     "freq": "4x per week", "img_path": "/Assets/Hollow body hold.png",  "requirements": ["Plank Hold — 30s", "Dead Bug — 10 reps", "Leg Raises — 10 reps"]},
    {"skill_key": "superman-hold",    "name": "Superman Hold",      "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/Superman hold.png",     "requirements": ["Back Extension — 10 reps", "Hip Hinge — basic", "Glute Activation — basic"]},
    {"skill_key": "tricep-dips",      "name": "Tricep Dips",        "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/TricepDips.png",        "requirements": ["Push Ups — 10 reps", "Shoulder Stability — basic", "Tricep Strength — basic"]},
    {"skill_key": "mountain-climbers","name": "Mountain Climbers",  "category": "beginner",     "freq": "3x per week", "img_path": "/Assets/MountainClimbers.png",  "requirements": ["Plank Hold — 30s", "Hip Flexor Mobility — basic", "Core Stability — basic"]},
    # ── Intermediate ─────────────────────────────────────────────────────────
    {"skill_key": "dips",             "name": "Dips",               "category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Dips.png",              "requirements": ["Tricep Dips — 15 reps", "Push Ups — 20 reps", "Shoulder Stability — good", "Straight Bar Support — 20s"]},
    {"skill_key": "pullups",          "name": "Pull Ups",           "category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Pullups.png",           "requirements": ["Dead Hang — 30s", "Australian Pull Ups — 10 reps", "Negative Pull Ups — 5 reps"]},
    {"skill_key": "australian-pulls", "name": "Australian Pull Ups","category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Austrailian Pulls.png", "requirements": ["Dead Hang — 20s", "Row Movement — basic", "Scapular Retraction — basic"]},
    {"skill_key": "hanging-knee",     "name": "Hanging Knee Raises","category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Hanging Knee Raises.png","requirements": ["Dead Hang — 30s", "Core Compression — basic", "Hip Flexor Strength — basic"]},
    {"skill_key": "jump-squats",      "name": "Jump Squats",        "category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Jump squats.png",       "requirements": ["Squats — 20 reps", "Ankle Stability — good", "Landing Mechanics — basic"]},
    {"skill_key": "lsit",             "name": "L-Sit",              "category": "intermediate", "freq": "4x per week", "img_path": "/Assets/L-sit.png",             "requirements": ["Support Hold — 30s", "Hollow Body Hold — 40s", "Knee Raises — 15 reps", "Tuck L-Sit — 10s"]},
    {"skill_key": "dragon-flag",      "name": "Dragon Flag",        "category": "intermediate", "freq": "3x per week", "img_path": "/Assets/Dragon Flag.png",       "requirements": ["Hollow Body Hold — 45s", "Hanging Knee Raises — 15 reps", "Leg Raises — 12 reps", "Core Strength — good"]},
    # ── Advanced ─────────────────────────────────────────────────────────────
    {"skill_key": "handstand",        "name": "Handstand",          "category": "advanced",     "freq": "4x per week", "img_path": "/Assets/Handstand.png",         "requirements": ["Wall Handstand — 45s", "Pike Push Ups — 15 reps", "Shoulder Taps — 15 reps", "Kick Up — 5 reps"]},
    {"skill_key": "pistol-squats",    "name": "Pistol Squats",      "category": "advanced",     "freq": "3x per week", "img_path": "/Assets/Pistol squats.png",     "requirements": ["Squats — 30 reps", "Single Leg Balance — 30s", "Hip Flexor Mobility — good", "Jump Squats — 15 reps"]},
    {"skill_key": "front-lever",      "name": "Front Lever",        "category": "advanced",     "freq": "3x per week", "img_path": "/Assets/Front Lever.png",       "requirements": ["Pull Ups — 12 reps", "Tuck Lever — 10s", "Hollow Hold — 45s", "Dragon Flag — 5 reps"]},
    {"skill_key": "back-lever",       "name": "Back Lever",         "category": "advanced",     "freq": "3x per week", "img_path": "/Assets/Back Lever.png",        "requirements": ["Skin The Cat — 5 reps", "German Hang — 30s", "Pull Ups — 10 reps", "Tuck Back Lever — 10s"]},
    {"skill_key": "planche-lean",     "name": "Planche Lean",       "category": "advanced",     "freq": "4x per week", "img_path": "/Assets/Planche Lean.png",      "requirements": ["Push Ups — 30 reps", "Dips — 20 reps", "Tuck Planche — 5s", "Wrist Conditioning — good"]},
    {"skill_key": "ring-dips",        "name": "Ring Dips",          "category": "advanced",     "freq": "3x per week", "img_path": "/Assets/Ring Dips.png",         "requirements": ["Bar Dips — 20 reps", "Ring Support Hold — 20s", "Shoulder Stability — advanced"]},
    {"skill_key": "hspu",             "name": "Handstand Push Ups", "category": "advanced",     "freq": "3x per week", "img_path": "/Assets/HSPU.png",              "requirements": ["Handstand — 30s freestanding", "Pike Push Ups — 20 reps", "Wall HSPU — 5 reps"]},
    # ── Elite ─────────────────────────────────────────────────────────────────
    {"skill_key": "muscle-ups",       "name": "Muscle Ups",         "category": "elite",        "freq": "3x per week", "img_path": "/Assets/Muscle-ups.jpg",        "requirements": ["Dead Hang — 1 min", "Pull Ups — 12 reps", "Bar Dips — 25 reps", "High Pull Ups — 10 reps"], "badge": "HOT"},
    {"skill_key": "full-planche",     "name": "Full Planche",       "category": "elite",        "freq": "3x per week", "img_path": "/Assets/Full Planche.png",      "requirements": ["Planche Lean — 30s", "Straddle Planche — 5s", "Tuck Planche — 15s", "Straight Body Tension — advanced"]},
    {"skill_key": "one-arm-pushup",   "name": "One Arm Push Up",    "category": "elite",        "freq": "3x per week", "img_path": "/Assets/One arm pushups.png",   "requirements": ["Push Ups — 40 reps", "Archer Push Ups — 10 reps each side", "Core Stability — advanced", "Shoulder Strength — advanced"]},
    {"skill_key": "iron-cross",       "name": "Iron Cross",         "category": "elite",        "freq": "2x per week", "img_path": "/Assets/Iron cross.png",        "requirements": ["Ring Dips — 15 reps", "Ring Support Hold — 45s", "Ring Fly — partial range", "Straight Arm Strength — advanced"]},
    {"skill_key": "human-flag",       "name": "Human Flag",         "category": "elite",        "freq": "3x per week", "img_path": "/Assets/Human flag.png",        "requirements": ["Pull Ups — 15 reps", "Handstand — 30s", "Core Stability — elite", "Straight Arm Strength — elite"]},
]


def seed_skills():
    db = SessionLocal()
    try:
        existing = db.query(Skill).count()
        if existing > 0:
            return  # Already seeded

        for s in SKILLS_SEED:
            db.add(Skill(**s))
        db.commit()
        print(f"[seed] Seeded {len(SKILLS_SEED)} skills into the database.")
    except Exception as e:
        db.rollback()
        print(f"[seed] Error seeding skills: {e}")
    finally:
        db.close()
