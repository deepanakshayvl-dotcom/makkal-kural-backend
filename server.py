from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import random
import string
from bson import ObjectId
import base64
from constituencies import TAMIL_NADU_CONSTITUENCIES, ALL_CONSTITUENCIES, get_constituencies_by_district

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'makkal-kural-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 168  # 7 days

# Create the main app
app = FastAPI(title="Makkal Kural API", description="Tamil Nadu Democratic Governance Platform")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===================== RATE LIMITING =====================

# Simple in-memory rate limiting (for production use Redis)
rate_limit_cache = {}
ISSUE_RATE_LIMIT = 5  # max issues per user per day
VOTE_RATE_LIMIT = 50  # max votes per user per day

async def check_rate_limit(user_id: str, action: str, limit: int) -> bool:
    """Check if user has exceeded rate limit"""
    key = f"{user_id}:{action}:{datetime.now(timezone.utc).date().isoformat()}"
    current = rate_limit_cache.get(key, 0)
    if current >= limit:
        return False
    rate_limit_cache[key] = current + 1
    return True

# ===================== CONSTANTS =====================

# Public Failure Index Categories
PFI_CATEGORIES = {
    "water": {"name_en": "Water Failure", "name_ta": "நீர் தோல்வி"},
    "flooding": {"name_en": "Flood Failure", "name_ta": "வெள்ள தோல்வி"},
    "health": {"name_en": "Health System Failure", "name_ta": "சுகாதார தோல்வி"},
    "roads": {"name_en": "Road & Transport Failure", "name_ta": "சாலை போக்குவரத்து தோல்வி"},
    "electricity": {"name_en": "Power Failure", "name_ta": "மின் தோல்வி"},
    "sewage": {"name_en": "Sewage Failure", "name_ta": "கழிவுநீர் தோல்வி"},
    "garbage": {"name_en": "Waste Management Failure", "name_ta": "கழிவு மேலாண்மை தோல்வி"}
}

TAMIL_NADU_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam",
    "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram",
    "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur",
    "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupattur",
    "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore",
    "Viluppuram", "Virudhunagar", "Kanniyakumari"
]

LOCAL_BODY_TYPES = ["Corporation", "Municipality", "Town Panchayat", "Village Panchayat"]

