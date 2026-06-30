"""
Comprehensive Seed Script for Makkal Kural - All 38 Tamil Nadu Districts
Run: python seed_all_districts.py
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

CATEGORY_INFO = {
    "water": {"name_en": "Drinking Water", "name_ta": "குடிநீர்"},
    "flooding": {"name_en": "Flooding", "name_ta": "வெள்ளம்"},
    "roads": {"name_en": "Roads", "name_ta": "சாலைகள்"},
    "sewage": {"name_en": "Sewage", "name_ta": "கழிவுநீர்"},
    "garbage": {"name_en": "Garbage", "name_ta": "குப்பை"},
    "health": {"name_en": "Health Services", "name_ta": "சுகாதார சேவைகள்"},
    "schools": {"name_en": "Schools / Colleges", "name_ta": "பள்ளிகள் / கல்லூரிகள்"},
    "farming": {"name_en": "Farming / Irrigation", "name_ta": "விவசாயம் / நீர்ப்பாசனம்"},
    "transport": {"name_en": "Transport", "name_ta": "போக்குவரத்து"},
    "electricity": {"name_en": "Electricity", "name_ta": "மின்சாரம்"},
    "pollution": {"name_en": "Pollution", "name_ta": "மாசுபாடு"},
    "employment": {"name_en": "Employment", "name_ta": "வேலைவாய்ப்பு"},
    "housing": {"name_en": "Housing", "name_ta": "வீட்டுவசதி"},
    "welfare": {"name_en": "Welfare Schemes", "name_ta": "நலத்திட்டங்கள்"},
    "corruption": {"name_en": "Corruption", "name_ta": "ஊழல்"},
    "safety": {"name_en": "Public Safety", "name_ta": "பொது பாதுகாப்பு"}
}

# District-wise specific issues for all 38 districts
DISTRICT_ISSUES = {
    "Chennai": [
        {"category": "flooding", "problem_en": "Urban flooding & stormwater drainage failure", "problem_ta": "நகர்ப்புற வெள்ளம் & மழைநீர் வடிகால் தோல்வி", 
         "description": "Every monsoon, Chennai faces severe waterlogging. The stormwater drains are clogged with garbage and encroachments. Low-lying areas like Velachery, Mudichur remain flooded for weeks. Residents lose property worth crores.", 
         "areas": ["Velachery", "Mudichur", "Porur", "Tambaram", "Perumbakkam"], "support": (180, 350)},
        {"category": "transport", "problem_en": "Traffic congestion & poor last-mile connectivity", "problem_ta": "போக்குவரத்து நெரிசல் & கடைசி மைல் இணைப்பின்மை",
         "description": "Chennai traffic has become unbearable. Office commute takes 2-3 hours. Metro doesn't reach many areas. Share autos charge exorbitant rates. Need more buses and better connectivity.",
         "areas": ["OMR", "Anna Nagar", "T Nagar", "Guindy", "Adyar"], "support": (150, 280)},
        {"category": "water", "problem_en": "Water scarcity in summer - Tanker dependency", "problem_ta": "கோடையில் நீர் பற்றாக்குறை - டேங்கர் சார்பு",
         "description": "Every summer, Chennai faces acute water crisis. Metrowater supply is irregular. We spend Rs. 3000-5000 per month on tanker water. Bore wells have dried up.",
         "areas": ["Pallikaranai", "Thoraipakkam", "Sholinganallur", "Perungudi"], "support": (200, 380)},
        {"category": "garbage", "problem_en": "Waste segregation failure & landfill overflow", "problem_ta": "கழிவு பிரிப்பு தோல்வி & குப்பைக்குழி வழிதல்",
         "description": "Perungudi and Kodungaiyur landfills are overflowing. Garbage not collected for days. No proper waste segregation. The stench is unbearable for nearby residents.",
         "areas": ["Perungudi", "Kodungaiyur", "Manali", "Ennore"], "support": (120, 220)},
        {"category": "pollution", "problem_en": "Coastal erosion in North Chennai - Industrial pollution", "problem_ta": "வட சென்னையில் கடலோர அரிப்பு - தொழிற்சாலை மாசுபாடு",
         "description": "Ennore and Manali areas face severe industrial pollution. Air quality is hazardous. Coastal areas are eroding. Fishing communities are losing their livelihood.",
         "areas": ["Ennore", "Manali", "Royapuram", "Kasimedu"], "support": (140, 260)},
    ],
    
    "Chengalpattu": [
        {"category": "flooding", "problem_en": "Flood-prone low-lying layouts approved illegally", "problem_ta": "சட்டவிரோதமாக அனுமதிக்கப்பட்ட வெள்ளப்பகுதி மனைகள்",
         "description": "Many layouts in Chengalpattu are in low-lying areas and flood every year. DTCP approvals were given without proper drainage plans. Residents are trapped during monsoon.",
         "areas": ["Guduvanchery", "Urapakkam", "Vandalur", "Maraimalai Nagar"], "support": (90, 180)},
        {"category": "water", "problem_en": "Drinking water supply gaps in new developments", "problem_ta": "புதிய வளர்ச்சிப் பகுதிகளில் குடிநீர் இடைவெளி",
         "description": "Rapid construction but no water infrastructure. New apartments have no metro water connection. Tanker water costs Rs. 800 per load.",
         "areas": ["GST Road", "Tambaram", "Chromepet", "Pallavaram"], "support": (100, 200)},
        {"category": "pollution", "problem_en": "SIPCOT industrial pollution affecting villages", "problem_ta": "SIPCOT தொழிற்பகுதி மாசுபாடு கிராமங்களை பாதிக்கிறது",
         "description": "Factories in SIPCOT Sriperumbudur discharge waste into water bodies. Groundwater is contaminated. Villagers have skin diseases and respiratory issues.",
         "areas": ["Sriperumbudur", "Oragadam", "Singaperumal Koil"], "support": (130, 240)},
        {"category": "roads", "problem_en": "Roads damaged by heavy vehicles - No repairs", "problem_ta": "கனரக வாகனங்களால் சேதமான சாலைகள் - பழுது இல்லை",
         "description": "Industrial areas have damaged roads due to heavy lorry traffic. Potholes cause accidents daily. PWD ignores our complaints.",
         "areas": ["Oragadam", "Sriperumbudur", "Irungattukottai"], "support": (80, 160)},
    ],
    
    "Kancheepuram": [
        {"category": "water", "problem_en": "Groundwater depletion - Wells drying up", "problem_ta": "நிலத்தடி நீர் குறைவு - கிணறுகள் வற்றுகின்றன",
         "description": "Groundwater level has dropped drastically due to over-extraction. Agricultural wells that worked at 100ft now need 500ft. Farmers are abandoning cultivation.",
         "areas": ["Walajabad", "Uthiramerur", "Sriperumbudur"], "support": (110, 210)},
        {"category": "employment", "problem_en": "Silk weavers facing income crisis", "problem_ta": "பட்டு நெசவாளர்கள் வருமான நெருக்கடி",
         "description": "Kanchipuram silk weavers are struggling. Machine-made competition, GST burden, and lack of orders have pushed many to poverty. Traditional craft is dying.",
         "areas": ["Kanchipuram Town", "Pillayarpalayam", "Ekambaranallur"], "support": (95, 190)},
        {"category": "flooding", "problem_en": "Lake encroachment causing floods", "problem_ta": "ஏரி ஆக்கிரமிப்பு வெள்ளத்தை ஏற்படுத்துகிறது",
         "description": "Temple tanks and lakes in Kanchipuram are encroached. During monsoon, water has nowhere to go and floods residential areas.",
         "areas": ["Kanchipuram Town", "Little Kanchipuram"], "support": (85, 170)},
        {"category": "roads", "problem_en": "Rural road maintenance neglected", "problem_ta": "கிராம சாலை பராமரிப்பு புறக்கணிப்பு",
         "description": "Village roads are in terrible condition. Buses don't ply due to bad roads. Students and elderly suffer the most.",
         "areas": ["Walajabad Block", "Uthiramerur Block"], "support": (75, 150)},
    ],
    
    "Tiruvallur": [
        {"category": "pollution", "problem_en": "Ennore thermal plant fly ash contamination", "problem_ta": "எண்ணூர் அனல்மின் நிலைய சாம்பல் மாசுபாடு",
         "description": "Fly ash from NCTPS is dumped in open areas. Dust covers nearby villages. Respiratory diseases are common. Groundwater is contaminated with heavy metals.",
         "areas": ["Ennore", "Athipattu", "Ponneri"], "support": (160, 300)},
        {"category": "water", "problem_en": "Water contamination from industries", "problem_ta": "தொழிற்சாலைகளிலிருந்து நீர் மாசுபாடு",
         "description": "Industries discharge untreated effluents. Kosasthalaiyar river is polluted. Villages downstream use this contaminated water for agriculture.",
         "areas": ["Gummidipoondi", "Ponneri", "RK Pet"], "support": (140, 270)},
        {"category": "flooding", "problem_en": "Flooding in peri-urban areas during monsoon", "problem_ta": "பருவமழையில் புறநகர் பகுதிகளில் வெள்ளம்",
         "description": "Areas near Cooum and Kosasthalaiyar rivers flood every year. No proper embankments. Houses get submerged. No government relief reaches in time.",
         "areas": ["Puzhal", "Avadi", "Ambattur"], "support": (120, 230)},
    ],
    
    "Vellore": [
        {"category": "water", "problem_en": "Chronic water scarcity - Palar river dried", "problem_ta": "நீடித்த நீர் பற்றாக்குறை - பாலாறு வற்றியது",
         "description": "Palar river bed is completely dry. Vellore city depends entirely on Palar water. Tanker mafia is exploiting the situation. Poor families can't afford water.",
         "areas": ["Vellore Town", "Katpadi", "Gudiyatham"], "support": (170, 320)},
        {"category": "pollution", "problem_en": "Leather industry pollution - Untreated waste", "problem_ta": "தோல் தொழிற்சாலை மாசுபாடு - சுத்திகரிக்காத கழிவு",
         "description": "Ranipet-Ambur belt tanneries discharge chromium waste into Palar. Cancer cases are high. Groundwater is permanently contaminated.",
         "areas": ["Ranipet", "Ambur", "Vaniyambadi"], "support": (190, 350)},
        {"category": "health", "problem_en": "Government hospital overcrowded - No beds", "problem_ta": "அரசு மருத்துவமனை நெரிசல் - படுக்கைகள் இல்லை",
         "description": "Vellore Government Hospital serves 5 districts but has limited capacity. Patients wait for days. Emergency cases are turned away.",
         "areas": ["Vellore Town"], "support": (130, 250)},
        {"category": "employment", "problem_en": "Youth unemployment despite education", "problem_ta": "கல்வி இருந்தும் இளைஞர் வேலையின்மை",
         "description": "Engineering graduates from Vellore are jobless. Local industries hire contract workers at low wages. Brain drain to cities is high.",
         "areas": ["Vellore District"], "support": (100, 200)},
    ],
    
    "Ranipet": [
        {"category": "pollution", "problem_en": "Tannery pollution - Chromium in groundwater", "problem_ta": "தோல் பதனிடும் தொழிற்சாலை மாசுபாடு - நிலத்தடி நீரில் குரோமியம்",
         "description": "Ranipet is one of the most polluted places in India. Tannery waste has contaminated soil and water. Cancer rates are 10x higher than state average.",
         "areas": ["Ranipet Town", "Walajah", "Arcot"], "support": (200, 380)},
        {"category": "garbage", "problem_en": "Hazardous waste dumping in open", "problem_ta": "அபாயகரமான கழிவுகளை திறந்த வெளியில் கொட்டுதல்",
         "description": "Industrial hazardous waste is dumped illegally in village outskirts. Children play near toxic dumps. No proper disposal facility exists.",
         "areas": ["Ranipet Industrial Area", "Walajah"], "support": (150, 280)},
        {"category": "water", "problem_en": "Groundwater unfit for any use", "problem_ta": "நிலத்தடி நீர் எந்த பயன்பாட்டிற்கும் தகுதியற்றது",
         "description": "Groundwater in Ranipet is completely contaminated with heavy metals. We buy drinking water. Even for bathing, we need tanker water.",
         "areas": ["Ranipet Town", "SIPCOT Area"], "support": (180, 340)},
    ],
    
    "Tirupattur": [
        {"category": "farming", "problem_en": "Drought-prone agriculture - No irrigation", "problem_ta": "வறட்சி பாதித்த விவசாயம் - நீர்ப்பாசனம் இல்லை",
         "description": "Tirupattur is rain-dependent. Consecutive drought years have destroyed farmers. No proper irrigation projects completed despite promises.",
         "areas": ["Tirupattur", "Vaniyambadi", "Natrampalli"], "support": (140, 270)},
        {"category": "employment", "problem_en": "No industrial employment - Youth migration", "problem_ta": "தொழிற்சாலை வேலைவாய்ப்பு இல்லை - இளைஞர் இடம்பெயர்வு",
         "description": "No major industries in Tirupattur. Youth migrate to Bangalore and Chennai for jobs. Villages have only elderly people left.",
         "areas": ["Tirupattur District"], "support": (110, 210)},
        {"category": "health", "problem_en": "Rural healthcare inaccessible", "problem_ta": "கிராமப்புற சுகாதாரம் அணுக முடியாது",
         "description": "PHCs have no doctors. For any treatment, we travel 50km to Vellore. Emergency cases die on the way. Need functional health centers.",
         "areas": ["Natrampalli", "Ambur Block"], "support": (100, 190)},
    ],
    
    "Tiruvannamalai": [
        {"category": "farming", "problem_en": "Severe drought cycles destroying crops", "problem_ta": "கடுமையான வறட்சி சுழற்சி பயிர்களை அழிக்கிறது",
         "description": "Tiruvannamalai is drought-prone. No major river or dam. Farmers depend on erratic monsoon. Crop failures have led to farmer suicides.",
         "areas": ["Chengam", "Polur", "Cheyyar"], "support": (160, 300)},
        {"category": "roads", "problem_en": "Road connectivity poor in rural blocks", "problem_ta": "கிராம வட்டங்களில் சாலை இணைப்பு மோசம்",
         "description": "Interior villages have no proper roads. During monsoon, villages are cut off. Ambulances cannot reach. Students miss school.",
         "areas": ["Jawadhu Hills", "Chengam Block", "Kalasapakkam"], "support": (120, 230)},
        {"category": "transport", "problem_en": "Temple town crowd management failure", "problem_ta": "கோயில் நகர கூட்ட மேலாண்மை தோல்வி",
         "description": "During Karthigai Deepam, lakhs visit Tiruvannamalai. No proper traffic management. Stampede risk is high. Local residents cannot move.",
         "areas": ["Tiruvannamalai Town"], "support": (90, 180)},
    ],
    
    "Villupuram": [
        {"category": "farming", "problem_en": "Poor irrigation infrastructure - Tanks silted", "problem_ta": "மோசமான நீர்ப்பாசன உள்கட்டமைப்பு - ஏரிகள் தூர்ந்தன",
         "description": "Traditional tanks are silted and encroached. Canal irrigation project incomplete for 10 years. Farmers struggle every season.",
         "areas": ["Gingee", "Tindivanam", "Villupuram"], "support": (130, 250)},
        {"category": "employment", "problem_en": "Migration due to lack of local jobs", "problem_ta": "உள்ளூர் வேலைகள் இல்லாததால் இடம்பெயர்வு",
         "description": "No industries in Villupuram district. Entire families migrate to Chennai for construction work. Children's education suffers.",
         "areas": ["Villupuram District"], "support": (100, 200)},
        {"category": "safety", "problem_en": "Frequent road accidents - NH45", "problem_ta": "அடிக்கடி சாலை விபத்துகள் - NH45",
         "description": "NH45 passing through Villupuram has become a death trap. No proper dividers, poor lighting. Accidents happen almost daily.",
         "areas": ["Tindivanam", "Vikravandi", "Villupuram"], "support": (110, 210)},
    ],
    
    "Kallakurichi": [
        {"category": "schools", "problem_en": "Education quality concerns in government schools", "problem_ta": "அரசு பள்ளிகளில் கல்வி தர கவலைகள்",
         "description": "After the tragic incident, parents are worried about school safety and quality. Many schools lack proper teachers and infrastructure.",
         "areas": ["Kallakurichi Town", "Chinnasalem", "Ulundurpet"], "support": (140, 270)},
        {"category": "farming", "problem_en": "Agricultural instability - Price fluctuation", "problem_ta": "விவசாய உறுதியின்மை - விலை ஏற்ற இறக்கம்",
         "description": "Sugarcane and paddy farmers face price crashes. Sugar mills delay payments for months. No MSP enforcement.",
         "areas": ["Kallakurichi", "Sankarapuram"], "support": (110, 210)},
        {"category": "water", "problem_en": "Rural drinking water shortage", "problem_ta": "கிராமப்புற குடிநீர் பற்றாக்குறை",
         "description": "Hand pumps have dried up. Panchayat water supply is irregular. Women walk kilometers to fetch water.",
         "areas": ["Interior Villages", "Chinnasalem Block"], "support": (100, 190)},
    ],
    
    "Cuddalore": [
        {"category": "flooding", "problem_en": "Cyclone & flood vulnerability every year", "problem_ta": "ஒவ்வொரு ஆண்டும் புயல் & வெள்ள பாதிப்பு",
         "description": "Cuddalore faces cyclones and floods regularly. Homes are destroyed every monsoon. Relief is inadequate. Permanent solution needed.",
         "areas": ["Cuddalore Town", "Porto Novo", "Parangipettai"], "support": (180, 340)},
        {"category": "pollution", "problem_en": "SIPCOT industrial pollution - Health hazards", "problem_ta": "SIPCOT தொழிற்பகுதி மாசுபாடு - உடல்நல அபாயங்கள்",
         "description": "SIPCOT Cuddalore is highly polluted. Chemical factories release toxic fumes. Cancer cases are high. Villages near SIPCOT are worst affected.",
         "areas": ["SIPCOT Cuddalore", "Semmankuppam", "Kudikadu"], "support": (200, 380)},
        {"category": "water", "problem_en": "Salinity intrusion in coastal areas", "problem_ta": "கடலோர பகுதிகளில் உப்புநீர் ஊடுருவல்",
         "description": "Groundwater in coastal Cuddalore has become saline. Agriculture is impossible. Drinking water is bought from far away.",
         "areas": ["Porto Novo", "Parangipettai", "Pichavaram"], "support": (150, 280)},
    ],
    
    "Mayiladuthurai": [
        {"category": "farming", "problem_en": "Delta irrigation concerns - Mettur water", "problem_ta": "டெல்டா நீர்ப்பாசன கவலைகள் - மேட்டூர் நீர்",
         "description": "Cauvery delta farmers depend on Mettur dam water. Delayed opening affects samba crop. Karnataka releases less water every year.",
         "areas": ["Mayiladuthurai", "Sirkazhi", "Kuthalam"], "support": (170, 320)},
        {"category": "flooding", "problem_en": "Flooding during heavy rains - No drainage", "problem_ta": "கனமழையில் வெள்ளம் - வடிகால் இல்லை",
         "description": "Low-lying delta region floods easily. Paddy fields submerge. Standing crops are destroyed. Farmers lose everything.",
         "areas": ["Mayiladuthurai", "Poompuhar"], "support": (130, 250)},
        {"category": "employment", "problem_en": "Fishing community livelihood stress", "problem_ta": "மீனவ சமூக வாழ்வாதார நெருக்கடி",
         "description": "Mechanized boats are depleting fish. Traditional fishermen can't compete. Sri Lankan navy arrests are common. No insurance or compensation.",
         "areas": ["Poompuhar", "Tharangambadi"], "support": (120, 230)},
    ],
    
    "Nagapattinam": [
        {"category": "flooding", "problem_en": "Cyclone damage recurrence - Not rebuilt", "problem_ta": "புயல் சேதம் மீண்டும் மீண்டும் - மறுகட்டமைப்பு இல்லை",
         "description": "Since 2004 tsunami, Nagapattinam faces cyclones every few years. Houses rebuilt after one cyclone are damaged in the next. Permanent houses needed.",
         "areas": ["Nagapattinam Town", "Velankanni", "Vedaranyam"], "support": (160, 300)},
        {"category": "pollution", "problem_en": "Coastal erosion threatening villages", "problem_ta": "கடலோர அரிப்பு கிராமங்களை அச்சுறுத்துகிறது",
         "description": "Sea is advancing inland. Several houses have been swallowed. No proper sea wall construction. Fishing hamlets are at risk.",
         "areas": ["Nagore", "Velankanni", "Kodiyakarai"], "support": (140, 270)},
        {"category": "employment", "problem_en": "Fisherfolk income declining", "problem_ta": "மீனவர் வருமானம் குறைகிறது",
         "description": "Overfishing by trawlers has reduced catch. Traditional fishermen can't sustain. Government schemes don't reach actual fishermen.",
         "areas": ["Nagapattinam Coast"], "support": (110, 210)},
    ],
    
    "Thanjavur": [
        {"category": "farming", "problem_en": "Cauvery water disputes affecting farmers", "problem_ta": "காவிரி நீர் தகராறு விவசாயிகளை பாதிக்கிறது",
         "description": "Delta farmers don't get adequate Cauvery water. Karnataka doesn't release water on time. Crops fail every year. Farmers are in debt.",
         "areas": ["Thanjavur", "Papanasam", "Orathanadu"], "support": (200, 380)},
        {"category": "welfare", "problem_en": "Farmer debt crisis - No loan waiver", "problem_ta": "விவசாயி கடன் நெருக்கடி - கடன் தள்ளுபடி இல்லை",
         "description": "Thanjavur farmers have taken multiple loans. Crop failures mean no repayment. Banks seize equipment. Suicides are increasing.",
         "areas": ["Thanjavur District"], "support": (180, 340)},
        {"category": "farming", "problem_en": "Crop loss due to irregular rainfall", "problem_ta": "ஒழுங்கற்ற மழையால் பயிர் இழப்பு",
         "description": "Climate change has made rainfall unpredictable. Sowings done based on forecast fail. Insurance claims are rejected on technicalities.",
         "areas": ["Budalur", "Thiruvaiyaru", "Kumbakonam"], "support": (150, 290)},
    ],
    
    "Tiruvarur": [
        {"category": "farming", "problem_en": "Agricultural distress in delta", "problem_ta": "டெல்டாவில் விவசாய துயரம்",
         "description": "Tiruvarur is rice bowl but farmers are poorest. Input costs rise but produce prices fall. Young generation leaving farming.",
         "areas": ["Tiruvarur", "Mannargudi", "Needamangalam"], "support": (140, 270)},
        {"category": "employment", "problem_en": "Youth migration - No local opportunities", "problem_ta": "இளைஞர் இடம்பெயர்வு - உள்ளூர் வாய்ப்புகள் இல்லை",
         "description": "No industries in Tiruvarur. Educated youth migrate to cities. Agriculture alone cannot sustain families.",
         "areas": ["Tiruvarur District"], "support": (100, 200)},
        {"category": "roads", "problem_en": "Poor industrial presence", "problem_ta": "மோசமான தொழிற்துறை இருப்பு",
         "description": "Despite being close to Cauvery, no industries set up. Government promised industrial parks but nothing materialized.",
         "areas": ["Tiruvarur District"], "support": (90, 180)},
    ],
    
    "Tiruchirappalli": [
        {"category": "water", "problem_en": "Water management issues - Cauvery allocation", "problem_ta": "நீர் மேலாண்மை பிரச்சனைகள் - காவிரி ஒதுக்கீடு",
         "description": "Trichy gets less Cauvery water than entitled. Supplying water to growing city is a challenge. Rationing is frequent.",
         "areas": ["Trichy City", "Srirangam", "Lalgudi"], "support": (130, 250)},
        {"category": "transport", "problem_en": "Rockfort area traffic congestion", "problem_ta": "ரோக்ஃபோர்ட் பகுதி போக்குவரத்து நெரிசல்",
         "description": "Narrow roads near Rockfort temple create massive jams. Tourist buses block entire streets. No parking facilities.",
         "areas": ["Rockfort", "Teppakulam", "Main Guard Gate"], "support": (100, 200)},
        {"category": "roads", "problem_en": "Urban road infrastructure gaps", "problem_ta": "நகர்ப்புற சாலை உள்கட்டமைப்பு இடைவெளிகள்",
         "description": "Trichy roads are poorly maintained. Ring road incomplete. Flyovers needed at major junctions but not built.",
         "areas": ["Trichy City"], "support": (90, 180)},
    ],
    
    "Perambalur": [
        {"category": "employment", "problem_en": "Low industrial development", "problem_ta": "குறைந்த தொழில் வளர்ச்சி",
         "description": "Perambalur is industrially backward. No major factories. Youth have no job options locally. Entire district depends on agriculture.",
         "areas": ["Perambalur District"], "support": (110, 210)},
        {"category": "water", "problem_en": "Groundwater depletion - Agriculture affected", "problem_ta": "நிலத்தடி நீர் குறைவு - விவசாயம் பாதிப்பு",
         "description": "Groundwater table has dropped drastically. Bore wells need to go 800-1000 feet. Drilling cost is unaffordable for small farmers.",
         "areas": ["Perambalur", "Veppanthattai", "Kunnam"], "support": (100, 190)},
        {"category": "schools", "problem_en": "Limited higher education access", "problem_ta": "வரையறுக்கப்பட்ட உயர்கல்வி அணுகல்",
         "description": "No engineering or medical colleges in Perambalur. Students travel to Trichy or Chennai. Poor families can't afford hostel fees.",
         "areas": ["Perambalur District"], "support": (80, 160)},
    ],
    
    "Ariyalur": [
        {"category": "pollution", "problem_en": "Cement industry pollution - Respiratory issues", "problem_ta": "சிமெண்ட் தொழிற்சாலை மாசுபாடு - சுவாச பிரச்சனைகள்",
         "description": "Ariyalur has many cement factories. Dust pollution is severe. Villages near factories have high rates of asthma and lung diseases.",
         "areas": ["Ariyalur", "Jayankondam", "Sendurai"], "support": (160, 300)},
        {"category": "schools", "problem_en": "Limited higher education facilities", "problem_ta": "வரையறுக்கப்பட்ட உயர்கல்வி வசதிகள்",
         "description": "Ariyalur has no quality colleges. Students go to Trichy. Government college has poor infrastructure and absent faculty.",
         "areas": ["Ariyalur Town"], "support": (90, 180)},
        {"category": "water", "problem_en": "Agricultural water scarcity", "problem_ta": "விவசாய நீர் பற்றாக்குறை",
         "description": "Ariyalur is drought-prone. No major irrigation project. Farmers depend on rain. One failed monsoon destroys entire year.",
         "areas": ["Ariyalur District"], "support": (120, 230)},
    ],
    
    "Karur": [
        {"category": "pollution", "problem_en": "Textile dyeing pollution - Amaravathi river dead", "problem_ta": "துணி சாயம் மாசுபாடு - அமராவதி ஆறு இறந்தது",
         "description": "Dyeing units discharge colored effluents into Amaravathi river. River water is unusable. Fish have died. Downstream villages affected.",
         "areas": ["Karur Town", "Kulithalai"], "support": (180, 340)},
        {"category": "water", "problem_en": "River contamination - No clean water", "problem_ta": "ஆற்று மாசுபாடு - சுத்தமான நீர் இல்லை",
         "description": "Both Cauvery and Amaravathi are polluted near Karur. Municipal water supply is unreliable. Skin diseases are common.",
         "areas": ["Karur Town", "K. Paramathi"], "support": (150, 280)},
        {"category": "employment", "problem_en": "SME financial instability", "problem_ta": "சிறு தொழில் நிதி உறுதியின்மை",
         "description": "Small textile units are closing due to GST burden and competition. Bank loans are not available. Workers losing jobs.",
         "areas": ["Karur Town"], "support": (100, 200)},
    ],
    
    "Namakkal": [
        {"category": "garbage", "problem_en": "Poultry industry waste mismanagement", "problem_ta": "கோழி தொழில் கழிவு மேலாண்மை தோல்வி",
         "description": "Namakkal is poultry hub but dead bird disposal is a mess. Carcasses dumped in open. Stench is unbearable. Disease outbreak risk.",
         "areas": ["Namakkal", "Mohanur", "Rasipuram"], "support": (140, 270)},
        {"category": "water", "problem_en": "Water scarcity - Competing uses", "problem_ta": "நீர் பற்றாக்குறை - போட்டி பயன்பாடுகள்",
         "description": "Limited water shared between poultry farms, industries, and residents. Groundwater depleted by borewells. Drinking water is scarce.",
         "areas": ["Namakkal", "Tiruchengode"], "support": (120, 230)},
        {"category": "transport", "problem_en": "Lorry hub congestion - Accidents", "problem_ta": "லாரி மையம் நெரிசல் - விபத்துகள்",
         "description": "Namakkal is lorry manufacturing hub. Heavy vehicles congest town roads. Accidents with two-wheelers are daily occurrence.",
         "areas": ["Namakkal Town", "Pallipalayam"], "support": (100, 200)},
    ],
    
    "Salem": [
        {"category": "pollution", "problem_en": "Steel & industrial pollution", "problem_ta": "எஃகு & தொழிற்சாலை மாசுபாடு",
         "description": "Salem Steel Plant and other industries pollute air and water. Surrounding villages have health issues. No environmental monitoring.",
         "areas": ["Salem Steel Plant Area", "Mettur"], "support": (150, 290)},
        {"category": "transport", "problem_en": "Traffic bottlenecks - Old city", "problem_ta": "போக்குவரத்து தடை - பழைய நகரம்",
         "description": "Salem's narrow old city roads can't handle modern traffic. Jams during peak hours. Bypasses incomplete.",
         "areas": ["Salem Town", "Five Roads", "Ammapet"], "support": (110, 210)},
        {"category": "farming", "problem_en": "Yercaud hill development concerns", "problem_ta": "ஏற்காடு மலை வளர்ச்சி கவலைகள்",
         "description": "Unregulated construction in Yercaud is destroying environment. Landslides increasing. Water sources drying up.",
         "areas": ["Yercaud"], "support": (90, 180)},
    ],
    
    "Dharmapuri": [
        {"category": "farming", "problem_en": "Chronic drought - Farmer suicides", "problem_ta": "நீடித்த வறட்சி - விவசாயி தற்கொலைகள்",
         "description": "Dharmapuri faces drought almost every year. No irrigation facilities. Farmers take loans, fail to repay when crops fail. Suicide rates are high.",
         "areas": ["Dharmapuri", "Harur", "Palacode"], "support": (200, 380)},
        {"category": "employment", "problem_en": "Mass migration to cities", "problem_ta": "நகரங்களுக்கு பெரும் இடம்பெயர்வு",
         "description": "No jobs in Dharmapuri. Entire families migrate to Bangalore. Villages are empty. Only elderly remain.",
         "areas": ["Dharmapuri District"], "support": (150, 290)},
        {"category": "water", "problem_en": "Groundwater completely depleted", "problem_ta": "நிலத்தடி நீர் முற்றிலும் தீர்ந்தது",
         "description": "Bore wells go 1000+ feet and still no water. Traditional wells are dry. Drinking water is a luxury.",
         "areas": ["Dharmapuri", "Pennagaram"], "support": (170, 320)},
    ],
    
    "Krishnagiri": [
        {"category": "farming", "problem_en": "Mango farmers price crash", "problem_ta": "மாம்பழ விவசாயிகள் விலை வீழ்ச்சி",
         "description": "Krishnagiri is mango capital but farmers suffer. Market price crashes during peak season. Cold storage is inadequate. Mangoes rot.",
         "areas": ["Krishnagiri", "Hosur", "Bargur"], "support": (180, 340)},
        {"category": "safety", "problem_en": "Highway accidents - Salem-Bangalore NH", "problem_ta": "நெடுஞ்சாலை விபத்துகள் - சேலம்-பெங்களூர் NH",
         "description": "NH44 through Krishnagiri has highest accident rate. Sharp curves, no dividers, drunk driving. Deaths every week.",
         "areas": ["Hosur", "Krishnagiri", "Denkanikottai"], "support": (140, 270)},
        {"category": "water", "problem_en": "Water shortages despite KRS dam", "problem_ta": "KRS அணை இருந்தும் நீர் பற்றாக்குறை",
         "description": "Karnataka controls water release. Krishnagiri doesn't get enough. Hosur industries consume all available water.",
         "areas": ["Krishnagiri", "Hosur"], "support": (130, 250)},
    ],
    
    "Erode": [
        {"category": "pollution", "problem_en": "Textile dyeing pollution - Noyyal river", "problem_ta": "துணி சாயம் மாசுபாடு - நொய்யல் ஆறு",
         "description": "Erode-Tiruppur belt has destroyed Noyyal river. Dyeing units discharge toxic waste. Groundwater polluted. Farming affected downstream.",
         "areas": ["Erode", "Perundurai", "Bhavani"], "support": (190, 360)},
        {"category": "water", "problem_en": "Cauvery water dependency", "problem_ta": "காவிரி நீர் சார்பு",
         "description": "Erode depends on Cauvery for drinking and agriculture. Karnataka disputes affect water availability. Rationing is common.",
         "areas": ["Erode Town", "Bhavani"], "support": (140, 270)},
        {"category": "farming", "problem_en": "Turmeric farmers price instability", "problem_ta": "மஞ்சள் விவசாயிகள் விலை உறுதியின்மை",
         "description": "Erode is turmeric market hub but farmers don't benefit. Middlemen control prices. Storage facilities are poor.",
         "areas": ["Erode", "Gobichettipalayam"], "support": (120, 230)},
    ],
    
    "Tiruppur": [
        {"category": "pollution", "problem_en": "Garment industry wastewater - Zero liquid discharge failure", "problem_ta": "ஆடை தொழில் கழிவுநீர் - ZLD தோல்வி",
         "description": "Despite ZLD mandate, dyeing units discharge colored water. Noyyal river is dead. Groundwater contaminated for kilometers.",
         "areas": ["Tiruppur", "Avinashi", "Palladam"], "support": (200, 380)},
        {"category": "housing", "problem_en": "Migrant worker housing crisis", "problem_ta": "புலம்பெயர்ந்த தொழிலாளர் வீட்டு நெருக்கடி",
         "description": "Lakhs of workers from Bihar, Odisha work in Tiruppur. They live in cramped, unhygienic conditions. No welfare measures.",
         "areas": ["Tiruppur Industrial Areas"], "support": (150, 290)},
        {"category": "pollution", "problem_en": "Air pollution in industrial zones", "problem_ta": "தொழிற்பகுதிகளில் காற்று மாசுபாடு",
         "description": "Garment factories release chemicals in air. Workers have respiratory diseases. No proper ventilation in most units.",
         "areas": ["Tiruppur", "Avinashi"], "support": (130, 250)},
    ],
    
    "Coimbatore": [
        {"category": "water", "problem_en": "Water scarcity - Siruvani source depleting", "problem_ta": "நீர் பற்றாக்குறை - சிறுவாணி மூலம் குறைகிறது",
         "description": "Coimbatore's main water source Siruvani is insufficient for growing population. Alternate sources not developed. Summer crisis every year.",
         "areas": ["Coimbatore City", "Singanallur", "Saravanampatti"], "support": (170, 320)},
        {"category": "roads", "problem_en": "Urban sprawl - Infrastructure lag", "problem_ta": "நகர்ப்புற விரிவாக்கம் - உள்கட்டமைப்பு பின்தங்கியது",
         "description": "Coimbatore is expanding rapidly but roads, drains not built. New areas have no water supply. Traffic jams increasing.",
         "areas": ["Saravanampatti", "Thudiyalur", "Vadavalli"], "support": (140, 270)},
        {"category": "garbage", "problem_en": "Solid waste management failure", "problem_ta": "திட கழிவு மேலாண்மை தோல்வி",
         "description": "Vellalore dump yard is overflowing. Waste processing plant underperforming. Segregation not happening at source.",
         "areas": ["Vellalore", "Coimbatore City"], "support": (120, 230)},
        {"category": "pollution", "problem_en": "Air quality declining", "problem_ta": "காற்று தரம் குறைகிறது",
         "description": "Vehicle pollution and industrial emissions are worsening Coimbatore's air. No proper monitoring. Green cover decreasing.",
         "areas": ["Coimbatore City"], "support": (100, 200)},
    ],
    
    "Nilgiris": [
        {"category": "flooding", "problem_en": "Landslides during monsoon", "problem_ta": "பருவமழையில் நிலச்சரிவுகள்",
         "description": "Every monsoon brings landslides in Nilgiris. Houses buried, people killed. No proper early warning. Deforestation is the cause.",
         "areas": ["Coonoor", "Kotagiri", "Ooty"], "support": (160, 300)},
        {"category": "transport", "problem_en": "Tourism pressure - Traffic jams", "problem_ta": "சுற்றுலா அழுத்தம் - போக்குவரத்து நெரிசல்",
         "description": "Tourist vehicles clog narrow ghat roads. Local movement is impossible during season. Accidents on curves.",
         "areas": ["Ooty", "Coonoor", "Mettupalayam Ghat"], "support": (120, 230)},
        {"category": "welfare", "problem_en": "Tribal welfare gaps", "problem_ta": "பழங்குடி நலன் இடைவெளிகள்",
         "description": "Indigenous tribes in Nilgiris lack basic facilities. Forest rights not given. Healthcare inaccessible. Education poor.",
         "areas": ["Tribal Settlements"], "support": (100, 200)},
        {"category": "pollution", "problem_en": "Climate change impact - Frost patterns changing", "problem_ta": "காலநிலை மாற்ற தாக்கம் - உறைபனி முறைகள் மாறுகின்றன",
         "description": "Traditional frost patterns changing. Tea estates affected. Vegetables growing patterns disrupted. Farmers can't predict anymore.",
         "areas": ["Nilgiris District"], "support": (90, 180)},
    ],
    
    "Dindigul": [
        {"category": "water", "problem_en": "Water stress - Multiple competing uses", "problem_ta": "நீர் நெருக்கடி - பல போட்டி பயன்பாடுகள்",
         "description": "Dindigul has tanneries, agriculture, and urban population competing for limited water. Groundwater depleted. Conflicts common.",
         "areas": ["Dindigul", "Oddanchatram", "Palani"], "support": (140, 270)},
        {"category": "pollution", "problem_en": "Tannery pollution in town", "problem_ta": "நகரத்தில் தோல் பதனிடும் தொழிற்சாலை மாசுபாடு",
         "description": "Dindigul tanneries in residential areas. Smell is unbearable. Wastewater contaminates surroundings. Health issues common.",
         "areas": ["Dindigul Town"], "support": (120, 230)},
        {"category": "roads", "problem_en": "Kodaikanal road safety issues", "problem_ta": "கொடைக்கானல் சாலை பாதுகாப்பு பிரச்சனைகள்",
         "description": "Hairpin bends on Kodaikanal road cause accidents. Tourist vehicle drivers inexperienced. No barriers at many points.",
         "areas": ["Kodaikanal Ghat Road"], "support": (100, 200)},
    ],
    
    "Madurai": [
        {"category": "transport", "problem_en": "Traffic congestion around Meenakshi Temple", "problem_ta": "மீனாட்சி கோயில் சுற்றி போக்குவரத்து நெரிசல்",
         "description": "Temple area has severe traffic jams. Narrow streets can't handle modern traffic. Parking is a nightmare. Pilgrims and residents suffer.",
         "areas": ["Temple Area", "Periyar Bus Stand", "Mattuthavani"], "support": (160, 300)},
        {"category": "roads", "problem_en": "City infrastructure stress", "problem_ta": "நகர உள்கட்டமைப்பு நெருக்கடி",
         "description": "Madurai roads are poorly maintained. Drainage overflows during rain. Streetlights don't work in many areas.",
         "areas": ["Madurai City"], "support": (130, 250)},
        {"category": "water", "problem_en": "Water supply inconsistent - Vaigai dependency", "problem_ta": "நீர் வழங்கல் சீரற்றது - வைகை சார்பு",
         "description": "Madurai depends on Vaigai dam which doesn't fill every year. Water rationing is common. New areas have no piped water.",
         "areas": ["Madurai City", "Thirumangalam"], "support": (140, 270)},
    ],
    
    "Theni": [
        {"category": "farming", "problem_en": "Grape and vegetable farmers price crash", "problem_ta": "திராட்சை மற்றும் காய்கறி விவசாயிகள் விலை வீழ்ச்சி",
         "description": "Theni farmers grow grapes and vegetables for Madurai market. Price fluctuations destroy them. No cold storage. Produce rots.",
         "areas": ["Theni", "Cumbum", "Periyakulam"], "support": (130, 250)},
        {"category": "water", "problem_en": "Mullaperiyar dam water dependency", "problem_ta": "முல்லைப்பெரியாறு அணை நீர் சார்பு",
         "description": "Theni's irrigation depends on Mullaperiyar. Kerala disputes affect farmers. Uncertainty every season.",
         "areas": ["Cumbum Valley", "Theni"], "support": (150, 290)},
        {"category": "safety", "problem_en": "Border area smuggling - Illicit liquor", "problem_ta": "எல்லைப் பகுதி கடத்தல் - சட்டவிரோத மது",
         "description": "Illicit liquor from Kerala kills people regularly. Smuggling is rampant. Police-smuggler nexus alleged.",
         "areas": ["Kerala Border Areas"], "support": (110, 210)},
    ],
    
    "Sivagangai": [
        {"category": "welfare", "problem_en": "Rural poverty - Scheme benefits not reaching", "problem_ta": "கிராமப்புற வறுமை - திட்ட பலன்கள் சேரவில்லை",
         "description": "Sivagangai has severe rural poverty. Government schemes exist on paper but benefits don't reach actual poor. Middlemen take commission.",
         "areas": ["Sivagangai District"], "support": (120, 230)},
        {"category": "water", "problem_en": "Water scarcity - Tanks dry", "problem_ta": "நீர் பற்றாக்குறை - ஏரிகள் வறண்டன",
         "description": "Traditional tanks in Sivagangai are dry. No desilting done for decades. Farmers have no water for second crop.",
         "areas": ["Sivagangai", "Karaikudi", "Devakottai"], "support": (100, 200)},
        {"category": "employment", "problem_en": "No industrial growth", "problem_ta": "தொழில் வளர்ச்சி இல்லை",
         "description": "Sivagangai has no industries. Agriculture alone can't sustain. Youth migrate to Gulf countries and cities.",
         "areas": ["Sivagangai District"], "support": (90, 180)},
    ],
    
    "Ramanathapuram": [
        {"category": "farming", "problem_en": "Severe drought - Agriculture impossible", "problem_ta": "கடுமையான வறட்சி - விவசாயம் சாத்தியமில்லை",
         "description": "Ramanathapuram is Tamil Nadu's driest district. Rainfall is minimal. Agriculture has nearly stopped. Farmers survive on MGNREGA.",
         "areas": ["Ramanathapuram", "Paramakudi", "Rameswaram"], "support": (180, 340)},
        {"category": "employment", "problem_en": "Fisherfolk livelihood at risk", "problem_ta": "மீனவர் வாழ்வாதாரம் ஆபத்தில்",
         "description": "Sri Lankan navy arrests fishermen crossing IMBL. Boats confiscated. Families left without income. No insurance or compensation.",
         "areas": ["Rameswaram", "Mandapam", "Pamban"], "support": (160, 300)},
        {"category": "water", "problem_en": "Saline groundwater - No drinking water", "problem_ta": "உப்பு நிலத்தடி நீர் - குடிநீர் இல்லை",
         "description": "Groundwater in Ramanathapuram is saline and undrinkable. Drinking water comes from 50km away. Cost is high.",
         "areas": ["Ramanathapuram", "Mudukulathur"], "support": (150, 290)},
        {"category": "flooding", "problem_en": "Cyclone vulnerability - Coastal areas", "problem_ta": "புயல் பாதிப்பு - கடலோர பகுதிகள்",
         "description": "Every cyclone in Bay of Bengal hits Ramanathapuram. Fishing hamlets destroyed. No permanent cyclone shelters.",
         "areas": ["Rameswaram", "Pamban", "Mandapam"], "support": (140, 270)},
    ],
    
    "Virudhunagar": [
        {"category": "safety", "problem_en": "Firecracker industry safety concerns", "problem_ta": "பட்டாசு தொழில் பாதுகாப்பு கவலைகள்",
         "description": "Sivakasi firecracker units have frequent accidents. Workers die in explosions. Child labour still exists. Safety norms ignored.",
         "areas": ["Sivakasi", "Sattur", "Virudhunagar"], "support": (170, 320)},
        {"category": "employment", "problem_en": "Industrial accidents - Worker compensation", "problem_ta": "தொழிற்சாலை விபத்துகள் - தொழிலாளர் இழப்பீடு",
         "description": "Match and firecracker workers injured in accidents get no proper compensation. Medical treatment is expensive. Families suffer.",
         "areas": ["Sivakasi", "Kovilpatti"], "support": (130, 250)},
        {"category": "welfare", "problem_en": "Labour welfare gaps", "problem_ta": "தொழிலாளர் நலன் இடைவெளிகள்",
         "description": "Firecracker industry workers don't have ESI or PF. Work is seasonal. During off-season, families starve.",
         "areas": ["Sivakasi Belt"], "support": (110, 210)},
    ],
    
    "Thoothukudi": [
        {"category": "pollution", "problem_en": "Sterlite & industrial pollution legacy", "problem_ta": "ஸ்டெர்லைட் & தொழிற்சாலை மாசுபாடு பாரம்பரியம்",
         "description": "Even after Sterlite closure, pollution effects remain. Soil and water contaminated. Health issues persist. New industries face protests.",
         "areas": ["Thoothukudi Town", "SIPCOT"], "support": (200, 380)},
        {"category": "employment", "problem_en": "Port expansion vs Fisherfolk", "problem_ta": "துறைமுக விரிவாக்கம் vs மீனவர்கள்",
         "description": "Port expansion is displacing traditional fishing grounds. Dredging affects fish breeding. Fishermen losing livelihood.",
         "areas": ["Thoothukudi Port Area", "Harbour"], "support": (150, 290)},
        {"category": "water", "problem_en": "Groundwater salinity", "problem_ta": "நிலத்தடி நீர் உப்புத்தன்மை",
         "description": "Coastal Thoothukudi has saline groundwater. Drinking water is scarce. Desalination plant not working properly.",
         "areas": ["Thoothukudi", "Tiruchendur"], "support": (130, 250)},
    ],
    
    "Tirunelveli": [
        {"category": "water", "problem_en": "Tamiraparani water management issues", "problem_ta": "தாமிரபரணி நீர் மேலாண்மை பிரச்சனைகள்",
         "description": "Tamiraparani is Tamil Nadu's only perennial river but still water scarcity exists. Poor distribution. Tail-end farmers get nothing.",
         "areas": ["Tirunelveli", "Ambasamudram", "Palayamkottai"], "support": (140, 270)},
        {"category": "flooding", "problem_en": "Flooding in some blocks during monsoon", "problem_ta": "பருவமழையில் சில வட்டங்களில் வெள்ளம்",
         "description": "Low-lying areas near Tamiraparani flood during heavy rain. Paddy crops destroyed. Houses damaged. No proper bunds.",
         "areas": ["Nanguneri", "Radhapuram"], "support": (110, 210)},
        {"category": "employment", "problem_en": "Youth unemployment - Migration", "problem_ta": "இளைஞர் வேலையின்மை - இடம்பெயர்வு",
         "description": "Despite universities, Tirunelveli youth migrate to Chennai and abroad. Local job creation is minimal.",
         "areas": ["Tirunelveli District"], "support": (100, 200)},
    ],
    
    "Tenkasi": [
        {"category": "roads", "problem_en": "Western Ghats road safety - Accidents", "problem_ta": "மேற்கு தொடர்ச்சி மலை சாலை பாதுகாப்பு - விபத்துகள்",
         "description": "Roads through Western Ghats have sharp curves. Tourist vehicles and buses have accidents regularly. Need better barriers.",
         "areas": ["Courtallam", "Shencottah Ghat"], "support": (120, 230)},
        {"category": "farming", "problem_en": "Cardamom and pepper farmers struggling", "problem_ta": "ஏலக்காய் மற்றும் மிளகு விவசாயிகள் போராடுகிறார்கள்",
         "description": "Spice farmers in Tenkasi face price fluctuations. Import from Vietnam affects prices. No proper marketing support.",
         "areas": ["Kadayanallur", "Shencottah"], "support": (100, 200)},
        {"category": "transport", "problem_en": "Tourism infrastructure gaps - Courtallam", "problem_ta": "சுற்றுலா உள்கட்டமைப்பு இடைவெளிகள் - குற்றாலம்",
         "description": "Courtallam attracts lakhs but facilities are poor. Changing rooms unhygienic. Safety at waterfalls lacking. Accidents happen.",
         "areas": ["Courtallam"], "support": (90, 180)},
    ],
    
    "Kanniyakumari": [
        {"category": "pollution", "problem_en": "Coastal erosion - Houses falling into sea", "problem_ta": "கடலோர அரிப்பு - வீடுகள் கடலில் விழுகின்றன",
         "description": "Sea erosion in Kanniyakumari is severe. Several houses have collapsed into sea. Fishing hamlets are disappearing. Need proper seawalls.",
         "areas": ["Kanyakumari Town", "Colachel", "Thengapattinam"], "support": (160, 300)},
        {"category": "employment", "problem_en": "Fisherfolk safety at sea", "problem_ta": "கடலில் மீனவர் பாதுகாப்பு",
         "description": "Fishermen go to deep sea without proper safety equipment. Boats are not seaworthy. During storms, many die. Insurance inadequate.",
         "areas": ["Kanniyakumari Coast"], "support": (140, 270)},
        {"category": "garbage", "problem_en": "Tourism waste management", "problem_ta": "சுற்றுலா கழிவு மேலாண்மை",
         "description": "Kanyakumari sunrise point generates tons of waste daily. No proper disposal. Plastic litters the coast. Marine life affected.",
         "areas": ["Kanyakumari Town", "Vivekananda Rock Area"], "support": (120, 230)},
        {"category": "transport", "problem_en": "Religious tourism crowding", "problem_ta": "மத சுற்றுலா கூட்டம்",
         "description": "Temple and church festivals bring huge crowds. No crowd management. Stampede risk. Accommodation insufficient.",
         "areas": ["Kanyakumari", "Suchindram", "Nagercoil"], "support": (100, 200)},
    ],
    
    "Pudukkottai": [
        {"category": "water", "problem_en": "Water scarcity - Ancient tanks not maintained", "problem_ta": "நீர் பற்றாக்குறை - பழங்கால ஏரிகள் பராமரிக்கப்படவில்லை",
         "description": "Pudukkottai has beautiful traditional tanks but all are silted. No government initiative to restore. Agriculture suffering.",
         "areas": ["Pudukkottai", "Aranthangi", "Alangudi"], "support": (130, 250)},
        {"category": "employment", "problem_en": "Rural unemployment - No industries", "problem_ta": "கிராமப்புற வேலையின்மை - தொழிற்சாலைகள் இல்லை",
         "description": "Pudukkottai is industrially backward. Youth migrate to cities. Agriculture alone cannot sustain population.",
         "areas": ["Pudukkottai District"], "support": (100, 200)},
        {"category": "roads", "problem_en": "Infrastructure backlog in remote areas", "problem_ta": "தொலைதூர பகுதிகளில் உள்கட்டமைப்பு பின்னடைவு",
         "description": "Remote villages in Pudukkottai lack basic roads. During monsoon, villages cut off. Ambulances can't reach.",
         "areas": ["Interior Blocks"], "support": (90, 180)},
    ],
}

LOCAL_BODIES = ["Corporation", "Municipality", "Town Panchayat", "Village Panchayat"]

async def create_users(count_per_district=5):
    """Create sample users for each district"""
    users = []
    
    for district in DISTRICT_ISSUES.keys():
        for i in range(count_per_district):
            mobile_num = f"98{abs(hash(district)) % 10000:04d}{i:04d}"[-10:]
            user = {
                "id": str(uuid.uuid4()),
                "mobile": mobile_num,
                "name": f"Citizen from {district} {i+1}",
                "district": district,
                "local_body_type": random.choice(LOCAL_BODIES),
                "local_body_name": f"{district} Area {i+1}",
                "ward": f"Ward {random.randint(1, 20)}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "issues_raised": 0,
                "votes_cast": 0
            }
            users.append(user)
    
    if users:
        await db.users.delete_many({})
        await db.users.insert_many(users)
        print(f"✓ Created {len(users)} users across {len(DISTRICT_ISSUES)} districts")
    
    return users

async def create_all_district_issues(users):
    """Create issues for all 38 districts"""
    all_issues = []
    
    for district, issues_data in DISTRICT_ISSUES.items():
        district_users = [u for u in users if u["district"] == district]
        
        for issue_data in issues_data:
            if not district_users:
                continue
                
            creator = random.choice(district_users)
            support_count = random.randint(*issue_data["support"])
            oppose_count = random.randint(5, max(10, support_count // 5))
            total = support_count + oppose_count
            support_percentage = round((support_count / total) * 100, 1) if total > 0 else 0
            
            # Determine status and level
            current_level = 1
            if support_count >= 150 and support_percentage >= 70:
                current_level = 4
            elif support_count >= 80 and support_percentage >= 60:
                current_level = 3
            elif support_count >= 40:
                current_level = 2
                
            status = "pending"
            if support_count >= 80:
                status = "serious_issue"
            elif support_count >= 30:
                status = "area_concern"
            
            # Create escalation history
            created_date = datetime.now(timezone.utc) - timedelta(days=random.randint(14, 120))
            escalation_history = []
            for level in range(1, current_level + 1):
                level_info = ESCALATION_HIERARCHY[level - 1]
                level_date = created_date + timedelta(days=level * 10)
                escalation_history.append({
                    "level": level,
                    "role_en": level_info["role_en"],
                    "role_ta": level_info["role_ta"],
                    "reached_at": level_date.isoformat(),
                    "sla_deadline": (level_date + timedelta(days=level_info["sla_days"])).isoformat(),
                    "auto_escalated": level > 1,
                    "reason": f"Auto-escalated with {support_percentage}% support" if level > 1 else "Initial submission"
                })
            
            cat_info = CATEGORY_INFO.get(issue_data["category"], {"name_en": issue_data["category"], "name_ta": issue_data["category"]})
            area = random.choice(issue_data["areas"])
            
            issue = {
                "id": str(uuid.uuid4()),
                "user_id": creator["id"],
                "user_name": creator["name"],
                "user_mobile": creator["mobile"][-4:],
                "district": district,
                "local_body_type": random.choice(LOCAL_BODIES),
                "local_body_name": area,
                "ward": f"Ward {random.randint(1, 15)}",
                "street": f"{random.choice(['Main', '1st Cross', '2nd Cross', 'Temple', 'Market'])} Street",
                "category": issue_data["category"],
                "category_name_en": cat_info["name_en"],
                "category_name_ta": cat_info["name_ta"],
                "problem_id": issue_data["category"],
                "problem_name_en": issue_data["problem_en"],
                "problem_name_ta": issue_data["problem_ta"],
                "description": issue_data["description"],
                "voice_note_text": None,
                "frequency": random.choice(["daily", "weekly", "seasonal"]),
                "affected_people": random.choice(["50-500", "entire_area"]),
                "duration": random.choice(["months", "years"]),
                "media_urls": [],
                "status": status,
                "support_count": support_count,
                "oppose_count": oppose_count,
                "support_percentage": support_percentage,
                "publicly_validated": support_percentage >= 60,
                "comment_count": random.randint(5, 40),
                "current_level": current_level,
                "escalation_history": escalation_history,
                "created_at": created_date.isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            all_issues.append(issue)
    
    if all_issues:
        await db.issues.delete_many({})
        await db.issues.insert_many(all_issues)
        print(f"✓ Created {len(all_issues)} issues across all 38 districts")
    
    return all_issues

async def create_votes_and_comments(users, issues):
    """Create votes and comments"""
    votes = []
    comments = []
    
    sample_comments = [
        "This problem is affecting my family too. Please take action!",
        "நான் இந்த பிரச்சனையை தினமும் எதிர்கொள்கிறேன். உடனடி நடவடிக்கை தேவை.",
        "We have complained multiple times but no response from officials.",
        "இது 5 வருடங்களாக தொடர்கிறது. எந்த தீர்வும் இல்லை.",
        "The collector should visit our area and see the problem directly.",
        "We are ready for a peaceful protest if this is not resolved.",
        "My children are suffering because of this issue.",
        "Government schemes exist only on paper, not in reality.",
        "Thank you for raising this. We all support.",
        "The responsible officer should be transferred immediately."
    ]
    
    for issue in issues:
        district_users = [u for u in users if u["district"] == issue["district"]]
        
        # Create support votes
        num_supporters = min(issue["support_count"], len(district_users))
        supporters = random.sample(district_users, num_supporters) if district_users else []
        for voter in supporters:
            votes.append({
                "id": str(uuid.uuid4()),
                "user_id": voter["id"],
                "issue_id": issue["id"],
                "vote_type": "support",
                "district": issue["district"],
                "created_at": issue["created_at"]
            })
        
        # Create comments
        num_comments = min(random.randint(3, 8), len(district_users))
        commenters = random.sample(district_users, num_comments) if district_users else []
        for commenter in commenters:
            comments.append({
                "id": str(uuid.uuid4()),
                "issue_id": issue["id"],
                "user_id": commenter["id"],
                "user_name": commenter["name"],
                "text": random.choice(sample_comments),
                "created_at": (datetime.fromisoformat(issue["created_at"].replace('Z', '+00:00')) + timedelta(days=random.randint(1, 30))).isoformat()
            })
    
    if votes:
        await db.votes.delete_many({})
        await db.votes.insert_many(votes)
        print(f"✓ Created {len(votes)} votes")
    
    if comments:
        await db.comments.delete_many({})
        await db.comments.insert_many(comments)
        print(f"✓ Created {len(comments)} comments")

async def create_scheme_feedback():
    """Create scheme feedback entries"""
    schemes = [
        {"name": "Pradhan Mantri Awas Yojana (PMAY)", "type": "corrupt", "action": "modify", 
         "desc": "Houses sanctioned 4 years ago still incomplete. Contractor fled with funds. Officials demand bribes to restart.", "support": 345},
        {"name": "Kisan Samman Nidhi", "type": "not_reaching", "action": "modify",
         "desc": "Many tenant farmers excluded. Land record errors prevent enrollment. Banks rejecting applications.", "support": 278},
        {"name": "Free Laptop Scheme", "type": "not_useful", "action": "modify",
         "desc": "Laptops given are of poor quality. Most stop working within months. No service centers. Students can't use for studies.", "support": 189},
        {"name": "MGNREGA", "type": "corrupt", "action": "modify",
         "desc": "Ghost workers on rolls. Actual workers paid half the wages. Payment delayed 3-6 months. Contractors take commission.", "support": 412},
        {"name": "Free Bus Pass for Women", "type": "not_useful", "action": "modify",
         "desc": "Buses are overcrowded now. Women can't get seats. Bus frequency not increased. Men harass women in crowded buses.", "support": 156},
        {"name": "Amma Unavagam (Subsidized Canteens)", "type": "not_reaching", "action": "modify",
         "desc": "Quality has declined. Many canteens closed. Remaining ones serve unhygienic food. Need to restore original quality.", "support": 234},
        {"name": "CM Health Insurance Scheme", "type": "corrupt", "action": "modify",
         "desc": "Private hospitals inflate bills. Government hospitals refuse to treat under scheme. Paperwork is nightmare.", "support": 298},
    ]
    
    feedback_docs = []
    for scheme in schemes:
        feedback_docs.append({
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "user_district": random.choice(list(DISTRICT_ISSUES.keys())),
            "scheme_name": scheme["name"],
            "feedback_type": scheme["type"],
            "action": scheme["action"],
            "description": scheme["desc"],
            "support_count": scheme["support"],
            "in_review_queue": scheme["support"] >= 100,
            "review_queue_date": datetime.now(timezone.utc).isoformat() if scheme["support"] >= 100 else None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(10, 90))).isoformat()
        })
    
    await db.scheme_feedback.delete_many({})
    await db.scheme_feedback.insert_many(feedback_docs)
    print(f"✓ Created {len(feedback_docs)} scheme feedback entries")

async def main():
    print("\n🌱 Seeding Makkal Kural with ALL 38 Tamil Nadu Districts...\n")
    
    users = await create_users(5)
    issues = await create_all_district_issues(users)
    await create_votes_and_comments(users, issues)
    await create_scheme_feedback()
    
    # Clear notifications
    await db.notifications.delete_many({})
    
    print("\n" + "="*60)
    print("✅ Database seeding complete!")
    print("="*60)
    print(f"   Districts: {len(DISTRICT_ISSUES)}")
    print(f"   Users: {len(users)}")
    print(f"   Issues: {len(issues)}")
    print(f"   Categories covered: {len(set(i['category'] for i in issues))}")
    print("="*60)
    
    # Summary by district
    print("\n📊 Issues by District:")
    district_count = {}
    for issue in issues:
        d = issue["district"]
        district_count[d] = district_count.get(d, 0) + 1
    for district, count in sorted(district_count.items()):
        print(f"   {district}: {count} issues")

if __name__ == "__main__":
    asyncio.run(main())
