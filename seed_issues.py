"""
Seed script to populate Makkal Kural with realistic Tamil Nadu issues
Run: python seed_issues.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import uuid
import random
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'makkal_kural')]

ESCALATION_HIERARCHY = [
    {"level": 1, "role_en": "Village Administrative Officer (VAO) / Ward Officer", "role_ta": "கிராம நிர்வாக அலுவலர் / வார்டு அலுவலர்", "sla_days": 7},
    {"level": 2, "role_en": "Block Development Officer (BDO) / Zonal Officer", "role_ta": "வட்டார வளர்ச்சி அலுவலர் / மண்டல அலுவலர்", "sla_days": 14},
    {"level": 3, "role_en": "District Collector", "role_ta": "மாவட்ட ஆட்சியர்", "sla_days": 21},
    {"level": 4, "role_en": "Concerned Department Secretary", "role_ta": "சம்பந்தப்பட்ட துறை செயலாளர்", "sla_days": 30},
    {"level": 5, "role_en": "Concerned Minister", "role_ta": "சம்பந்தப்பட்ட அமைச்சர்", "sla_days": 45},
]

# Real issues from Tamil Nadu
SEED_ISSUES = [
    # DRINKING WATER ISSUES
    {
        "category": "water",
        "problem_id": "no_water",
        "problem_name_en": "Irregular water supply",
        "problem_name_ta": "ஒழுங்கற்ற நீர் வழங்கல்",
        "description": "Water supply comes only once in 15-20 days. Families are forced to buy expensive tanker water. This has been going on for over 6 months. The municipality has not responded to our repeated complaints.",
        "description_ta": "நீர் வழங்கல் 15-20 நாட்களுக்கு ஒருமுறை மட்டுமே வருகிறது. குடும்பங்கள் விலை உயர்ந்த டேங்கர் தண்ணீர் வாங்க வேண்டிய நிர்பந்தத்தில் உள்ளனர். இது 6 மாதங்களுக்கும் மேலாக நடந்து வருகிறது.",
        "districts": ["Chennai", "Chengalpattu", "Kancheepuram", "Ariyalur", "Cuddalore"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "months",
        "support_range": (45, 180),
        "oppose_range": (5, 25)
    },
    {
        "category": "water",
        "problem_id": "contaminated",
        "problem_name_en": "Groundwater contamination",
        "problem_name_ta": "நிலத்தடி நீர் மாசுபாடு",
        "description": "The groundwater in our area contains heavy metals and industrial waste. Many children have developed skin diseases. The water testing report shows dangerous levels of arsenic and lead. We need immediate action.",
        "description_ta": "எங்கள் பகுதியில் நிலத்தடி நீரில் கனரக உலோகங்கள் மற்றும் தொழிற்சாலை கழிவுகள் உள்ளன. பல குழந்தைகளுக்கு தோல் நோய்கள் வந்துள்ளன.",
        "districts": ["Erode", "Karur", "Coimbatore", "Krishnagiri", "Madurai"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (80, 250),
        "oppose_range": (3, 15)
    },
    {
        "category": "water",
        "problem_id": "tanker",
        "problem_name_en": "Tanker dependency - High costs",
        "problem_name_ta": "டேங்கர் சார்பு - அதிக செலவு",
        "description": "We spend Rs. 2000-3000 per month on private tanker water because municipal supply is unreliable. Poor families cannot afford this. The tanker mafia is exploiting the situation.",
        "description_ta": "நகராட்சி வழங்கல் நம்பகமற்றதாக இருப்பதால் தனியார் டேங்கர் தண்ணீருக்கு மாதம் ரூ.2000-3000 செலவிடுகிறோம்.",
        "districts": ["Chennai", "Madurai", "Coimbatore", "Dharmapuri", "Dindigul"],
        "frequency": "weekly",
        "affected_people": "50-500",
        "duration": "months",
        "support_range": (30, 120),
        "oppose_range": (5, 20)
    },
    
    # INDUSTRIAL POLLUTION
    {
        "category": "pollution",
        "problem_id": "water_pollution",
        "problem_name_en": "Textile dyeing unit dumping untreated waste",
        "problem_name_ta": "துணி சாயப்பட்டறை சுத்திகரிக்கப்படாத கழிவுகளை கொட்டுதல்",
        "description": "The textile dyeing units near our village are dumping untreated chemical waste into the river. The water has turned red/blue and fish are dying. Farmers cannot use this water for irrigation anymore.",
        "description_ta": "எங்கள் கிராமத்திற்கு அருகிலுள்ள துணி சாயப்பட்டறைகள் சுத்திகரிக்கப்படாத ரசாயன கழிவுகளை ஆற்றில் கொட்டுகின்றன. தண்ணீர் சிவப்பு/நீல நிறமாக மாறி மீன்கள் இறக்கின்றன.",
        "districts": ["Erode", "Karur", "Cuddalore", "Chengalpattu"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (100, 300),
        "oppose_range": (10, 30)
    },
    {
        "category": "pollution",
        "problem_id": "air",
        "problem_name_en": "SIPCOT industrial zone toxic fumes",
        "problem_name_ta": "SIPCOT தொழில்பேட்டை நச்சு புகை",
        "description": "The SIPCOT industrial area releases toxic fumes especially at night. Many residents suffer from respiratory problems. Children have developed asthma. The pollution control board ignores our complaints.",
        "description_ta": "SIPCOT தொழிற்பகுதி குறிப்பாக இரவில் நச்சு புகையை வெளியிடுகிறது. பல குடியிருப்பாளர்கள் சுவாச பிரச்சனைகளால் அவதிப்படுகின்றனர்.",
        "districts": ["Cuddalore", "Chengalpattu", "Chennai", "Madurai"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (120, 350),
        "oppose_range": (5, 20)
    },
    
    # FLOODING & DRAINAGE
    {
        "category": "flooding",
        "problem_id": "drainage",
        "problem_name_en": "Sewage mixing with rainwater flooding",
        "problem_name_ta": "கழிவுநீர் மழைநீருடன் கலந்து வெள்ளம்",
        "description": "Every monsoon, our area gets flooded with sewage-mixed water. The drainage system is completely blocked. Houses get waterlogged for days. Disease outbreaks are common. We need proper stormwater drains.",
        "description_ta": "ஒவ்வொரு மழைக்காலத்திலும் எங்கள் பகுதி கழிவுநீர் கலந்த தண்ணீரால் வெள்ளத்தில் மூழ்குகிறது. வடிகால் அமைப்பு முற்றிலும் அடைபட்டுள்ளது.",
        "districts": ["Chennai", "Chengalpattu", "Mayiladuthurai", "Coimbatore"],
        "frequency": "seasonal",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (150, 400),
        "oppose_range": (10, 35)
    },
    {
        "category": "flooding",
        "problem_id": "waterlogging",
        "problem_name_en": "Weak embankments causing floods",
        "problem_name_ta": "பலவீனமான கரைகள் வெள்ளத்தை ஏற்படுத்துகின்றன",
        "description": "The river embankments are weak and breach every year during monsoon. Agricultural lands get submerged. Crops worth lakhs are destroyed. The PWD has not strengthened the bunds despite repeated requests.",
        "description_ta": "ஆற்றுக் கரைகள் பலவீனமாக உள்ளன, ஒவ்வொரு மழைக்காலத்திலும் உடைகின்றன. விவசாய நிலங்கள் மூழ்குகின்றன.",
        "districts": ["Ariyalur", "Mayiladuthurai", "Cuddalore", "Chengalpattu"],
        "frequency": "seasonal",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (80, 200),
        "oppose_range": (5, 15)
    },
    
    # SANITATION & WASTE
    {
        "category": "garbage",
        "problem_id": "no_collection",
        "problem_name_en": "Garbage piling up on streets",
        "problem_name_ta": "குப்பை தெருக்களில் குவிகிறது",
        "description": "Garbage has not been collected for the past 3 weeks. The corporation workers are on strike but no alternative arrangement made. The stench is unbearable and stray dogs are spreading waste everywhere.",
        "description_ta": "கடந்த 3 வாரங்களாக குப்பை சேகரிக்கப்படவில்லை. மாநகராட்சி தொழிலாளர்கள் வேலைநிறுத்தத்தில் உள்ளனர் ஆனால் மாற்று ஏற்பாடு இல்லை.",
        "districts": ["Chennai", "Madurai", "Coimbatore", "Cuddalore", "Kancheepuram"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "weeks",
        "support_range": (60, 180),
        "oppose_range": (8, 25)
    },
    {
        "category": "sewage",
        "problem_id": "overflow",
        "problem_name_en": "Hospital medical waste mismanagement",
        "problem_name_ta": "மருத்துவமனை மருத்துவ கழிவு மேலாண்மை தோல்வி",
        "description": "The government hospital is dumping biomedical waste along with regular garbage. Used syringes and blood-soaked bandages are visible in the open dump. This is a serious health hazard for nearby residents.",
        "description_ta": "அரசு மருத்துவமனை உயிர்மருத்துவ கழிவுகளை சாதாரண குப்பையுடன் சேர்த்து கொட்டுகிறது. பயன்படுத்திய ஊசிகள் தெரிகின்றன.",
        "districts": ["Chennai", "Karur", "Cuddalore", "Krishnagiri"],
        "frequency": "daily",
        "affected_people": "50-500",
        "duration": "months",
        "support_range": (90, 220),
        "oppose_range": (5, 18)
    },
    
    # AGRICULTURAL CRISIS
    {
        "category": "farming",
        "problem_id": "water_shortage",
        "problem_name_en": "Drought and irrigation delays",
        "problem_name_ta": "வறட்சி மற்றும் நீர்ப்பாசன தாமதங்கள்",
        "description": "The irrigation canal project promised 5 years ago is still incomplete. Farmers are entirely dependent on monsoon. Three consecutive drought years have pushed many into debt. Farmer suicides are increasing.",
        "description_ta": "5 ஆண்டுகளுக்கு முன் உறுதியளிக்கப்பட்ட நீர்ப்பாசன கால்வாய் திட்டம் இன்னும் முடிக்கப்படவில்லை. விவசாயிகள் முற்றிலும் பருவமழையை சார்ந்துள்ளனர்.",
        "districts": ["Dharmapuri", "Krishnagiri", "Dindigul", "Erode", "Mayiladuthurai"],
        "frequency": "seasonal",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (200, 500),
        "oppose_range": (15, 40)
    },
    {
        "category": "farming",
        "problem_id": "crop_damage",
        "problem_name_en": "Mango price crash - Farmers in distress",
        "problem_name_ta": "மாம்பழ விலை வீழ்ச்சி - விவசாயிகள் துயரத்தில்",
        "description": "Mango prices have crashed to Rs.5/kg while production cost is Rs.15/kg. No government procurement or minimum support price. Farmers are dumping mangoes on roads in protest. Need immediate intervention.",
        "description_ta": "மாம்பழ விலை கிலோவுக்கு ரூ.5-க்கு வீழ்ச்சியடைந்துள்ளது, உற்பத்தி செலவு ரூ.15/கிலோ. அரசு கொள்முதல் அல்லது குறைந்தபட்ச ஆதார விலை இல்லை.",
        "districts": ["Krishnagiri", "Dharmapuri", "Dindigul"],
        "frequency": "seasonal",
        "affected_people": "entire_area",
        "duration": "weeks",
        "support_range": (150, 380),
        "oppose_range": (10, 30)
    },
    {
        "category": "farming",
        "problem_id": "other",
        "problem_name_en": "Elephant-human conflict destroying crops",
        "problem_name_ta": "யானை-மனித மோதல் பயிர்களை அழிக்கிறது",
        "description": "Wild elephants from the forest area frequently raid our village at night and destroy standing crops. Two farmers were killed last year. The forest department provides no compensation. We need elephant-proof trenches.",
        "description_ta": "காட்டு யானைகள் அடிக்கடி இரவில் எங்கள் கிராமத்தை தாக்கி நிற்கும் பயிர்களை அழிக்கின்றன. கடந்த ஆண்டு இரண்டு விவசாயிகள் கொல்லப்பட்டனர்.",
        "districts": ["Dharmapuri", "Krishnagiri", "Erode", "Coimbatore"],
        "frequency": "weekly",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (180, 420),
        "oppose_range": (8, 25)
    },
    
    # HEALTHCARE
    {
        "category": "health",
        "problem_id": "no_doctors",
        "problem_name_en": "Government hospital - No doctors available",
        "problem_name_ta": "அரசு மருத்துவமனை - மருத்துவர்கள் இல்லை",
        "description": "The taluk hospital has only 2 doctors for 5 lakh population. Most specialists posts are vacant for years. Patients have to travel 50km to the district hospital for basic treatment. Emergency cases often die on the way.",
        "description_ta": "தாலுகா மருத்துவமனையில் 5 லட்சம் மக்கள் தொகைக்கு 2 மருத்துவர்கள் மட்டுமே. பெரும்பாலான நிபுணர் பதவிகள் பல ஆண்டுகளாக காலியாக உள்ளன.",
        "districts": ["Karur", "Cuddalore", "Ariyalur", "Krishnagiri", "Dharmapuri"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (250, 600),
        "oppose_range": (12, 35)
    },
    {
        "category": "health",
        "problem_id": "medicines",
        "problem_name_en": "Essential medicines not available in PHC",
        "problem_name_ta": "PHC-யில் அத்தியாவசிய மருந்துகள் இல்லை",
        "description": "The Primary Health Center has no stock of basic medicines like paracetamol, antibiotics, or diabetes medicines. Patients are given prescription to buy from private shops. The free medicine scheme exists only on paper.",
        "description_ta": "ஆரம்ப சுகாதார நிலையத்தில் பாராசிட்டமால், நுண்ணுயிர் எதிர்ப்பிகள் அல்லது நீரிழிவு மருந்துகள் போன்ற அடிப்படை மருந்துகள் கையிருப்பு இல்லை.",
        "districts": ["Dindigul", "Erode", "Mayiladuthurai", "Cuddalore"],
        "frequency": "weekly",
        "affected_people": "entire_area",
        "duration": "months",
        "support_range": (80, 200),
        "oppose_range": (6, 20)
    },
    
    # ROADS & TRANSPORT
    {
        "category": "roads",
        "problem_id": "potholes",
        "problem_name_en": "Broken rural roads - Accidents daily",
        "problem_name_ta": "உடைந்த கிராம சாலைகள் - தினமும் விபத்துகள்",
        "description": "The village road has massive potholes and is completely broken. Two-wheelers fall daily. An ambulance got stuck last month and the patient died. The road was laid just 2 years ago with substandard material.",
        "description_ta": "கிராம சாலையில் பெரிய குழிகள் உள்ளன, முற்றிலும் உடைந்துள்ளது. இரு சக்கர வாகனங்கள் தினமும் விழுகின்றன. கடந்த மாதம் ஆம்புலன்ஸ் சிக்கி நோயாளி இறந்தார்.",
        "districts": ["Ariyalur", "Karur", "Dharmapuri", "Erode", "Chengalpattu"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (100, 280),
        "oppose_range": (8, 22)
    },
    {
        "category": "transport",
        "problem_id": "no_bus",
        "problem_name_en": "Bus services skipping villages",
        "problem_name_ta": "பேருந்து சேவைகள் கிராமங்களை தவிர்க்கின்றன",
        "description": "Government buses don't enter our village anymore. Students have to walk 5km to reach the bus stop. Senior citizens cannot access healthcare. Private autos charge Rs.100 for short distances.",
        "description_ta": "அரசு பேருந்துகள் இனி எங்கள் கிராமத்திற்குள் வருவதில்லை. மாணவர்கள் பேருந்து நிறுத்தத்தை அடைய 5 கி.மீ நடக்க வேண்டும்.",
        "districts": ["Ariyalur", "Dharmapuri", "Kallakurichi", "Krishnagiri"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "months",
        "support_range": (70, 180),
        "oppose_range": (5, 15)
    },
    
    # DEVELOPMENT PROJECTS
    {
        "category": "housing",
        "problem_id": "no_house",
        "problem_name_en": "PMAY houses incomplete for 4 years",
        "problem_name_ta": "PMAY வீடுகள் 4 ஆண்டுகளாக முடிக்கப்படவில்லை",
        "description": "We were sanctioned houses under PMAY scheme 4 years ago. Only foundation was laid. Funds were released but contractor disappeared. Officials demand bribe to restart construction. 50 families still living in huts.",
        "description_ta": "4 ஆண்டுகளுக்கு முன் PMAY திட்டத்தின் கீழ் வீடுகள் ஒதுக்கப்பட்டன. அடித்தளம் மட்டுமே போடப்பட்டது. நிதி வெளியிடப்பட்டது ஆனால் ஒப்பந்ததாரர் காணாமல் போனார்.",
        "districts": ["Kallakurichi", "Dharmapuri", "Ariyalur", "Cuddalore"],
        "frequency": "daily",
        "affected_people": "50-500",
        "duration": "years",
        "support_range": (90, 240),
        "oppose_range": (6, 18)
    },
    {
        "category": "corruption",
        "problem_id": "bribery",
        "problem_name_en": "Bribery for basic services at Taluk office",
        "problem_name_ta": "தாலுகா அலுவலகத்தில் அடிப்படை சேவைகளுக்கு லஞ்சம்",
        "description": "Getting any certificate from the Taluk office requires Rs.500-2000 bribe. Community certificate takes months without bribe but 2 days with bribe. Even pension applications need middlemen who charge fees.",
        "description_ta": "தாலுகா அலுவலகத்தில் எந்த சான்றிதழ் பெறவும் ரூ.500-2000 லஞ்சம் தேவை. சமூக சான்றிதழ் லஞ்சம் இல்லாமல் மாதங்கள் ஆகும் ஆனால் லஞ்சத்துடன் 2 நாட்கள்.",
        "districts": ["Chennai", "Madurai", "Coimbatore", "Erode", "Cuddalore"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (200, 500),
        "oppose_range": (20, 50)
    },
    
    # UNEMPLOYMENT
    {
        "category": "employment",
        "problem_id": "no_jobs",
        "problem_name_en": "Youth unemployment - No local jobs",
        "problem_name_ta": "இளைஞர் வேலையின்மை - உள்ளூர் வேலைகள் இல்லை",
        "description": "Despite having a degree, no jobs available in our district. Youth have to migrate to Chennai/Bangalore. SIPCOT industrial area promised jobs but hired only outsiders. Skill training programs exist only on paper.",
        "description_ta": "பட்டம் பெற்றிருந்தாலும் எங்கள் மாவட்டத்தில் வேலைகள் இல்லை. இளைஞர்கள் சென்னை/பெங்களூருக்கு இடம்பெயர வேண்டும்.",
        "districts": ["Krishnagiri", "Dharmapuri", "Dindigul", "Ariyalur"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (180, 450),
        "oppose_range": (15, 40)
    },
    
    # TRIBAL & RURAL NEGLECT
    {
        "category": "schools",
        "problem_id": "infrastructure",
        "problem_name_en": "Tribal village - No school within 10km",
        "problem_name_ta": "பழங்குடி கிராமம் - 10 கி.மீ-க்குள் பள்ளி இல்லை",
        "description": "Our tribal hamlet has no school within 10km. Children have to cross a river and walk through forest to reach school. During monsoon, children cannot attend for months. No school bus service provided.",
        "description_ta": "எங்கள் பழங்குடி குடியிருப்புக்கு 10 கி.மீ-க்குள் பள்ளி இல்லை. குழந்தைகள் ஆற்றைக் கடந்து காட்டின் வழியாக நடந்து பள்ளிக்கு செல்ல வேண்டும்.",
        "districts": ["Dharmapuri", "Kallakurichi", "Krishnagiri", "Erode"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (150, 350),
        "oppose_range": (8, 22)
    },
    {
        "category": "safety",
        "problem_id": "street_lights",
        "problem_name_en": "No street lights - Women safety concern",
        "problem_name_ta": "தெரு விளக்குகள் இல்லை - பெண்கள் பாதுகாப்பு கவலை",
        "description": "Our area has no street lights for over 2 years. Women are afraid to go out after dark. Two chain snatching incidents happened last month. The electricity board says funds not sanctioned.",
        "description_ta": "எங்கள் பகுதியில் 2 ஆண்டுகளுக்கும் மேலாக தெரு விளக்குகள் இல்லை. இருட்டிய பின் பெண்கள் வெளியே செல்ல பயப்படுகிறார்கள்.",
        "districts": ["Chennai", "Madurai", "Coimbatore", "Chengalpattu", "Cuddalore"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "years",
        "support_range": (120, 300),
        "oppose_range": (10, 28)
    },
    {
        "category": "electricity",
        "problem_id": "frequent_cuts",
        "problem_name_en": "Power cuts 8-10 hours daily",
        "problem_name_ta": "தினமும் 8-10 மணி நேர மின்வெட்டு",
        "description": "We face 8-10 hours of power cuts daily, especially during summer. Agriculture pump sets cannot be operated. Small businesses are shutting down. The transformer is overloaded but not replaced.",
        "description_ta": "குறிப்பாக கோடையில் தினமும் 8-10 மணி நேரம் மின்வெட்டு எதிர்கொள்கிறோம். விவசாய பம்ப் செட்களை இயக்க முடியவில்லை.",
        "districts": ["Ariyalur", "Karur", "Dindigul", "Erode", "Dharmapuri"],
        "frequency": "daily",
        "affected_people": "entire_area",
        "duration": "months",
        "support_range": (140, 320),
        "oppose_range": (12, 30)
    },
    
    # WELFARE SCHEMES
    {
        "category": "welfare",
        "problem_id": "not_received",
        "problem_name_en": "Old age pension not received for 8 months",
        "problem_name_ta": "8 மாதங்களாக முதியோர் ஓய்வூதியம் கிடைக்கவில்லை",
        "description": "I am 72 years old. My old age pension of Rs.1000/month has not been credited for 8 months. When I visit the office, they say 'system problem'. I have no other income and depend on this pension for food.",
        "description_ta": "எனக்கு 72 வயது. மாதம் ரூ.1000 முதியோர் ஓய்வூதியம் 8 மாதங்களாக வரவு வைக்கப்படவில்லை. அலுவலகத்திற்கு செல்லும்போது 'சிஸ்டம் பிரச்சனை' என்கிறார்கள்.",
        "districts": ["Dindigul", "Ariyalur", "Krishnagiri", "Cuddalore", "Karur"],
        "frequency": "daily",
        "affected_people": "10-50",
        "duration": "months",
        "support_range": (60, 150),
        "oppose_range": (4, 12)
    },
]

LOCAL_BODIES = {
    "Corporation": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5"],
    "Municipality": ["Ward 1", "Ward 2", "Ward 3", "Ward 4", "Ward 5", "Ward 6"],
    "Town Panchayat": ["Division 1", "Division 2", "Division 3"],
    "Village Panchayat": ["Main Village", "Colony", "Extension"]
}

CITY_NAMES = {
    "Chennai": ["T. Nagar", "Mylapore", "Adyar", "Velachery", "Porur", "Ambattur", "Perambur"],
    "Coimbatore": ["RS Puram", "Gandhipuram", "Peelamedu", "Saibaba Colony", "Town Hall"],
    "Madurai": ["Goripalayam", "Anna Nagar", "Tallakulam", "Simmakkal", "KK Nagar"],
    "Erode": ["Perundurai", "Bhavani", "Gobichettipalayam", "Town Area"],
    "Chengalpattu": ["Tambaram", "Chromepet", "Pallavaram", "Guduvanchery"],
    "default": ["Main Town", "Colony Area", "Village Centre", "Extension Area", "Near Bus Stand"]
}

async def create_users(count=50):
    """Create sample users across different districts"""
    users = []
    districts = ["Chennai", "Coimbatore", "Madurai", "Erode", "Chengalpattu", "Ariyalur", 
                 "Dharmapuri", "Dindigul", "Krishnagiri", "Cuddalore", "Karur", "Kancheepuram",
                 "Mayiladuthurai", "Kallakurichi"]
    
    for i in range(count):
        district = random.choice(districts)
        local_body_type = random.choice(list(LOCAL_BODIES.keys()))
        user = {
            "id": str(uuid.uuid4()),
            "mobile": f"98765{10000 + i:05d}",
            "name": f"Citizen {i+1}",
            "district": district,
            "local_body_type": local_body_type,
            "local_body_name": random.choice(CITY_NAMES.get(district, CITY_NAMES["default"])),
            "ward": random.choice(LOCAL_BODIES[local_body_type]),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "issues_raised": 0,
            "votes_cast": 0
        }
        users.append(user)
    
    if users:
        await db.users.delete_many({})  # Clear existing
        await db.users.insert_many(users)
        print(f"✓ Created {len(users)} sample users")
    
    return users

async def create_issues(users):
    """Create realistic issues based on seed data"""
    issues_created = []
    
    for seed in SEED_ISSUES:
        for district in seed["districts"]:
            # Create 1-3 issues per district for this problem
            for _ in range(random.randint(1, 2)):
                # Find users from this district
                district_users = [u for u in users if u["district"] == district]
                if not district_users:
                    continue
                
                creator = random.choice(district_users)
                local_body_type = random.choice(list(LOCAL_BODIES.keys()))
                local_body_name = random.choice(CITY_NAMES.get(district, CITY_NAMES["default"]))
                
                support_count = random.randint(*seed["support_range"])
                oppose_count = random.randint(*seed["oppose_range"])
                total = support_count + oppose_count
                support_percentage = round((support_count / total) * 100, 1) if total > 0 else 0
                
                # Determine current level based on support
                current_level = 1
                if support_count >= 200 and support_percentage >= 75:
                    current_level = 4
                elif support_count >= 100 and support_percentage >= 60:
                    current_level = 3
                elif support_count >= 50:
                    current_level = 2
                
                # Determine status
                status = "pending"
                if support_count >= 100:
                    status = "serious_issue"
                elif support_count >= 25:
                    status = "area_concern"
                
                # Create escalation history
                created_date = datetime.now(timezone.utc) - timedelta(days=random.randint(7, 90))
                escalation_history = []
                for level in range(1, current_level + 1):
                    level_info = ESCALATION_HIERARCHY[level - 1]
                    level_date = created_date + timedelta(days=level * 7)
                    escalation_history.append({
                        "level": level,
                        "role_en": level_info["role_en"],
                        "role_ta": level_info["role_ta"],
                        "reached_at": level_date.isoformat(),
                        "sla_deadline": (level_date + timedelta(days=level_info["sla_days"])).isoformat(),
                        "auto_escalated": level > 1,
                        "reason": f"Support threshold reached ({support_percentage}%)" if level > 1 else "Initial submission"
                    })
                
                issue = {
                    "id": str(uuid.uuid4()),
                    "user_id": creator["id"],
                    "user_name": creator["name"],
                    "user_mobile": creator["mobile"][-4:],
                    "district": district,
                    "local_body_type": local_body_type,
                    "local_body_name": local_body_name,
                    "ward": random.choice(LOCAL_BODIES[local_body_type]),
                    "street": f"{random.choice(['Main', 'Cross', 'Back'])} Street {random.randint(1, 10)}",
                    "category": seed["category"],
                    "category_name_en": seed["category"].replace("_", " ").title(),
                    "category_name_ta": {
                        "water": "குடிநீர்", "pollution": "மாசுபாடு", "flooding": "வெள்ளம்",
                        "garbage": "குப்பை", "sewage": "கழிவுநீர்", "farming": "விவசாயம்",
                        "health": "சுகாதாரம்", "roads": "சாலைகள்", "transport": "போக்குவரத்து",
                        "housing": "வீட்டுவசதி", "corruption": "ஊழல்", "employment": "வேலைவாய்ப்பு",
                        "schools": "பள்ளிகள்", "safety": "பாதுகாப்பு", "electricity": "மின்சாரம்",
                        "welfare": "நலத்திட்டங்கள்"
                    }.get(seed["category"], seed["category"]),
                    "problem_id": seed["problem_id"],
                    "problem_name_en": seed["problem_name_en"],
                    "problem_name_ta": seed["problem_name_ta"],
                    "description": seed["description"],
                    "voice_note_text": None,
                    "frequency": seed["frequency"],
                    "affected_people": seed["affected_people"],
                    "duration": seed["duration"],
                    "media_urls": [],
                    "status": status,
                    "support_count": support_count,
                    "oppose_count": oppose_count,
                    "support_percentage": support_percentage,
                    "publicly_validated": support_percentage >= 60,
                    "comment_count": random.randint(5, 30),
                    "current_level": current_level,
                    "escalation_history": escalation_history,
                    "created_at": created_date.isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                issues_created.append(issue)
    
    if issues_created:
        await db.issues.delete_many({})  # Clear existing
        await db.issues.insert_many(issues_created)
        print(f"✓ Created {len(issues_created)} sample issues across multiple districts")
    
    return issues_created

async def create_votes(users, issues):
    """Create realistic votes from users"""
    votes = []
    
    for issue in issues:
        # Get users from the same district
        district_users = [u for u in users if u["district"] == issue["district"]]
        
        # Create support votes
        support_needed = issue["support_count"]
        voters = random.sample(district_users, min(support_needed, len(district_users)))
        for voter in voters:
            votes.append({
                "id": str(uuid.uuid4()),
                "user_id": voter["id"],
                "issue_id": issue["id"],
                "vote_type": "support",
                "district": issue["district"],
                "created_at": issue["created_at"]
            })
        
        # Create oppose votes
        oppose_needed = issue["oppose_count"]
        remaining_users = [u for u in district_users if u not in voters]
        opposers = random.sample(remaining_users, min(oppose_needed, len(remaining_users)))
        for opposer in opposers:
            votes.append({
                "id": str(uuid.uuid4()),
                "user_id": opposer["id"],
                "issue_id": issue["id"],
                "vote_type": "oppose",
                "district": issue["district"],
                "created_at": issue["created_at"]
            })
    
    if votes:
        await db.votes.delete_many({})  # Clear existing
        await db.votes.insert_many(votes)
        print(f"✓ Created {len(votes)} votes")
    
    return votes

async def create_comments(users, issues):
    """Create sample comments on issues"""
    sample_comments = [
        "This is affecting my family too. Please resolve urgently!",
        "I have been facing this issue for 2 years. No action taken.",
        "The officials visited once but nothing changed.",
        "My children are suffering because of this problem.",
        "We submitted petition to collector but no response.",
        "This should be escalated to minister level.",
        "The contractor is corrupt. Everyone knows.",
        "We are ready to protest if this is not resolved.",
        "Thank you for raising this. I fully support.",
        "Same problem in my area. Government should wake up."
    ]
    
    comments = []
    for issue in random.sample(issues, min(30, len(issues))):
        num_comments = random.randint(3, 10)
        district_users = [u for u in users if u["district"] == issue["district"]]
        
        for _ in range(min(num_comments, len(district_users))):
            commenter = random.choice(district_users)
            comments.append({
                "id": str(uuid.uuid4()),
                "issue_id": issue["id"],
                "user_id": commenter["id"],
                "user_name": commenter["name"],
                "text": random.choice(sample_comments),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
    
    if comments:
        await db.comments.delete_many({})  # Clear existing
        await db.comments.insert_many(comments)
        print(f"✓ Created {len(comments)} comments")
    
    return comments

async def create_scheme_feedback():
    """Create sample scheme feedback"""
    schemes = [
        {
            "scheme_name": "Pradhan Mantri Awas Yojana (PMAY)",
            "feedback_type": "corrupt",
            "action": "modify",
            "description": "Houses sanctioned but construction stopped midway. Contractor fled with funds. Officials demand bribe to restart.",
            "support_count": 245
        },
        {
            "scheme_name": "Kisan Samman Nidhi",
            "feedback_type": "not_reaching",
            "action": "modify",
            "description": "Many genuine farmers excluded due to land record errors. Banks rejecting applications on technical grounds.",
            "support_count": 180
        },
        {
            "scheme_name": "Free Laptop Scheme for Students",
            "feedback_type": "not_useful",
            "action": "modify",
            "description": "Laptops given are of very poor quality. Most stop working within 6 months. No service centers available.",
            "support_count": 156
        },
        {
            "scheme_name": "MGNREGA",
            "feedback_type": "corrupt",
            "action": "modify",
            "description": "Fake job cards being created. Actual workers not getting full wages. Payment delayed by 4-6 months.",
            "support_count": 312
        },
        {
            "scheme_name": "Free Rice Distribution",
            "feedback_type": "not_reaching",
            "action": "modify",
            "description": "Rice quality is very poor - has stones and insects. Many deserving families excluded from ration cards.",
            "support_count": 198
        }
    ]
    
    feedback_docs = []
    for scheme in schemes:
        feedback_docs.append({
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "user_district": random.choice(["Chennai", "Madurai", "Coimbatore"]),
            "scheme_name": scheme["scheme_name"],
            "feedback_type": scheme["feedback_type"],
            "action": scheme["action"],
            "description": scheme["description"],
            "support_count": scheme["support_count"],
            "in_review_queue": scheme["support_count"] >= 100,
            "review_queue_date": datetime.now(timezone.utc).isoformat() if scheme["support_count"] >= 100 else None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(10, 60))).isoformat()
        })
    
    if feedback_docs:
        await db.scheme_feedback.delete_many({})
        await db.scheme_feedback.insert_many(feedback_docs)
        print(f"✓ Created {len(feedback_docs)} scheme feedback entries")
    
    return feedback_docs

async def main():
    print("\n🌱 Seeding Makkal Kural Database with Realistic Tamil Nadu Issues...\n")
    
    # Create users
    users = await create_users(100)
    
    # Create issues
    issues = await create_issues(users)
    
    # Create votes
    await create_votes(users, issues)
    
    # Create comments
    await create_comments(users, issues)
    
    # Create scheme feedback
    await create_scheme_feedback()
    
    print("\n✅ Database seeding complete!")
    print(f"   - Users: {len(users)}")
    print(f"   - Issues: {len(issues)}")
    print(f"   - Scheme Feedback: 5")
    print("\n📊 You can now explore the platform with realistic data.\n")

if __name__ == "__main__":
    asyncio.run(main())