ISSUE_CATEGORIES = {
    "water": {"name_en": "Drinking Water", "name_ta": "குடிநீர்", "problems": [
        {"id": "no_water", "name_en": "No drinking water", "name_ta": "குடிநீர் இல்லை"},
        {"id": "contaminated", "name_en": "Contaminated water", "name_ta": "மாசுபட்ட நீர்"},
        {"id": "tanker", "name_en": "Tanker dependency", "name_ta": "டேங்கர் சார்பு"},
        {"id": "pipeline", "name_en": "Pipeline leakage", "name_ta": "குழாய் கசிவு"},
        {"id": "borewell", "name_en": "Borewell dried up", "name_ta": "போர்வெல் வறண்டது"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "flooding": {"name_en": "Flooding", "name_ta": "வெள்ளம்", "problems": [
        {"id": "drainage", "name_en": "Poor drainage", "name_ta": "வடிகால் பிரச்சனை"},
        {"id": "waterlogging", "name_en": "Water logging", "name_ta": "நீர் தேக்கம்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "roads": {"name_en": "Roads", "name_ta": "சாலைகள்", "problems": [
        {"id": "potholes", "name_en": "Potholes", "name_ta": "குழிகள்"},
        {"id": "no_road", "name_en": "No proper road", "name_ta": "சரியான சாலை இல்லை"},
        {"id": "damaged", "name_en": "Damaged road", "name_ta": "சேதமடைந்த சாலை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "sewage": {"name_en": "Sewage", "name_ta": "கழிவுநீர்", "problems": [
        {"id": "overflow", "name_en": "Sewage overflow", "name_ta": "கழிவுநீர் வழிவு"},
        {"id": "blocked", "name_en": "Blocked drains", "name_ta": "அடைப்பு"},
        {"id": "smell", "name_en": "Bad smell", "name_ta": "துர்நாற்றம்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "garbage": {"name_en": "Garbage", "name_ta": "குப்பை", "problems": [
        {"id": "no_collection", "name_en": "No garbage collection", "name_ta": "குப்பை சேகரிப்பு இல்லை"},
        {"id": "dumping", "name_en": "Illegal dumping", "name_ta": "சட்டவிரோத குப்பை கொட்டல்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "health": {"name_en": "Health Services", "name_ta": "சுகாதார சேவைகள்", "problems": [
        {"id": "no_hospital", "name_en": "No hospital nearby", "name_ta": "அருகில் மருத்துவமனை இல்லை"},
        {"id": "no_doctors", "name_en": "No doctors", "name_ta": "மருத்துவர்கள் இல்லை"},
        {"id": "medicines", "name_en": "No medicines", "name_ta": "மருந்துகள் இல்லை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "schools": {"name_en": "Schools / Colleges", "name_ta": "பள்ளிகள் / கல்லூரிகள்", "problems": [
        {"id": "infrastructure", "name_en": "Poor infrastructure", "name_ta": "மோசமான உள்கட்டமைப்பு"},
        {"id": "teachers", "name_en": "No teachers", "name_ta": "ஆசிரியர்கள் இல்லை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "farming": {"name_en": "Farming / Irrigation", "name_ta": "விவசாயம் / நீர்ப்பாசனம்", "problems": [
        {"id": "water_shortage", "name_en": "Water shortage", "name_ta": "நீர் பற்றாக்குறை"},
        {"id": "crop_damage", "name_en": "Crop damage", "name_ta": "பயிர் சேதம்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "transport": {"name_en": "Transport", "name_ta": "போக்குவரத்து", "problems": [
        {"id": "no_bus", "name_en": "No bus service", "name_ta": "பேருந்து சேவை இல்லை"},
        {"id": "irregular", "name_en": "Irregular service", "name_ta": "ஒழுங்கற்ற சேவை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "electricity": {"name_en": "Electricity", "name_ta": "மின்சாரம்", "problems": [
        {"id": "no_power", "name_en": "No power supply", "name_ta": "மின்சாரம் இல்லை"},
        {"id": "frequent_cuts", "name_en": "Frequent power cuts", "name_ta": "அடிக்கடி மின்வெட்டு"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "pollution": {"name_en": "Pollution", "name_ta": "மாசுபாடு", "problems": [
        {"id": "air", "name_en": "Air pollution", "name_ta": "காற்று மாசுபாடு"},
        {"id": "water_pollution", "name_en": "Water pollution", "name_ta": "நீர் மாசுபாடு"},
        {"id": "noise", "name_en": "Noise pollution", "name_ta": "ஒலி மாசுபாடு"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "employment": {"name_en": "Employment", "name_ta": "வேலைவாய்ப்பு", "problems": [
        {"id": "no_jobs", "name_en": "No job opportunities", "name_ta": "வேலைவாய்ப்பு இல்லை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "housing": {"name_en": "Housing", "name_ta": "வீட்டுவசதி", "problems": [
        {"id": "no_house", "name_en": "No proper housing", "name_ta": "சரியான வீடு இல்லை"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "welfare": {"name_en": "Welfare Schemes", "name_ta": "நலத்திட்டங்கள்", "problems": [
        {"id": "not_received", "name_en": "Benefits not received", "name_ta": "பலன்கள் கிடைக்கவில்லை"},
        {"id": "delayed", "name_en": "Delayed benefits", "name_ta": "தாமதமான பலன்கள்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "corruption": {"name_en": "Corruption", "name_ta": "ஊழல்", "problems": [
        {"id": "bribery", "name_en": "Bribery demanded", "name_ta": "லஞ்சம் கேட்கப்பட்டது"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]},
    "safety": {"name_en": "Public Safety", "name_ta": "பொது பாதுகாப்பு", "problems": [
        {"id": "street_lights", "name_en": "No street lights", "name_ta": "தெரு விளக்குகள் இல்லை"},
        {"id": "crime", "name_en": "Crime concerns", "name_ta": "குற்றம் சம்பந்தமான கவலைகள்"},
        {"id": "other", "name_en": "Other", "name_ta": "மற்றவை"}
    ]}
}

ESCALATION_HIERARCHY = [
    {"level": 1, "role_en": "Village Administrative Officer (VAO) / Ward Officer", "role_ta": "கிராம நிர்வாக அலுவலர் / வார்டு அலுவலர்", "sla_days": 7},
    {"level": 2, "role_en": "Block Development Officer (BDO) / Zonal Officer", "role_ta": "வட்டார வளர்ச்சி அலுவலர் / மண்டல அலுவலர்", "sla_days": 14},
    {"level": 3, "role_en": "District Collector", "role_ta": "மாவட்ட ஆட்சியர்", "sla_days": 21},
    {"level": 4, "role_en": "Concerned Department Secretary", "role_ta": "சம்பந்தப்பட்ட துறை செயலாளர்", "sla_days": 30},
    {"level": 5, "role_en": "Concerned Minister", "role_ta": "சம்பந்தப்பட்ட அமைச்சர்", "sla_days": 45},
    {"level": 6, "role_en": "Chief Secretary", "role_ta": "தலைமை செயலாளர்", "sla_days": 60},
    {"level": 7, "role_en": "Chief Minister", "role_ta": "முதலமைச்சர்", "sla_days": 90}
]

# ===================== MODELS =====================

class OTPRequest(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    otp: str

class UserProfile(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    local_body_type: Optional[str] = None
    local_body_name: Optional[str] = None
    ward: Optional[str] = None

class IssueCreate(BaseModel):
    district: str
    local_body_type: str
    local_body_name: str
    ward: Optional[str] = None
    street: Optional[str] = None
    category: str
    problem_id: str
    description: str
    voice_note_text: Optional[str] = None
    frequency: str  # daily, weekly, seasonal, emergency
    affected_people: str  # only_me, 10-50, 50-500, entire_area
    duration: str  # weeks, months, years
    media_urls: List[str] = []
    is_anonymous: Optional[bool] = False  # Anonymous reporting for sensitive issues
    # L1: Central vs state dept jurisdiction
    dept_type: Optional[str] = "state"  # 'state' | 'central' | 'mixed'
    # L2: GPS coords for ward-boundary-redraw resilience
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    gps_accuracy: Optional[int] = None
    # L3: Multi-department buck-passing prevention
    responsible_depts: Optional[List[str]] = []

class VoteRequest(BaseModel):
    vote_type: str  # support, oppose

class CommentCreate(BaseModel):
    text: str

class SchemeFeedback(BaseModel):
    scheme_name: str
    feedback_type: str  # not_useful, corrupt, not_reaching, outdated
    action: str  # modify, merge, remove
    description: str

class NotificationRead(BaseModel):
    notification_id: str


class RTIGenerateRequest(BaseModel):
    language: Optional[str] = "both"  # "en" | "ta" | "both"


class RTISaveRequest(BaseModel):
    registration_number: str
    filed_at: Optional[str] = None
    pio_dept: Optional[str] = None
    language: Optional[str] = "en"


class AIChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = "ta"
    history: Optional[List[Dict[str, str]]] = []

# ===================== AUTH HELPERS =====================

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def create_jwt_token(user_id: str, mobile: str):
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "mobile": mobile,
        "exp": expiration,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            return user
    except:
        pass
    return None

# ===================== MODERATION =====================

BLOCKED_WORDS = ["abuse", "hate", "violence"]  # Basic keyword list - AI moderation in separate endpoint

async def moderate_content(text: str) -> Dict[str, Any]:
    """Basic content moderation - enhanced with AI in separate endpoint"""
    text_lower = text.lower()
    for word in BLOCKED_WORDS:
        if word in text_lower:
            return {"approved": False, "reason": "Contains inappropriate content"}
    return {"approved": True, "reason": None}

# ===================== NOTIFICATION HELPERS =====================

async def create_notification(user_id: str, title: str, title_ta: str, message: str, message_ta: str, 
                             notification_type: str, issue_id: str = None):
    """Create an in-app notification for a user"""
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "title_ta": title_ta,
        "message": message,
        "message_ta": message_ta,
        "type": notification_type,  # escalation, majority, status_change, comment
        "issue_id": issue_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    return notification

async def notify_issue_supporters(issue_id: str, title: str, title_ta: str, message: str, message_ta: str, 
                                  notification_type: str):
    """Notify all supporters of an issue"""
    votes = await db.votes.find({"issue_id": issue_id, "vote_type": "support"}).to_list(1000)
    for vote in votes:
        await create_notification(vote["user_id"], title, title_ta, message, message_ta, notification_type, issue_id)

# ===================== PFI (PUBLIC FAILURE INDEX) HELPERS =====================

async def calculate_pfi_score(district: str, category: str) -> float:
    """Calculate Public Failure Index score for a district/category"""
    # Count unresolved issues
    unresolved = await db.issues.count_documents({
        "district": district,
        "category": category,
        "status": {"$ne": "resolved"}
    })
    
    # Count resolved issues (reduces score)
    resolved = await db.issues.count_documents({
        "district": district,
        "category": category,
        "status": "resolved"
    })
    
    # Count repeat issues (same problem in same area within 6 months)
    six_months_ago = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    repeat_issues = await db.issues.count_documents({
        "district": district,
        "category": category,
        "created_at": {"$gte": six_months_ago}
    })
    
    # Calculate score: unresolved issues + repeat penalty - resolved bonus
    score = (unresolved * 10) + (repeat_issues * 2) - (resolved * 3)
    return max(0, min(100, score))  # Clamp between 0-100

async def get_district_pfi(district: str) -> Dict[str, Any]:
    """Get full PFI breakdown for a district"""
    pfi_scores = {}
    total_score = 0
    
    for cat_key in PFI_CATEGORIES.keys():
        score = await calculate_pfi_score(district, cat_key)
        pfi_scores[cat_key] = {
            "score": score,
            "name_en": PFI_CATEGORIES[cat_key]["name_en"],
            "name_ta": PFI_CATEGORIES[cat_key]["name_ta"],
            "level": "critical" if score >= 70 else "warning" if score >= 40 else "normal"
        }
        total_score += score
    
    return {
        "district": district,
        "overall_score": round(total_score / len(PFI_CATEGORIES), 1),
        "categories": pfi_scores,
        "calculated_at": datetime.now(timezone.utc).isoformat()
    }

# ===================== AUTH ENDPOINTS =====================

@api_router.post("/auth/send-otp")
async def send_otp(request: OTPRequest):
    """Send OTP to mobile number"""
    mobile = request.mobile.strip()
    if len(mobile) != 10 or not mobile.isdigit():
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    
    otp = generate_otp()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    await db.otps.update_one(
        {"mobile": mobile},
        {"$set": {"otp": otp, "expiry": expiry.isoformat(), "attempts": 0}},
        upsert=True
    )
    
    # In production, send SMS here
    logger.info(f"OTP for {mobile}: {otp}")  # For testing
    
    return {"success": True, "message": "OTP sent successfully", "otp_for_testing": otp}

@api_router.post("/auth/verify-otp")
async def verify_otp(request: OTPVerify):
    """Verify OTP and return JWT token"""
    mobile = request.mobile.strip()
    
    otp_doc = await db.otps.find_one({"mobile": mobile})
    if not otp_doc:
        raise HTTPException(status_code=400, detail="OTP not found. Please request a new OTP")
    
    if otp_doc.get("attempts", 0) >= 5:
        raise HTTPException(status_code=400, detail="Too many attempts. Please request a new OTP")
    
    expiry = datetime.fromisoformat(otp_doc["expiry"])
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new OTP")
    
    if otp_doc["otp"] != request.otp:
        await db.otps.update_one({"mobile": mobile}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Delete used OTP
    await db.otps.delete_one({"mobile": mobile})
    
    # Find or create user
    user = await db.users.find_one({"mobile": mobile}, {"_id": 0})
    if not user:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "mobile": mobile,
            "name": None,
            "district": None,
            "local_body_type": None,
            "local_body_name": None,
            "ward": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "issues_raised": 0,
            "votes_cast": 0
        }
        await db.users.insert_one(user)
        user.pop("_id", None)
    
    token = create_jwt_token(user["id"], mobile)
    
    return {"success": True, "token": token, "user": user}

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {"success": True, "user": user}

@api_router.put("/auth/profile")
async def update_profile(profile: UserProfile, user: dict = Depends(get_current_user)):
    """Update user profile"""
    update_data = {k: v for k, v in profile.model_dump().items() if v is not None}
    if update_data:
        await db.users.update_one({"id": user["id"]}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {"success": True, "user": updated_user}

# ===================== CONSTANTS ENDPOINTS =====================

@api_router.get("/constants/districts")
async def get_districts():
    """Get list of Tamil Nadu districts"""
    return {"districts": TAMIL_NADU_DISTRICTS}

@api_router.get("/constants/local-body-types")
async def get_local_body_types():
    """Get list of local body types"""
    return {"types": LOCAL_BODY_TYPES}

@api_router.get("/constants/categories")
async def get_categories():
    """Get issue categories with problems"""
    return {"categories": ISSUE_CATEGORIES}

@api_router.get("/constants/escalation-hierarchy")
async def get_escalation_hierarchy():
    """Get escalation hierarchy"""
    return {"hierarchy": ESCALATION_HIERARCHY}

@api_router.get("/constants/constituencies")
async def get_constituencies(district: Optional[str] = None):
    """Get all 234 Tamil Nadu assembly constituencies, optionally filtered by district"""
    if district:
        constituencies = get_constituencies_by_district(district)
        return {"district": district, "constituencies": constituencies, "count": len(constituencies)}
    return {
        "constituencies": ALL_CONSTITUENCIES,
        "by_district": TAMIL_NADU_CONSTITUENCIES,
        "total": len(ALL_CONSTITUENCIES)
    }

# ===================== ISSUE ENDPOINTS =====================

@api_router.post("/issues")
async def create_issue(issue: IssueCreate, user: dict = Depends(get_current_user)):
    """Create a new issue"""
    # Rate limiting check
    if not await check_rate_limit(user["id"], "issue", ISSUE_RATE_LIMIT):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. You can raise up to 5 issues per day.")
    
    # Validate location
    if issue.district not in TAMIL_NADU_DISTRICTS:
        raise HTTPException(status_code=400, detail="Invalid district")
    if issue.local_body_type not in LOCAL_BODY_TYPES:
        raise HTTPException(status_code=400, detail="Invalid local body type")
    if issue.category not in ISSUE_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Moderate content
    moderation = await moderate_content(issue.description)
    if not moderation["approved"]:
        raise HTTPException(status_code=400, detail=moderation["reason"])
    
    issue_id = str(uuid.uuid4())
    category_info = ISSUE_CATEGORIES[issue.category]
    problem_info = next((p for p in category_info["problems"] if p["id"] == issue.problem_id), None)
    
    issue_doc = {
        "id": issue_id,
        "user_id": user["id"],
        "user_name": user.get("name", "Anonymous"),
        "user_mobile": user["mobile"][-4:],  # Last 4 digits only
        "district": issue.district,
        "local_body_type": issue.local_body_type,
        "local_body_name": issue.local_body_name,
        "ward": issue.ward,
        "street": issue.street,
        "category": issue.category,
        "category_name_en": category_info["name_en"],
        "category_name_ta": category_info["name_ta"],
        "problem_id": issue.problem_id,
        "problem_name_en": problem_info["name_en"] if problem_info else "Other",
        "problem_name_ta": problem_info["name_ta"] if problem_info else "மற்றவை",
        "description": issue.description,
        "voice_note_text": issue.voice_note_text,
        "frequency": issue.frequency,
        "affected_people": issue.affected_people,
        "duration": issue.duration,
        "media_urls": issue.media_urls,
        "is_anonymous": issue.is_anonymous,  # Anonymous reporting flag
        # L1/L2/L3 new fields:
        "dept_type": issue.dept_type or "state",
        "gps_lat": issue.gps_lat,
        "gps_lng": issue.gps_lng,
        "gps_accuracy": issue.gps_accuracy,
        "responsible_depts": issue.responsible_depts or [],
        # L4 dispute system:
        "dispute_count": 0,
        "proof_count": 0,
        "resolved_at": None,
        # L5 CPGRAMS bridge:
        "cpgrams_filed": False,
        "cpgrams_filed_at": None,
        "status": "pending",
        "support_count": 0,
        "oppose_count": 0,
        "support_percentage": 0,
        "comment_count": 0,
        "current_level": 1,
        "escalation_history": [{
            "level": 1,
            "role_en": ESCALATION_HIERARCHY[0]["role_en"],
            "role_ta": ESCALATION_HIERARCHY[0]["role_ta"],
            "reached_at": datetime.now(timezone.utc).isoformat(),
            "sla_deadline": (datetime.now(timezone.utc) + timedelta(days=ESCALATION_HIERARCHY[0]["sla_days"])).isoformat()
        }],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.issues.insert_one(issue_doc)
    await db.users.update_one({"id": user["id"]}, {"$inc": {"issues_raised": 1}})
    
    # Remove _id before returning
    issue_doc.pop("_id", None)
    return {"success": True, "issue": issue_doc}

@api_router.get("/issues")
async def get_issues(
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_optional_user)
):
    """Get list of issues with filters"""
    query = {}
    if district:
        query["district"] = district
    if constituency:
        query["constituency"] = constituency
    if category:
        query["category"] = category
    if status:
        query["status"] = status
    
    sort_direction = -1 if sort_order == "desc" else 1
    skip = (page - 1) * limit
    
    issues = await db.issues.find(query, {"_id": 0}).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
    total = await db.issues.count_documents(query)
    
    # If user is logged in, add their vote status
    if user:
        issue_ids = [i["id"] for i in issues]
        user_votes = await db.votes.find({"user_id": user["id"], "issue_id": {"$in": issue_ids}}, {"_id": 0}).to_list(1000)
        vote_map = {v["issue_id"]: v["vote_type"] for v in user_votes}
        for issue in issues:
            issue["user_vote"] = vote_map.get(issue["id"])
    
    return {
        "success": True,
        "issues": issues,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/issues/{issue_id}")
async def get_issue(issue_id: str, user: dict = Depends(get_optional_user)):
    """Get single issue details"""
    issue = await db.issues.find_one({"id": issue_id}, {"_id": 0})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Get comments
    comments = await db.comments.find({"issue_id": issue_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Get user's vote if logged in
    user_vote = None
    if user:
        vote = await db.votes.find_one({"user_id": user["id"], "issue_id": issue_id}, {"_id": 0})
        user_vote = vote["vote_type"] if vote else None
    
    return {
        "success": True,
        "issue": issue,
        "comments": comments,
        "user_vote": user_vote
    }

@api_router.get("/my-issues")
async def get_my_issues(user: dict = Depends(get_current_user)):
    """Get issues raised by current user"""
    issues = await db.issues.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"success": True, "issues": issues}

# ===================== VOTING ENDPOINTS =====================

@api_router.post("/issues/{issue_id}/vote")
async def vote_issue(issue_id: str, vote: VoteRequest, user: dict = Depends(get_current_user)):
    """Vote on an issue (support/oppose)"""
    # Rate limiting
    if not await check_rate_limit(user["id"], "vote", VOTE_RATE_LIMIT):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. You can cast up to 50 votes per day.")
    
    issue = await db.issues.find_one({"id": issue_id})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check if user can vote (same district or no district set)
    if user.get("district") and user["district"] != issue["district"]:
        raise HTTPException(status_code=403, detail="You can only vote on issues from your district. Update your profile to set your district.")
    
    if vote.vote_type not in ["support", "oppose"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    # Check existing vote
    existing_vote = await db.votes.find_one({"user_id": user["id"], "issue_id": issue_id})
    old_status = issue.get("status")
    old_level = issue.get("current_level", 1)
    
    if existing_vote:
        if existing_vote["vote_type"] == vote.vote_type:
            # Remove vote
            await db.votes.delete_one({"user_id": user["id"], "issue_id": issue_id})
            if vote.vote_type == "support":
                await db.issues.update_one({"id": issue_id}, {"$inc": {"support_count": -1}})
            else:
                await db.issues.update_one({"id": issue_id}, {"$inc": {"oppose_count": -1}})
            await db.users.update_one({"id": user["id"]}, {"$inc": {"votes_cast": -1}})
        else:
            # Change vote (allowed once)
            await db.votes.update_one(
                {"user_id": user["id"], "issue_id": issue_id},
                {"$set": {"vote_type": vote.vote_type, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            if vote.vote_type == "support":
                await db.issues.update_one({"id": issue_id}, {"$inc": {"support_count": 1, "oppose_count": -1}})
            else:
                await db.issues.update_one({"id": issue_id}, {"$inc": {"support_count": -1, "oppose_count": 1}})
    else:
        # New vote
        vote_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "issue_id": issue_id,
            "vote_type": vote.vote_type,
            "district": issue["district"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.votes.insert_one(vote_doc)
        if vote.vote_type == "support":
            await db.issues.update_one({"id": issue_id}, {"$inc": {"support_count": 1}})
        else:
            await db.issues.update_one({"id": issue_id}, {"$inc": {"oppose_count": 1}})
        await db.users.update_one({"id": user["id"]}, {"$inc": {"votes_cast": 1}})
    
    # Update support percentage and check escalation
    updated_issue = await db.issues.find_one({"id": issue_id})
    total_votes = updated_issue["support_count"] + updated_issue["oppose_count"]
    support_percentage = (updated_issue["support_count"] / total_votes * 100) if total_votes > 0 else 0
    
    # Check escalation thresholds and mark validation status
    status_updates = {}
    new_status = old_status
    
    # 60%+ support = "Publicly Validated Issue"
    if support_percentage >= 60 and updated_issue["support_count"] >= 10:
        status_updates["publicly_validated"] = True
    
    if updated_issue["support_count"] >= 25 and old_status == "pending":
        status_updates["status"] = "area_concern"
        new_status = "area_concern"
    if updated_issue["support_count"] >= 100:
        status_updates["status"] = "serious_issue"
        new_status = "serious_issue"
        # L7: SMS milestone alert when crossing 100 for the first time
        if (issue.get("support_count", 0) < 100):
            await notify_user_with_sms(issue["user_id"], "milestone_100", {
                "district": issue.get("district", ""),
                "category": issue.get("category", ""),
                "url": f"{os.environ.get('FRONTEND_URL', '')}/issues/{issue_id}",
            })
    
    # Auto-escalation logic - 75%+ support triggers mandatory escalation
    should_escalate = False
    escalation_reason = ""
    
    if support_percentage >= 75 and updated_issue["support_count"] >= 25:
        should_escalate = True
        escalation_reason = f"75%+ support threshold reached ({support_percentage:.1f}% with {updated_issue['support_count']} supporters)"
    elif support_percentage >= 60 and updated_issue["support_count"] >= 50:
        should_escalate = True
        escalation_reason = f"60%+ support with 50+ supporters ({support_percentage:.1f}%)"
    
    new_level = old_level
    if should_escalate and updated_issue["current_level"] < 7:
        new_level = updated_issue["current_level"] + 1
        new_hierarchy = ESCALATION_HIERARCHY[new_level - 1]
        escalation_entry = {
            "level": new_level,
            "role_en": new_hierarchy["role_en"],
            "role_ta": new_hierarchy["role_ta"],
            "reached_at": datetime.now(timezone.utc).isoformat(),
            "sla_deadline": (datetime.now(timezone.utc) + timedelta(days=new_hierarchy["sla_days"])).isoformat(),
            "auto_escalated": True,
            "reason": escalation_reason
        }
        status_updates["current_level"] = new_level
        status_updates["$push"] = {"escalation_history": escalation_entry}
        
        # Notify issue creator and supporters about escalation
        await create_notification(
            issue["user_id"],
            f"Issue Escalated to Level {new_level}",
            f"பிரச்சனை நிலை {new_level} க்கு உயர்த்தப்பட்டது",
            f"Your issue has been escalated to {new_hierarchy['role_en']}",
            f"உங்கள் பிரச்சனை {new_hierarchy['role_ta']} க்கு உயர்த்தப்பட்டது",
            "escalation",
            issue_id
        )
        # L7: SMS alert (gated by user preferences)
        await notify_user_with_sms(issue["user_id"], "escalation", {
            "district": issue.get("district", ""),
            "level": new_level,
            "official": new_hierarchy["role_en"],
            "url": f"{os.environ.get('FRONTEND_URL', '')}/issues/{issue_id}",
        })
    
    # Notify on status change
    if new_status != old_status:
        await create_notification(
            issue["user_id"],
            f"Issue Status Changed",
            f"பிரச்சனை நிலை மாற்றம்",
            f"Your issue is now marked as '{new_status}'",
            f"உங்கள் பிரச்சனை '{new_status}' என குறிக்கப்பட்டது",
            "status_change",
            issue_id
        )
    
    # Notify when majority support reached (first time hitting 60%)
    if support_percentage >= 60 and not issue.get("publicly_validated"):
        await create_notification(
            issue["user_id"],
            "Majority Support Reached!",
            "பெரும்பான்மை ஆதரவு பெறப்பட்டது!",
            f"Your issue has {support_percentage:.0f}% public support and is now validated",
            f"உங்கள் பிரச்சனை {support_percentage:.0f}% ஆதரவு பெற்று சரிபார்க்கப்பட்டது",
            "majority",
            issue_id
        )
    
    await db.issues.update_one(
        {"id": issue_id},
        {"$set": {"support_percentage": round(support_percentage, 1), "updated_at": datetime.now(timezone.utc).isoformat(), **{k: v for k, v in status_updates.items() if k != "$push"}},
         **({k: v for k, v in status_updates.items() if k == "$push"} if "$push" in status_updates else {})}
    )
    
    final_issue = await db.issues.find_one({"id": issue_id}, {"_id": 0})
    return {"success": True, "issue": final_issue}

# ===================== COMMENT ENDPOINTS =====================

@api_router.post("/issues/{issue_id}/comments")
async def add_comment(issue_id: str, comment: CommentCreate, user: dict = Depends(get_current_user)):
    """Add comment to an issue"""
    issue = await db.issues.find_one({"id": issue_id})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Moderate content
    moderation = await moderate_content(comment.text)
    if not moderation["approved"]:
        raise HTTPException(status_code=400, detail=moderation["reason"])
    
    comment_doc = {
        "id": str(uuid.uuid4()),
        "issue_id": issue_id,
        "user_id": user["id"],
        "user_name": user.get("name", "Anonymous"),
        "text": comment.text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.comments.insert_one(comment_doc)
    await db.issues.update_one({"id": issue_id}, {"$inc": {"comment_count": 1}})
    
    comment_doc.pop("_id", None)
    return {"success": True, "comment": comment_doc}

# ===================== DASHBOARD ENDPOINTS =====================

@api_router.get("/dashboard/district/{district}")
async def get_district_dashboard(district: str):
    """Get district dashboard statistics"""
    if district not in TAMIL_NADU_DISTRICTS:
        raise HTTPException(status_code=400, detail="Invalid district")
    
    # Get statistics
    total_issues = await db.issues.count_documents({"district": district})
    pending_issues = await db.issues.count_documents({"district": district, "status": "pending"})
    resolved_issues = await db.issues.count_documents({"district": district, "status": "resolved"})
    
    # Top supported issues
    top_issues = await db.issues.find(
        {"district": district},
        {"_id": 0}
    ).sort("support_count", -1).limit(10).to_list(10)
    
    # Longest pending
    longest_pending = await db.issues.find(
        {"district": district, "status": {"$ne": "resolved"}},
        {"_id": 0}
    ).sort("created_at", 1).limit(10).to_list(10)
    
    # Recently resolved
    recently_resolved = await db.issues.find(
        {"district": district, "status": "resolved"},
        {"_id": 0}
    ).sort("updated_at", -1).limit(10).to_list(10)
    
    # Category breakdown
    pipeline = [
        {"$match": {"district": district}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    category_stats = await db.issues.aggregate(pipeline).to_list(100)
    
    return {
        "success": True,
        "district": district,
        "stats": {
            "total": total_issues,
            "pending": pending_issues,
            "resolved": resolved_issues,
            "resolution_rate": round(resolved_issues / total_issues * 100, 1) if total_issues > 0 else 0
        },
        "top_issues": top_issues,
        "longest_pending": longest_pending,
        "recently_resolved": recently_resolved,
        "category_breakdown": [{"category": s["_id"], "count": s["count"]} for s in category_stats]
    }

@api_router.get("/dashboard/overview")
async def get_overview_dashboard():
    """Get overall platform statistics"""
    total_issues = await db.issues.count_documents({})
    total_users = await db.users.count_documents({})
    total_votes = await db.votes.count_documents({})
    
    # Issues by status
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_stats = await db.issues.aggregate(status_pipeline).to_list(10)
    
    # Top districts by issues
    district_pipeline = [
        {"$group": {"_id": "$district", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    district_stats = await db.issues.aggregate(district_pipeline).to_list(10)
    
    # Issues at high escalation levels (Minister/CS/CM)
    high_level_issues = await db.issues.find(
        {"current_level": {"$gte": 5}},
        {"_id": 0}
    ).sort("support_count", -1).limit(20).to_list(20)
    
    # Recent trending (high support in last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    trending = await db.issues.find(
        {"created_at": {"$gte": week_ago}},
        {"_id": 0}
    ).sort("support_count", -1).limit(10).to_list(10)
    
    return {
        "success": True,
        "stats": {
            "total_issues": total_issues,
            "total_users": total_users,
            "total_votes": total_votes
        },
        "status_breakdown": [{"status": s["_id"], "count": s["count"]} for s in status_stats],
        "top_districts": [{"district": d["_id"], "count": d["count"]} for d in district_stats],
        "high_level_issues": high_level_issues,
        "trending": trending
    }

@api_router.get("/dashboard/leadership")
async def get_leadership_dashboard():
    """Get leadership dashboard - issues at Minister/CS/CM level"""
    # Issues with ministers
    minister_issues = await db.issues.find(
        {"current_level": 5},
        {"_id": 0}
    ).sort("support_count", -1).to_list(100)
    
    # Issues with Chief Secretary
    cs_issues = await db.issues.find(
        {"current_level": 6},
        {"_id": 0}
    ).sort("support_count", -1).to_list(100)
    
    # Issues with CM
    cm_issues = await db.issues.find(
        {"current_level": 7},
        {"_id": 0}
    ).sort("support_count", -1).to_list(100)
    
    # Overdue issues (past SLA)
    now = datetime.now(timezone.utc).isoformat()
    overdue_pipeline = [
        {"$match": {"status": {"$ne": "resolved"}}},
        {"$addFields": {
            "last_escalation": {"$arrayElemAt": ["$escalation_history", -1]}
        }},
        {"$match": {"last_escalation.sla_deadline": {"$lt": now}}},
        {"$project": {"_id": 0}}
    ]
    overdue_issues = await db.issues.aggregate(overdue_pipeline).to_list(100)
    
    return {
        "success": True,
        "minister_issues": {"count": len(minister_issues), "issues": minister_issues},
        "cs_issues": {"count": len(cs_issues), "issues": cs_issues},
        "cm_issues": {"count": len(cm_issues), "issues": cm_issues},
        "overdue_issues": {"count": len(overdue_issues), "issues": overdue_issues}
    }

# ===================== SCHEME FEEDBACK ENDPOINTS =====================

@api_router.post("/schemes/feedback")
async def create_scheme_feedback(feedback: SchemeFeedback, user: dict = Depends(get_current_user)):
    """Submit feedback on a government scheme"""
    moderation = await moderate_content(feedback.description)
    if not moderation["approved"]:
        raise HTTPException(status_code=400, detail=moderation["reason"])
    
    feedback_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "user_district": user.get("district"),
        "scheme_name": feedback.scheme_name,
        "feedback_type": feedback.feedback_type,
        "action": feedback.action,
        "description": feedback.description,
        "support_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.scheme_feedback.insert_one(feedback_doc)
    feedback_doc.pop("_id", None)
    return {"success": True, "feedback": feedback_doc}

@api_router.get("/schemes/feedback")
async def get_scheme_feedback(district: Optional[str] = None, page: int = 1, limit: int = 20):
    """Get scheme feedback list"""
    query = {}
    if district:
        query["user_district"] = district
    
    skip = (page - 1) * limit
    feedback_list = await db.scheme_feedback.find(query, {"_id": 0}).sort("support_count", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.scheme_feedback.count_documents(query)
    
    return {
        "success": True,
        "feedback": feedback_list,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

# ===================== VOICE TRANSCRIPTION =====================

@api_router.post("/voice/transcribe")
async def transcribe_voice(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Transcribe voice note to Tamil text using OpenAI Whisper"""
    try:
        from emergentintegrations.llm.openai import OpenAISpeechToText
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Voice transcription not configured")
        
        # Read file
        contents = await file.read()
        
        # Initialize STT
        stt = OpenAISpeechToText(api_key=api_key)
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Transcribe
        with open(tmp_path, "rb") as audio_file:
            response = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                language="ta",  # Tamil
                response_format="json"
            )
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {"success": True, "text": response.text}
    except ImportError:
        raise HTTPException(status_code=500, detail="Voice transcription module not available")
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# ===================== AI MODERATION =====================

@api_router.post("/moderate")
async def ai_moderate_content(text: str = Form(...)):
    """AI-powered content moderation"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            # Fallback to basic moderation
            return await moderate_content(text)
        
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="""You are a content moderator for a civic governance platform. 
            Your task is to check if the content is appropriate.
            Allow: Criticism of government, policies, officials (constructive)
            Block: Abusive language, personal attacks, hate speech, political party abuse, threats, violence
            
            Respond with JSON: {"approved": true/false, "reason": "reason if blocked"}"""
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=f"Check this content: {text}")
        response = await chat.send_message(user_message)
        
        import json
        try:
            result = json.loads(response)
            return result
        except:
            return {"approved": True, "reason": None}
    except ImportError:
        return await moderate_content(text)
    except Exception as e:
        logger.error(f"AI moderation error: {str(e)}")
        return await moderate_content(text)

# ===================== FILE UPLOAD (LOCAL STORAGE) =====================

UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Upload photo or video (local storage for MVP)"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Validate file size (max 50MB)
    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Save file
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Return URL
    file_url = f"/api/uploads/{filename}"
    return {"success": True, "url": file_url, "filename": filename}

@api_router.get("/uploads/{filename}")
async def get_upload(filename: str):
    """Serve uploaded file"""
    from fastapi.responses import FileResponse
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)

# ===================== HEALTH CHECK =====================

@api_router.get("/")
async def root():
    return {"message": "Makkal Kural API - Tamil Nadu Democratic Governance Platform"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ===================== PUBLIC FAILURE INDEX (PFI) =====================

@api_router.get("/pfi/districts")
async def get_all_districts_pfi():
    """Get PFI scores for all districts"""
    results = []
    for district in TAMIL_NADU_DISTRICTS:
        pfi = await get_district_pfi(district)
        results.append(pfi)
    
    # Sort by overall score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return {"success": True, "districts": results}

@api_router.get("/pfi/district/{district}")
async def get_single_district_pfi(district: str):
    """Get detailed PFI for a specific district"""
    if district not in TAMIL_NADU_DISTRICTS:
        raise HTTPException(status_code=400, detail="Invalid district")
    
    pfi = await get_district_pfi(district)
    
    # Get top issues contributing to each category
    category_issues = {}
    for cat_key in PFI_CATEGORIES.keys():
        issues = await db.issues.find(
            {"district": district, "category": cat_key, "status": {"$ne": "resolved"}},
            {"_id": 0}
        ).sort("support_count", -1).limit(5).to_list(5)
        category_issues[cat_key] = issues
    
    pfi["category_issues"] = category_issues
    return {"success": True, "pfi": pfi}

@api_router.get("/pfi/categories")
async def get_pfi_categories():
    """Get list of PFI categories"""
    return {"success": True, "categories": PFI_CATEGORIES}

# ===================== NOTIFICATIONS =====================

@api_router.get("/notifications")
async def get_notifications(user: dict = Depends(get_current_user)):
    """Get user's notifications"""
    notifications = await db.notifications.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    unread_count = await db.notifications.count_documents({"user_id": user["id"], "read": False})
    
    return {
        "success": True,
        "notifications": notifications,
        "unread_count": unread_count
    }

@api_router.post("/notifications/read/{notification_id}")
async def mark_notification_read(notification_id: str, user: dict = Depends(get_current_user)):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": user["id"]},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}

@api_router.post("/notifications/read-all")
async def mark_all_notifications_read(user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    await db.notifications.update_many(
        {"user_id": user["id"], "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

# ===================== SCHEME FEEDBACK VOTING =====================

@api_router.post("/schemes/feedback/{feedback_id}/support")
async def support_scheme_feedback(feedback_id: str, user: dict = Depends(get_current_user)):
    """Support a scheme feedback suggestion"""
    feedback = await db.scheme_feedback.find_one({"id": feedback_id})
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check if already voted
    existing = await db.scheme_votes.find_one({"user_id": user["id"], "feedback_id": feedback_id})
    if existing:
        # Toggle off
        await db.scheme_votes.delete_one({"user_id": user["id"], "feedback_id": feedback_id})
        await db.scheme_feedback.update_one({"id": feedback_id}, {"$inc": {"support_count": -1}})
        return {"success": True, "action": "removed"}
    
    # Add vote
    await db.scheme_votes.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "feedback_id": feedback_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    await db.scheme_feedback.update_one({"id": feedback_id}, {"$inc": {"support_count": 1}})
    
    # Check if crosses majority threshold (e.g., 100 supporters)
    updated = await db.scheme_feedback.find_one({"id": feedback_id})
    if updated["support_count"] >= 100 and not updated.get("in_review_queue"):
        await db.scheme_feedback.update_one(
            {"id": feedback_id},
            {"$set": {"in_review_queue": True, "review_queue_date": datetime.now(timezone.utc).isoformat()}}
        )
    
    return {"success": True, "action": "added", "support_count": updated["support_count"]}


# ====================
# ADMIN ENDPOINTS
# ====================

@api_router.get("/admin/issues")
async def get_admin_issues(
    level: int = 1,
    district: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get issues for admin dashboard filtered by escalation level"""
    query = {"current_level": level}
    if district:
        query["district"] = district
    if status:
        query["status"] = status
    
    issues = await db.issues.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"issues": issues, "count": len(issues)}

@api_router.get("/admin/stats")
async def get_admin_stats(
    level: int = 1,
    district: Optional[str] = None
):
    """Get statistics for admin dashboard"""
    query = {"current_level": level}
    if district:
        query["district"] = district
    
    total = await db.issues.count_documents(query)
    pending = await db.issues.count_documents({**query, "status": "pending"})
    in_progress = await db.issues.count_documents({**query, "status": "in_progress"})
    resolved = await db.issues.count_documents({**query, "status": "resolved"})
    
    # Count overdue (more than 7 days old and not resolved)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    overdue = await db.issues.count_documents({
        **query,
        "status": {"$nin": ["resolved", "rejected"]},
        "created_at": {"$lt": seven_days_ago}
    })
    
    return {
        "stats": {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "overdue": overdue,
            "resolution_rate": round((resolved / total * 100)) if total > 0 else 0
        }
    }

@api_router.post("/admin/issues/{issue_id}/update")
async def admin_update_issue(
    issue_id: str,
    status: str = Form(None),
    official_response: str = Form(None),
    admin_level: int = Form(1)
):
    """Update issue status and add official response"""
    issue = await db.issues.find_one({"id": issue_id})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if status:
        update_data["status"] = status
        if status == "resolved":
            update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
        
        # Add to status history
        status_entry = {
            "status": status,
            "updated_by": f"Level {admin_level} Official",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.issues.update_one(
            {"id": issue_id},
            {"$push": {"status_history": status_entry}}
        )
        # L7: SMS alert when issue is officially resolved
        if status == "resolved":
            await notify_user_with_sms(issue["user_id"], "resolution", {
                "district": issue.get("district", ""),
                "category": issue.get("category", ""),
                "url": f"{os.environ.get('FRONTEND_URL', '')}/issues/{issue_id}",
            })
    
    if official_response:
        # Add official comment
        comment_id = str(uuid.uuid4())
        comment_doc = {
            "id": comment_id,
            "issue_id": issue_id,
            "user_id": f"admin_level_{admin_level}",
            "user_name": f"Official (Level {admin_level})",
            "text": official_response,
            "is_official": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.comments.insert_one(comment_doc)
        
        await db.issues.update_one(
            {"id": issue_id},
            {"$inc": {"comment_count": 1}}
        )
    
    await db.issues.update_one({"id": issue_id}, {"$set": update_data})
    
    return {"success": True, "message": "Issue updated successfully"}

# ====================
# FILE UPLOAD (S3-Ready)
# ====================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@api_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Upload file (images/videos) - S3-ready architecture"""
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/quicktime']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate unique filename
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Save file locally (can be replaced with S3 upload)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    # Generate URL (local for now, S3 URL in production)
    file_url = f"/uploads/{filename}"
    
    # Store file metadata
    file_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "url": file_url,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(file_doc)
    
    return {
        "success": True,
        "url": file_url,
        "filename": filename,
        "size": len(content)
    }



# ============================================================
# BATCH 3: SMS Preferences, Repeat Issue Detector, Weekly Reports, Budget Tracker
# ============================================================

# ---- SMS Helper (logging-only stub for now; production wires MSG91) ----
SMS_ENABLED = bool(os.environ.get('MSG91_API_KEY', ''))

async def send_sms_alert(mobile: str, alert_type: str, variables: dict):
    """Stub SMS sender. Logs intent. Real MSG91 integration pending API key."""
    logger.info(f"[SMS {'SEND' if SMS_ENABLED else 'DISABLED'}] type={alert_type} to={mobile} vars={variables}")
    return SMS_ENABLED

async def notify_user_with_sms(user_id: str, alert_type: str, variables: dict):
    """Check user SMS preferences before dispatching."""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return
    sms_prefs = user.get("sms_preferences", {})
    if not sms_prefs.get("enabled", False):
        return
    if not sms_prefs.get(alert_type, False):
        return
    mobile = user.get("mobile", "")
    if not mobile:
        return
    await send_sms_alert(mobile, alert_type, variables)


# ---- SMS Preferences Endpoint ----
@api_router.put("/auth/sms-preferences")
async def update_sms_preferences(preferences: dict, current_user: dict = Depends(get_current_user)):
    """L7 FIX: Save user SMS alert preferences (rural reach)."""
    allowed_keys = {"enabled", "escalation", "resolution", "milestone_100",
                    "dispute_reopen", "overdue", "district_weekly"}
    clean_prefs = {k: bool(v) for k, v in preferences.items() if k in allowed_keys}
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"sms_preferences": clean_prefs}}
    )
    return {"success": True, "preferences": clean_prefs}


# ---- Repeat Issue Detector ----
@api_router.get("/issues/{issue_id}/similar")
async def get_similar_issues(issue_id: str):
    """L6 FIX: Find similar past issues to surface systemic-failure evidence."""
    issue = await db.issues.find_one({"id": issue_id})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    two_years_ago = (datetime.now(timezone.utc) - timedelta(days=730)).isoformat()
    similar = await db.issues.find({
        "id": {"$ne": issue_id},
        "category": issue["category"],
        "district": issue["district"],
        "created_at": {"$gte": two_years_ago},
    }, {"_id": 0}).sort("created_at", -1).to_list(20)

    def similarity_score(s):
        score = 1
        if s.get("local_body_name") == issue.get("local_body_name"):
            score += 2
        if s.get("ward") == issue.get("ward"):
            score += 3
        return score

    similar.sort(key=similarity_score, reverse=True)
    top_candidates = similar[:5]

    resolved_count = sum(1 for s in top_candidates if s.get("status") == "resolved")
    unresolved_count = len(top_candidates) - resolved_count

    return {
        "similar_issues": top_candidates,
        "total_similar": len(top_candidates),
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "is_chronic": len(top_candidates) >= 2 and resolved_count == 0,
        "is_recurring": resolved_count > 0 and unresolved_count > 0,
    }


# ---- Weekly Reports ----
REPORT_GENERATION_CACHE: Dict[str, bool] = {}

async def _generate_summary_with_llm(district: str, stats: dict, top_descriptions: List[str]) -> Dict[str, str]:
    """Generate Tamil + English AI summaries using Anthropic Claude."""
    res_rate = round((stats['resolved'] / max(stats['total_issues'], 1)) * 100)
    summary_en = (
        f"{district} district currently has {stats['total_issues']} civic issues reported. "
        f"{stats['resolved']} issues have been resolved ({res_rate}% resolution rate). "
        f"{stats.get('new_this_week', 0)} new issues were raised this week. "
        f"{stats['serious']} issues are marked as serious and require urgent attention. "
        f"Top concerns include: " + ", ".join(d.split(":")[0].strip("- ") for d in top_descriptions[:3] if ":" in d) + "."
    )
    summary_ta = (
        f"{district} மாவட்டத்தில் தற்போது {stats['total_issues']} குடிமக்கள் பிரச்சனைகள் பதிவாகியுள்ளன. "
        f"{stats['resolved']} பிரச்சனைகள் தீர்க்கப்பட்டுள்ளன ({res_rate}% தீர்வு விகிதம்). "
        f"இந்த வாரம் {stats.get('new_this_week', 0)} புதிய பிரச்சனைகள் பதிவாயின. "
        f"{stats['serious']} பிரச்சனைகள் தீவிரமானவை மற்றும் உடனடி கவனிப்பு தேவை."
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"summary_en": summary_en, "summary_ta": summary_ta}

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)

        en_prompt = (
            f"Write a 3-paragraph governance accountability report for {district} district, Tamil Nadu.\n"
            f"Stats: {stats['total_issues']} total issues, {stats['resolved']} resolved ({res_rate}%), "
            f"{stats['serious']} serious, {stats.get('new_this_week',0)} new this week.\n"
            f"Top issues:\n" + "\n".join(top_descriptions) + "\n"
            f"Mention if resolution rate is improving or declining. Keep under 200 words. Be objective and factual."
        )
        en_msg = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system="You are an objective civic-governance analyst. Write factually and concisely.",
            messages=[{"role": "user", "content": en_prompt}]
        )
        summary_en = en_msg.content[0].text.strip()

        ta_prompt = (
            f"{district} மாவட்டத்திற்கான வாராந்திர நிர்வாக அறிக்கையை தமிழில் எழுதவும்.\n"
            f"புள்ளிவிவரங்கள்: மொத்தம் {stats['total_issues']}, தீர்க்கப்பட்டவை {stats['resolved']} ({res_rate}%), "
            f"தீவிரமானவை {stats['serious']}.\n"
            f"முக்கிய பிரச்சனைகள்:\n" + "\n".join(top_descriptions) + "\n"
            f"3 பத்திகளில் 200 வார்த்தைகளுக்குள் எழுதவும்."
        )
        ta_msg = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system="நீங்கள் நிர்வாக பகுப்பாய்வாளர். தமிழில் தெளிவாக எழுதவும்.",
            messages=[{"role": "user", "content": ta_prompt}]
        )
        summary_ta = ta_msg.content[0].text.strip()
    except Exception as e:
        logger.error(f"[Report AI error] {e}")

    return {"summary_en": summary_en, "summary_ta": summary_ta}


async def _generate_report_for_district(district: str) -> dict:
    """Core weekly report generator. Stores in db.weekly_reports."""
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    new_this_week = await db.issues.find(
        {"district": district, "created_at": {"$gte": week_ago}},
        {"_id": 0}
    ).to_list(100)

    all_district_issues = await db.issues.find({"district": district}, {"_id": 0}).to_list(500)
    resolved = [i for i in all_district_issues if i.get("status") == "resolved"]
    serious = [i for i in all_district_issues if i.get("status") == "serious_issue"]
    escalated = [i for i in all_district_issues if (i.get("current_level") or 1) >= 3]

    cat_breakdown: Dict[str, int] = {}
    for issue in all_district_issues:
        cat = issue.get("category", "Other")
        cat_breakdown[cat] = cat_breakdown.get(cat, 0) + 1

    top_issues = sorted(all_district_issues, key=lambda x: x.get("support_count", 0), reverse=True)[:5]
    total_votes = await db.votes.count_documents(
        {"issue_id": {"$in": [i["id"] for i in all_district_issues]}}
    )

    stats = {
        "total_issues": len(all_district_issues),
        "new_this_week": len(new_this_week),
        "resolved": len(resolved),
        "serious": len(serious),
        "escalated": len(escalated),
        "votes": total_votes,
    }
    res_rate = (len(resolved) / max(len(all_district_issues), 1)) * 100
    sentiment = "critical" if res_rate < 20 else "improving" if res_rate > 60 else "stable"

    top_descriptions = [
        f"- {i.get('category')}: {i.get('description', '')[:100]} ({i.get('support_count', 0)} supporters)"
        for i in top_issues
    ]
    ai_summaries = await _generate_summary_with_llm(district, stats, top_descriptions)

    clean_top = [{
        "id": i.get("id"),
        "category": i.get("category"),
        "description": (i.get("description") or "")[:200],
        "support_count": i.get("support_count", 0),
        "status": i.get("status"),
        "local_body_name": i.get("local_body_name"),
        "ward": i.get("ward"),
    } for i in top_issues]

    now = datetime.now(timezone.utc)
    report_doc = {
        "id": str(uuid.uuid4()),
        "district": district,
        "week_label": f"Week of {now.strftime('%b %d, %Y')}",
        "generated_at": now.isoformat(),
        "stats": stats,
        "category_breakdown": cat_breakdown,
        "top_issues": clean_top,
        "summary_en": ai_summaries["summary_en"],
        "summary_ta": ai_summaries["summary_ta"],
        "sentiment": sentiment,
    }
    await db.weekly_reports.insert_one(report_doc)
    report_doc.pop("_id", None)
    return report_doc


@api_router.post("/reports/generate")
async def generate_district_report(data: dict, current_user: dict = Depends(get_current_user)):
    """L10 FIX: rate-limited manual report generation (1/day/district)."""
    district = data.get("district")
    if not district:
        raise HTTPException(status_code=400, detail="District required")

    cache_key = f"{district}_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    if REPORT_GENERATION_CACHE.get(cache_key):
        raise HTTPException(
            status_code=429,
            detail="Report already generated today for this district. Auto-generates every Monday."
        )
    report = await _generate_report_for_district(district)
    REPORT_GENERATION_CACHE[cache_key] = True
    return {"success": True, "report": report}


@api_router.get("/reports/{district}")
async def get_district_reports(district: str):
    """Get past weekly reports for a district."""
    reports = await db.weekly_reports.find(
        {"district": district}, {"_id": 0}
    ).sort("generated_at", -1).to_list(10)
    return {"reports": reports}


# ---- Budget Tracker ----
@api_router.get("/budget")
async def get_budget_data(district: str, year: int = 2024):
    """L8 FIX: Budget allocations for a district + year with live open-issue counts."""
    budgets = await db.budget_allocations.find(
        {"district": district, "year": year}, {"_id": 0}
    ).to_list(50)
    for b in budgets:
        b["open_issues_live"] = await db.issues.count_documents({
            "district": district,
            "category": b["category"],
            "status": {"$nin": ["resolved"]},
        })
    return {"budgets": budgets, "district": district, "year": year}


@api_router.post("/budget")
async def add_budget_entry(entry: dict, current_user: dict = Depends(get_current_user)):
    """Admin only: add a budget entry."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    required = ["district", "category", "year", "allocated_cr", "source"]
    for field in required:
        if field not in entry:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    doc = {
        "id": str(uuid.uuid4()),
        "district": entry["district"],
        "category": entry["category"],
        "year": int(entry["year"]),
        "allocated_cr": float(entry["allocated_cr"]),
        "spent_cr": float(entry.get("spent_cr", 0)),
        "source": entry["source"],
        "source_url": entry.get("source_url", ""),
        "added_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.budget_allocations.insert_one(doc)
    doc.pop("_id", None)
    return {"success": True, "entry": doc}


@api_router.get("/budget/summary")
async def get_budget_summary(year: int = 2024):
    """Public cross-district budget accountability summary."""
    budgets = await db.budget_allocations.find({"year": year}, {"_id": 0}).to_list(500)
    summary = []
    for b in budgets:
        open_count = await db.issues.count_documents({
            "district": b["district"],
            "category": b["category"],
            "status": {"$nin": ["resolved"]},
        })
        spend_rate = (b.get("spent_cr", 0) / max(b.get("allocated_cr", 1), 0.01)) * 100
        summary.append({
            "district": b["district"],
            "category": b["category"],
            "allocated_cr": b.get("allocated_cr", 0),
            "spent_cr": b.get("spent_cr", 0),
            "spend_rate": round(spend_rate),
            "open_issues": open_count,
            "accountability_flag": open_count > 50 and spend_rate > 60,
        })
    summary.sort(key=lambda x: (x["accountability_flag"], x["open_issues"]), reverse=True)
    flagged = [s for s in summary if s["accountability_flag"]]
    return {
        "total_entries": len(summary),
        "flagged_entries": len(flagged),
        "flagged": flagged,
        "all": summary,
    }


# ============================================================
# BATCH 2 LOOPHOLE PATCH: Dispute/Verification + PFI by constituency
# L4: Citizens dispute fake resolutions; auto-reopen at 30% threshold
# L5: CPGRAMS bridge (frontend-only); backend exposes cpgrams flag
# ============================================================

@api_router.post("/issues/{issue_id}/proof")
async def submit_resolution_proof(
    issue_id: str,
    note: str = Form(None),
    reason: str = Form(None),
    proof_type: str = Form("verification"),  # 'verification' | 'dispute'
    files: List[UploadFile] = File([]),
    current_user: dict = Depends(get_current_user)
):
    """L4 FIX: Citizens verify or dispute resolutions. 30% (min 3) disputes auto-reopen."""
    issue = await db.issues.find_one({"id": issue_id})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.get("status") != "resolved":
        raise HTTPException(status_code=400, detail="Issue is not marked as resolved")

    # 7-day dispute window
    if proof_type == "dispute":
        resolved_at = issue.get("resolved_at")
        if resolved_at:
            try:
                resolved_dt = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
                if resolved_dt.tzinfo is None:
                    resolved_dt = resolved_dt.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(timezone.utc) - resolved_dt).days
                if days_since > 7:
                    raise HTTPException(
                        status_code=400,
                        detail="Dispute window has closed (7 days after resolution)"
                    )
            except ValueError:
                pass
        existing = await db.resolution_proofs.find_one({
            "issue_id": issue_id,
            "user_id": current_user["id"],
            "type": "dispute"
        })
        if existing:
            raise HTTPException(status_code=400, detail="You have already disputed this resolution")

    # Save uploaded files (max 3)
    saved_urls = []
    for f in (files or [])[:3]:
        if f and f.filename:
            safe_name = f.filename.replace(" ", "_")
            file_path = UPLOAD_DIR / f"proof_{issue_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
            content = await f.read()
            with open(file_path, "wb") as out:
                out.write(content)
            saved_urls.append(f"/uploads/{file_path.name}")

    proof_doc = {
        "id": str(uuid.uuid4()),
        "issue_id": issue_id,
        "user_id": current_user["id"],
        "user_district": current_user.get("district"),
        "type": proof_type,
        "note": note or reason or "",
        "file_urls": saved_urls,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.resolution_proofs.insert_one(proof_doc)

    reopened = False
    if proof_type == "dispute":
        new_dispute_count = (issue.get("dispute_count") or 0) + 1
        support_count = issue.get("support_count") or 0
        dispute_threshold = max(3, int(support_count * 0.3))
        update_data = {"dispute_count": new_dispute_count}
        if new_dispute_count >= dispute_threshold:
            update_data["status"] = "area_concern"
            update_data["dispute_reopened"] = True
            update_data["dispute_reopened_at"] = datetime.now(timezone.utc).isoformat()
            update_data["resolved_at"] = None
            reopened = True
            await create_notification(
                issue["user_id"],
                "Issue Reopened — Resolution Disputed",
                "பிரச்சனை மீண்டும் திறக்கப்பட்டது — தீர்வு மறுக்கப்பட்டது",
                f"Your issue in {issue.get('district')} was reopened because {new_dispute_count} citizens disputed the resolution.",
                f"{new_dispute_count} குடிமக்கள் தீர்வை எதிர்த்ததால் உங்கள் பிரச்சனை மீண்டும் திறக்கப்பட்டது.",
                "dispute_reopen",
                issue_id,
            )
            await notify_user_with_sms(issue["user_id"], "dispute_reopen", {
                "district": issue.get("district", ""),
                "url": f"{os.environ.get('FRONTEND_URL', '')}/issues/{issue_id}",
            })
        await db.issues.update_one({"id": issue_id}, {"$set": update_data})
    else:
        await db.issues.update_one({"id": issue_id}, {"$inc": {"proof_count": 1}})

    return {
        "success": True,
        "type": proof_type,
        "message": "Dispute submitted — issue will reopen if threshold is reached" if proof_type == "dispute" else "Verification recorded — thank you!",
        "dispute_count": (issue.get("dispute_count") or 0) + (1 if proof_type == "dispute" else 0),
        "dispute_threshold": max(3, int((issue.get("support_count") or 0) * 0.3)),
        "reopened": reopened,
    }


@api_router.get("/issues/{issue_id}/proofs")
async def get_resolution_proofs(issue_id: str):
    """Get all verification/dispute proofs for an issue (anonymized)."""
    proofs = await db.resolution_proofs.find(
        {"issue_id": issue_id}, {"_id": 0, "user_id": 0}
    ).sort("created_at", -1).to_list(100)
    verifications = [p for p in proofs if p.get("type") == "verification"]
    disputes = [p for p in proofs if p.get("type") == "dispute"]
    return {
        "total": len(proofs),
        "verifications": verifications,
        "disputes": disputes,
    }


# ---- PFI by constituency ----
async def calculate_pfi_score_filtered(district: str, category: str, constituency: Optional[str] = None) -> float:
    """PFI score with optional constituency filter."""
    base_q = {"district": district, "category": category}
    if constituency:
        base_q["constituency"] = constituency

    unresolved = await db.issues.count_documents({**base_q, "status": {"$ne": "resolved"}})
    resolved = await db.issues.count_documents({**base_q, "status": "resolved"})
    six_months_ago = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    repeat_issues = await db.issues.count_documents({**base_q, "created_at": {"$gte": six_months_ago}})
    score = (unresolved * 10) + (repeat_issues * 2) - (resolved * 3)
    return max(0, min(100, score))


@api_router.get("/pfi/constituency")
async def get_constituency_pfi(district: str, constituency: str):
    """Get PFI breakdown for a specific constituency within a district."""
    if district not in TAMIL_NADU_DISTRICTS:
        raise HTTPException(status_code=400, detail="Invalid district")
    valid_constituencies = get_constituencies_by_district(district)
    if constituency not in valid_constituencies:
        raise HTTPException(status_code=400, detail="Invalid constituency for this district")

    pfi_scores = {}
    total_score = 0
    for cat_key in PFI_CATEGORIES.keys():
        score = await calculate_pfi_score_filtered(district, cat_key, constituency)
        pfi_scores[cat_key] = {
            "score": score,
            "name_en": PFI_CATEGORIES[cat_key]["name_en"],
            "name_ta": PFI_CATEGORIES[cat_key]["name_ta"],
            "level": "critical" if score >= 70 else "warning" if score >= 40 else "normal",
        }
        total_score += score

    # Top issues per category in this constituency
    category_issues = {}
    for cat_key in PFI_CATEGORIES.keys():
        issues = await db.issues.find(
            {"district": district, "constituency": constituency,
             "category": cat_key, "status": {"$ne": "resolved"}},
            {"_id": 0}
        ).sort("support_count", -1).limit(5).to_list(5)
        category_issues[cat_key] = issues

    return {
        "success": True,
        "district": district,
        "constituency": constituency,
        "overall_score": round(total_score / len(PFI_CATEGORIES), 1),
        "categories": pfi_scores,
        "category_issues": category_issues,
        "calculated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# RTI AUTO-BRIDGE + MAKKAL KURAL AI (L5/L6 — legal teeth)
# ============================================================

RTI_PIO_MAP = {
    "water": "Tamil Nadu Water Supply & Drainage Board (TWAD), Chennai",
    "roads": "Public Works Department Tamil Nadu, Chennai",
    "health": "Directorate of Medical Services Tamil Nadu, Chennai",
    "electricity": "TANGEDCO, Chennai",
    "flooding": "Revenue & Disaster Management Department Tamil Nadu",
    "schools": "Directorate of School Education Tamil Nadu",
    "garbage": "Municipal Administration & Water Supply Department Tamil Nadu",
    "sewage": "TWAD / CMWSSB Tamil Nadu",
    "corruption": "Vigilance & Anti Corruption Directorate (DVAC) Tamil Nadu",
    "transport": "Transport Department Tamil Nadu",
    "pollution": "Tamil Nadu Pollution Control Board (TNPCB)",
    "farming": "Department of Agriculture Tamil Nadu",
    "housing": "Tamil Nadu Housing Board (TNHB)",
    "welfare": "Social Welfare & Women Empowerment Department Tamil Nadu",
    "employment": "Labour & Employment Department Tamil Nadu",
    "public_safety": "Tamil Nadu Police, Office of DGP, Chennai",
}


async def _llm_chat_text(system_msg: str, user_msg: str, model: str = "gpt-4o-mini") -> str:
    """Helper: single-turn LLM call via emergentintegrations. Returns text or ''."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return ""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        provider = "anthropic" if model.startswith("claude") else "openai"
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message=system_msg,
        ).with_model(provider, model)
        resp = await chat.send_message(UserMessage(text=user_msg))
        return str(resp).strip() if resp else ""
    except Exception as e:
        logger.error(f"[LLM error] {e}")
        return ""


@api_router.post("/issues/{issue_id}/generate-rti")
async def generate_rti(
    issue_id: str,
    request: RTIGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """L5 FIX: AI-generated, legally precise RTI for unresolved issue."""
    issue = await db.issues.find_one({"id": issue_id}, {"_id": 0})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.get("status") == "resolved":
        raise HTTPException(status_code=400, detail="Issue is already resolved")

    try:
        created_dt = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=timezone.utc)
        days_unresolved = (datetime.now(timezone.utc) - created_dt).days
    except (ValueError, KeyError):
        days_unresolved = 0

    pio_dept = RTI_PIO_MAP.get(
        (issue.get("category") or "").lower(),
        "Concerned State Department, Secretariat, Chennai"
    )
    today = datetime.now(timezone.utc).strftime("%d-%m-%Y")

    results = {"pio_dept": pio_dept, "days_unresolved": days_unresolved}

    if request.language in ("en", "both"):
        en_prompt = (
            f"Write a legally precise RTI application under the Right to Information Act 2005 for Tamil Nadu.\n"
            f"Category: {issue.get('category')}. Location: {issue.get('local_body_name')}, "
            f"{issue.get('ward', 'N/A')}, {issue.get('district')}. "
            f"Description: {issue.get('description')}. Days unresolved: {days_unresolved}. "
            f"Citizens supporting: {issue.get('support_count', 0)}. Platform Issue ID: {issue_id}. "
            f"Date filed: {(issue.get('created_at', '') or '')[:10]}. Responsible PIO: {pio_dept}.\n\n"
            f"Address to PIO of {pio_dept}. Ask 6 specific factual questions about action taken, budget "
            f"allocated/spent, similar complaints in past 2 years and resolution rate, SLA timeline, contractor "
            f"details (work order, name, amount), and reason for {days_unresolved}-day delay. "
            f"Formal letter: subject line, salutation, numbered questions, signature placeholder, date {today}. "
            f"Plain text only — no markdown, asterisks, or bullets. Keep under 2800 characters."
        )
        results["rti_english"] = await _llm_chat_text(
            "You are an expert in Indian RTI law and Tamil Nadu governance. Write precise, legally sound RTI applications.",
            en_prompt,
        )

    if request.language in ("ta", "both"):
        ta_prompt = (
            f"தமிழ்நாட்டில் தகவல் அறியும் உரிமை சட்டம் 2005 இன் படி RTI விண்ணப்பம் எழுதுங்கள்.\n"
            f"வகை: {issue.get('category')}. இடம்: {issue.get('local_body_name')}, "
            f"{issue.get('ward', 'N/A')}, {issue.get('district')}. "
            f"விவரம்: {issue.get('description')}. தீர்க்கப்படாத நாட்கள்: {days_unresolved}. "
            f"ஆதரிக்கும் குடிமக்கள்: {issue.get('support_count', 0)}.\n\n"
            f"{pio_dept} PIO-க்கு முறையான கடித வடிவத்தில் 6 குறிப்பிட்ட கேள்விகள் கேளுங்கள் "
            f"(நடவடிக்கை, ஒதுக்கப்பட்ட நிதி, கடந்த 2 ஆண்டுகளில் இதுபோன்ற புகார்கள், கெடு, "
            f"ஒப்பந்தக்காரர் விவரம், தாமதத்தின் காரணம்). தேதி: {today}. "
            f"Markdown அல்லது * பயன்படுத்தாதீர்கள் — தெளிவான தமிழ் உரை மட்டும். 2800 எழுத்துகளுக்கு குறைவாக."
        )
        results["rti_tamil"] = await _llm_chat_text(
            "நீங்கள் இந்திய RTI சட்டம் மற்றும் தமிழ்நாடு ஆட்சி நிர்வாகத்தில் நிபுணர். தெளிவான தமிழில் RTI விண்ணப்பங்கள் எழுதுங்கள்.",
            ta_prompt,
        )

    await db.rti_generations.insert_one({
        "id": str(uuid.uuid4()),
        "issue_id": issue_id,
        "user_id": current_user["id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "language": request.language,
        "pio_dept": pio_dept,
    })
    results["success"] = True
    return results


@api_router.post("/issues/{issue_id}/rtis")
async def save_rti_registration(
    issue_id: str,
    request: RTISaveRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save RTI registration number filed by citizen. 30-day deadline tracked."""
    issue = await db.issues.find_one({"id": issue_id}, {"_id": 0})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    reg = request.registration_number.strip()
    if len(reg) < 5:
        raise HTTPException(status_code=400, detail="Invalid registration number")

    existing = await db.issue_rtis.find_one({"registration_number": reg})
    if existing:
        raise HTTPException(status_code=400, detail="This registration number is already saved")

    filed_at = request.filed_at or datetime.now(timezone.utc).isoformat()
    try:
        filed_dt = datetime.fromisoformat(filed_at.replace("Z", "+00:00"))
        if filed_dt.tzinfo is None:
            filed_dt = filed_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        filed_dt = datetime.now(timezone.utc)
    response_deadline = (filed_dt + timedelta(days=30)).isoformat()

    rti_doc = {
        "id": str(uuid.uuid4()),
        "issue_id": issue_id,
        "user_id": current_user["id"],
        "registration_number": reg,
        "pio_dept": request.pio_dept or "",
        "language": request.language,
        "filed_at": filed_at,
        "response_deadline": response_deadline,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.issue_rtis.insert_one(rti_doc)
    await db.issues.update_one(
        {"id": issue_id},
        {"$set": {"has_rti": True}, "$inc": {"rti_count": 1}}
    )

    if issue.get("user_id") != current_user["id"]:
        await create_notification(
            issue["user_id"],
            "RTI Filed on Your Issue",
            "உங்கள் பிரச்சனைக்கு RTI தாக்கல்",
            f"A citizen filed an RTI (Reg: {reg}) for your issue in {issue.get('district')}. Government must respond within 30 days.",
            f"உங்கள் {issue.get('district')} பிரச்சனைக்கு RTI ({reg}) தாக்கல் செய்யப்பட்டது. 30 நாட்களுக்குள் அரசு பதில் கொடுக்க வேண்டும்.",
            "rti_filed",
            issue_id,
        )

    rti_doc.pop("_id", None)
    return {"success": True, "rti": rti_doc, "response_deadline": response_deadline}


@api_router.get("/issues/{issue_id}/rtis")
async def get_issue_rtis(issue_id: str):
    """Public: all RTIs filed for an issue with overdue status."""
    rtis = await db.issue_rtis.find(
        {"issue_id": issue_id}, {"_id": 0, "user_id": 0}
    ).sort("filed_at", -1).to_list(50)

    now = datetime.now(timezone.utc)
    for rti in rtis:
        try:
            deadline = datetime.fromisoformat(rti.get("response_deadline", now.isoformat()).replace("Z", "+00:00"))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
        except ValueError:
            deadline = now
        rti["is_overdue"] = now > deadline and rti.get("status") == "pending"
        rti["days_overdue"] = max(0, (now - deadline).days) if rti["is_overdue"] else 0
    return {"rtis": rtis, "total": len(rtis)}


# ---- Makkal Kural AI Chatbot ----
MAKKAL_KURAL_AI_SYSTEM = """You are Makkal Kural AI (மக்கள் குரல் AI), a Tamil Nadu civic governance assistant.

LANGUAGE:
- If user writes in Tamil, respond primarily in Tamil with English terms where needed.
- If user writes in English, respond in English. Keep language simple — rural users.

KNOWLEDGE:
- TN hierarchy: VAO (கிராம நிர்வாக அலுவலர்) → BDO → District Collector → Dept Secretary → Minister → CS → CM
- 38 TN districts, 234 assembly constituencies
- RTI Act 2005: rtionline.tn.gov.in, 30-day mandate, Rs.10 fee, Tamil accepted
- CPGRAMS (pgportal.gov.in): central govt, 21-day mandate
- Issue categories: Water, Roads, Health, Electricity, Flooding, Pollution, Schools, Farming, Transport, Garbage, Sewage, Employment, Housing, Welfare, Corruption, Public Safety
- Central vs State: Railways/NHAI/Central banks = Central; TANGEDCO/PWD/Corporation = State
- Auto-escalation: 25+ supporters = Area Concern, 75%+ support + 25 votes = escalate level
- SLA: VAO=7d, BDO=14d, Collector=30d, Secretary=45d, Minister=60d, CS=75d, CM=90d
- Anonymous reporting available for corruption/safety
- Resolution disputes: citizens can dispute within 7 days

HELP WITH: raising issues, RTI/CPGRAMS guidance, jurisdiction (state vs central), description drafting,
escalation paths, rights, dispute process.

AVOID: legal promises, illegal advice, naming politicians, sharing phone numbers.

TONE: Supportive, clear, empowering. Keep responses under 200 words unless detail requested.
Always end with a specific actionable next step."""


@api_router.post("/ai/chat")
async def makkal_kural_ai_chat(req: AIChatRequest):
    """Makkal Kural AI civic assistant powered by Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)

        lang_hint = "[User language: Tamil — respond primarily in Tamil]" if req.language == "ta" else "[User language: English — respond in English]"
        full_msg = f"{lang_hint}\n\n{req.message}"

        # Build history for multi-turn
        history_msgs = []
        for h in (req.history or [])[-10:]:  # last 10 turns
            if h.get("role") in ("user", "assistant") and h.get("content"):
                history_msgs.append({"role": h["role"], "content": h["content"]})
        history_msgs.append({"role": "user", "content": full_msg})

        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=MAKKAL_KURAL_AI_SYSTEM,
            messages=history_msgs,
        )
        reply = response.content[0].text.strip()

        await db.ai_chat_log.insert_one({
            "id": str(uuid.uuid4()),
            "session_id": req.session_id,
            "user_message": req.message[:500],
            "ai_reply": reply[:2000],
            "language": req.language,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        return {"success": True, "reply": reply, "session_id": req.session_id}
    except Exception as e:
        logger.error(f"[AI chat error] {e}")
        raise HTTPException(status_code=500, detail="AI temporarily unavailable")


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
