"""
Comprehensive Seed Script for Makkal Kural
Seeds real issues based on 2024-2025 Tamil Nadu research data
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from constituencies import TAMIL_NADU_CONSTITUENCIES
from real_issues_data import REAL_ISSUES_DATA, ISSUE_CATEGORIES_DETAILED

load_dotenv()

mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
db_name = os.environ.get("DB_NAME", "makkal_kural_governance")

# Real issues based on research
REAL_ISSUES = [
    # Chennai - Water & Flooding
    {"district": "Chennai", "constituency": "Thiruvottiyur", "category": "water", "problem_id": "water_shortage",
     "title_ta": "மின்ஜூர் கடல்நீர் சுத்திகரிப்பு நிலைய நிறுத்தம்", "title_en": "Minjur Desalination Plant Shutdown",
     "description": "Minjur desalination plant shutdown causing severe water shortage. 100 MLD capacity loss affecting Ernavur, Manali, and Thiruvottiyur. Residents paying Rs 1500+ for private tankers.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Chennai", "constituency": "Velachery", "category": "flooding", "problem_id": "drainage_flooding",
     "title_ta": "வெள்ளப்பெருக்கு - மழைநீர் வடிகால் தோல்வி", "title_en": "Flooding Due to Drainage Failure",
     "description": "Every monsoon, Velachery gets flooded due to poor storm water drainage. Cyclone Michaung caused massive damage. Rs 4000 crore spent but no visible improvement.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Chennai", "constituency": "Madhavaram", "category": "garbage", "problem_id": "waste_dumping",
     "title_ta": "கொடுங்கையூர் குப்பை கிடங்கு சுகாதார கேடு", "title_en": "Kodungaiyur Dumpyard Health Hazard",
     "description": "Unsegregated waste at Kodungaiyur causing air pollution, foul odour, and health issues. Children suffering from respiratory problems. No proper waste processing.",
     "severity": "critical", "affected_people": "50-500"},
    
    {"district": "Chennai", "constituency": "Perambur", "category": "roads", "problem_id": "road_damage",
     "title_ta": "மழையால் சேதமடைந்த சாலைகள்", "title_en": "Rain-Damaged Roads with Potholes",
     "description": "Paper Mills Road and New Avadi Road full of potholes after monsoon. Several accidents reported. CCMC promising repairs for months but no action.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Coimbatore - Roads
    {"district": "Coimbatore", "constituency": "Coimbatore North", "category": "roads", "problem_id": "road_damage",
     "title_ta": "ரூ.415 கோடி செலவிட்டும் சாலைகள் சேதம்", "title_en": "Roads Damaged Despite Rs 415 Crore Spent",
     "description": "Vadavalli-Thondamuthur, Vilankurichi-Thaneerpandal stretches are accident hotspots. Rs 415 crore spent on 5,215 roads but 75% still damaged. Fatal accidents increasing.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Coimbatore", "constituency": "Pollachi", "category": "water", "problem_id": "borewell_failure",
     "title_ta": "வறட்சியால் ஆழ்துளை கிணறுகள் வற்றின", "title_en": "Borewells Dried Up Due to Drought",
     "description": "Western catchment drought affecting Pollachi. Borewells dried up in 50+ villages. Farmers paying Rs 2000+ for tanker water. Coconut and banana crops dying.",
     "severity": "critical", "affected_people": "entire_area"},
    
    # Madurai - Pollution & Power
    {"district": "Madurai", "constituency": "Madurai Central", "category": "pollution", "problem_id": "river_pollution",
     "title_ta": "வைகை ஆறு கடுமையாக மாசுபட்டது", "title_en": "Vaigai River Severely Polluted",
     "description": "Vaigai River has become dirty and odorous. Raw sewage entering river. Encroachment on riverbed reducing flood capacity. Downstream groundwater contaminated.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Madurai", "constituency": "Madurai East", "category": "electricity", "problem_id": "power_cuts",
     "title_ta": "உச்ச நேரத்தில் அடிக்கடி மின்தடை", "title_en": "Frequent Power Cuts During Peak Hours",
     "description": "Power outages in Kalavasal, Palaganatham, K Pudur due to transformer overload. 40°C heat making life difficult. New 110 kV substation promised but not built.",
     "severity": "high", "affected_people": "50-500"},
    
    # Tiruppur - Pollution
    {"district": "Tiruppur", "constituency": "Tiruppur North", "category": "garbage", "problem_id": "waste_dumping",
     "title_ta": "குவாரிகளில் 800 டன் குப்பை தினமும்", "title_en": "800 Tonnes Waste Dumped in Quarries Daily",
     "description": "Mudalipalayam and Kalampalayam villages suffering. 700-800 metric tonnes unsegregated waste dumped daily in abandoned quarries. Groundwater TDS at dangerous levels.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Tiruppur", "constituency": "Tiruppur South", "category": "health", "problem_id": "pollution_health_impact",
     "title_ta": "மாசுவால் சிறுநீரக நோய்கள் அதிகரிப்பு", "title_en": "Kidney Diseases Increasing Due to Pollution",
     "description": "Residents suffering from skin ailments, kidney diseases, and respiratory problems. Leachate from waste dumps contaminating drinking water. TNPCB not responding.",
     "severity": "critical", "affected_people": "50-500"},
    
    # Thanjavur - Farming
    {"district": "Thanjavur", "constituency": "Kumbakonam", "category": "farming", "problem_id": "irrigation_crisis",
     "title_ta": "காவிரி டெல்டா பாசன நெருக்கடி", "title_en": "Cauvery Delta Irrigation Crisis",
     "description": "Delayed water release from Mettur dam affecting kuruvai and samba crops. Farmers losing lakhs. Government compensation of Rs 10,000 per acre is inadequate.",
     "severity": "critical", "affected_people": "entire_area"},
    
    {"district": "Thanjavur", "constituency": "Pattukkottai", "category": "flooding", "problem_id": "cyclone_damage",
     "title_ta": "புயலால் நெற்பயிர் சேதம்", "title_en": "Paddy Crops Damaged by Cyclone",
     "description": "Standing paddy crops destroyed by cyclone. 10,000+ acres affected. Crop insurance claims pending for months. Farmers demanding immediate relief.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Dharmapuri - Health & Water
    {"district": "Dharmapuri", "constituency": "Dharmapuri", "category": "health", "problem_id": "hospital_shortage",
     "title_ta": "மருத்துவர் மற்றும் செவிலியர் பற்றாக்குறை", "title_en": "Severe Doctor and Nurse Shortage",
     "description": "PHCs and CHCs understaffed. Only 2 doctors for 50,000 population. Patients traveling 50+ km for treatment. Rs 57.85 crore sanctioned but not utilized.",
     "severity": "high", "affected_people": "entire_area"},
    
    {"district": "Dharmapuri", "constituency": "Harur", "category": "water", "problem_id": "borewell_failure",
     "title_ta": "22 வறட்சி மாவட்டங்களில் ஒன்று", "title_en": "One of 22 Drought-Hit Districts",
     "description": "Borewells dried up in 100+ villages. Rs 150 crore SDRF released but tanker supply irregular. Women walking 2+ km for water. Livestock dying.",
     "severity": "critical", "affected_people": "entire_area"},
    
    # Erode - Pollution
    {"district": "Erode", "constituency": "Bhavani", "category": "pollution", "problem_id": "industrial_pollution",
     "title_ta": "ஜவுளி சாயப்பட்டறை கழிவு மாசு", "title_en": "Textile Dyeing Unit Effluent Pollution",
     "description": "Untreated effluent from dyeing units entering Bhavani and Noyyal rivers. Groundwater turning colored. Crops failing. TNPCB orders ignored.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Salem - Roads
    {"district": "Salem", "constituency": "Salem North", "category": "roads", "problem_id": "highway_accidents",
     "title_ta": "சேலம்-சென்னை நெடுஞ்சாலை விபத்து", "title_en": "Salem-Chennai Highway Accident Hotspot",
     "description": "Highway has become death trap. Poor lighting, no speed breakers near villages. 50+ fatalities this year. Encroachments reducing road width.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Tiruchirappalli
    {"district": "Tiruchirappalli", "constituency": "Lalgudi", "category": "water", "problem_id": "cauvery_water_dispute",
     "title_ta": "மேட்டூர் அணை நீர் பங்கீடு பிரச்சனை", "title_en": "Mettur Dam Water Distribution Issue",
     "description": "Irregular water release from Mettur affecting kuruvai cultivation. Farmers demanding regulated schedule. Canal maintenance poor. Water theft rampant.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Tirunelveli
    {"district": "Tirunelveli", "constituency": "Ambasamudram", "category": "water", "problem_id": "irrigation_crisis",
     "title_ta": "பாபநாசம் அணை நீர் பிரச்சனை", "title_en": "Papanasam Dam Water Release Issue",
     "description": "Irregular release from Papanasam and Manimuthar dams. Tail-end farmers not getting water. Canal system needs Rs 100 crore repair.",
     "severity": "medium", "affected_people": "50-500"},
    
    # Kanniyakumari
    {"district": "Kanniyakumari", "constituency": "Nagercoil", "category": "flooding", "problem_id": "drainage_flooding",
     "title_ta": "மழைக்காலத்தில் வெள்ளம்", "title_en": "Monsoon Flooding in Low-Lying Areas",
     "description": "Parakkai and Nagercoil areas flood every monsoon. Drainage system built 30 years ago. Rs 50 crore needed for upgrades. Shops lose lakhs every year.",
     "severity": "medium", "affected_people": "50-500"},
    
    # Nilgiris
    {"district": "Nilgiris", "constituency": "Udhagamandalam", "category": "roads", "problem_id": "road_damage",
     "title_ta": "மலைப்பாதை சேதம்", "title_en": "Hill Road Damage After Landslides",
     "description": "Landslides damaged Ooty-Coonoor road. Tourists stranded. NHAI repairs temporary. Permanent solution needed. Local economy suffering.",
     "severity": "medium", "affected_people": "entire_area"},
    
    # Vellore
    {"district": "Vellore", "constituency": "Vellore", "category": "health", "problem_id": "hospital_shortage",
     "title_ta": "அரசு மருத்துவமனை கூட்டநெரிசல்", "title_en": "Government Hospital Overcrowding",
     "description": "Vellore GH handling 3x capacity. 100-bed hospital seeing 500+ patients daily. Staff exhausted. New block construction delayed by 2 years.",
     "severity": "high", "affected_people": "entire_area"},
    
    # Cuddalore
    {"district": "Cuddalore", "constituency": "Cuddalore", "category": "pollution", "problem_id": "industrial_pollution",
     "title_ta": "SIPCOT தொழிற்பேட்டை மாசு", "title_en": "SIPCOT Industrial Estate Pollution",
     "description": "Chemical industries releasing toxic fumes. Cancer cases increasing in nearby villages. TNPCB notices ignored. Residents demanding relocation.",
     "severity": "critical", "affected_people": "entire_area"},
    
    # Ranipet
    {"district": "Ranipet", "constituency": "Ranipet", "category": "pollution", "problem_id": "industrial_pollution",
     "title_ta": "தோல் பதனிடும் தொழிற்சாலை மாசு", "title_en": "Tannery Pollution Crisis",
     "description": "Tannery effluent contaminating Palar river. Groundwater chromium levels 100x safe limit. Villages drinking poisoned water. Supreme Court orders not implemented.",
     "severity": "critical", "affected_people": "entire_area"},
]

# Generate more issues for all constituencies
def generate_constituency_issues():
    """Generate realistic issues for all 234 constituencies"""
    issues = []
    
    categories = ["water", "roads", "flooding", "garbage", "pollution", "electricity", "health", "farming", "sewage"]
    
    problems_by_category = {
        "water": ["water_shortage", "contaminated_water", "borewell_failure", "irregular_supply"],
        "roads": ["road_damage", "highway_accidents", "traffic_congestion", "street_lights"],
        "flooding": ["drainage_flooding", "stagnant_water", "encroachment_flooding"],
        "garbage": ["waste_dumping", "no_collection", "landfill_issues"],
        "pollution": ["industrial_pollution", "river_pollution", "air_pollution"],
        "electricity": ["power_cuts", "transformer_failure", "voltage_fluctuation"],
        "health": ["hospital_shortage", "doctor_shortage", "medicine_shortage"],
        "farming": ["irrigation_crisis", "crop_damage", "market_price"],
        "sewage": ["sewage_overflow", "blocked_drains", "no_sewage_system"]
    }
    
    titles = {
        "water_shortage": {"en": "Drinking Water Shortage", "ta": "குடிநீர் பற்றாக்குறை"},
        "contaminated_water": {"en": "Contaminated Water Supply", "ta": "மாசுபட்ட நீர் வழங்கல்"},
        "borewell_failure": {"en": "Borewells Dried Up", "ta": "ஆழ்துளை கிணறுகள் வற்றின"},
        "irregular_supply": {"en": "Irregular Water Supply", "ta": "ஒழுங்கற்ற நீர் வழங்கல்"},
        "road_damage": {"en": "Damaged Roads Need Repair", "ta": "சேதமடைந்த சாலைகள் பழுது தேவை"},
        "highway_accidents": {"en": "Accident-Prone Road Stretch", "ta": "விபத்து ஏற்படும் சாலை பகுதி"},
        "traffic_congestion": {"en": "Heavy Traffic Congestion", "ta": "கடும் போக்குவரத்து நெரிசல்"},
        "street_lights": {"en": "No Street Lights", "ta": "தெரு விளக்குகள் இல்லை"},
        "drainage_flooding": {"en": "Flooding Due to Poor Drainage", "ta": "மோசமான வடிகால் காரணமாக வெள்ளம்"},
        "stagnant_water": {"en": "Stagnant Water Breeding Mosquitoes", "ta": "தேங்கும் நீரில் கொசுக்கள்"},
        "encroachment_flooding": {"en": "Encroachment Causing Floods", "ta": "ஆக்கிரமிப்பு வெள்ளத்தை ஏற்படுத்துகிறது"},
        "waste_dumping": {"en": "Illegal Waste Dumping", "ta": "சட்டவிரோத குப்பை கொட்டுதல்"},
        "no_collection": {"en": "No Garbage Collection Service", "ta": "குப்பை சேகரிப்பு சேவை இல்லை"},
        "landfill_issues": {"en": "Overflowing Landfill", "ta": "நிரம்பி வழியும் குப்பை மேடு"},
        "industrial_pollution": {"en": "Industrial Pollution", "ta": "தொழிற்சாலை மாசு"},
        "river_pollution": {"en": "River Water Pollution", "ta": "ஆற்று நீர் மாசு"},
        "air_pollution": {"en": "Severe Air Pollution", "ta": "கடும் காற்று மாசு"},
        "power_cuts": {"en": "Frequent Power Cuts", "ta": "அடிக்கடி மின்தடை"},
        "transformer_failure": {"en": "Transformer Needs Replacement", "ta": "மின்மாற்றி மாற்ற வேண்டும்"},
        "voltage_fluctuation": {"en": "Voltage Fluctuation Issues", "ta": "மின்னழுத்த ஏற்றத்தாழ்வு"},
        "hospital_shortage": {"en": "No Hospital Nearby", "ta": "அருகில் மருத்துவமனை இல்லை"},
        "doctor_shortage": {"en": "Doctor Shortage at PHC", "ta": "PHC-யில் மருத்துவர் பற்றாக்குறை"},
        "medicine_shortage": {"en": "Essential Medicines Not Available", "ta": "அத்தியாவசிய மருந்துகள் இல்லை"},
        "irrigation_crisis": {"en": "Irrigation Water Not Reaching", "ta": "பாசன நீர் வரவில்லை"},
        "crop_damage": {"en": "Crops Damaged by Weather", "ta": "வானிலையால் பயிர் சேதம்"},
        "market_price": {"en": "Low Price for Farm Produce", "ta": "விளைபொருளுக்கு குறைந்த விலை"},
        "sewage_overflow": {"en": "Sewage Overflow on Streets", "ta": "தெருவில் கழிவுநீர் வழிதல்"},
        "blocked_drains": {"en": "Drains Blocked and Overflowing", "ta": "வடிகால்கள் அடைத்து வழிகின்றன"},
        "no_sewage_system": {"en": "No Proper Sewage System", "ta": "சரியான கழிவுநீர் அமைப்பு இல்லை"}
    }
    
    descriptions = {
        "water_shortage": "Residents facing severe water shortage for the past {months} months. Tanker water costs Rs {cost} per load. Women and children walking {km} km to fetch water.",
        "contaminated_water": "Water supply has turned yellow/brown and smells bad. Lab tests show high TDS and bacteria levels. Many residents suffering from stomach issues.",
        "borewell_failure": "Groundwater table has dropped drastically. {count} borewells in the area have dried up. Agricultural activities completely stopped.",
        "road_damage": "Main road has {count} major potholes in {length} km stretch. {accidents} accidents reported in last month. Vehicles getting damaged daily.",
        "power_cuts": "Power cuts lasting {hours} hours daily during peak summer. Transformers overloaded. Small businesses and students suffering badly.",
        "drainage_flooding": "Every rain causes flooding in low-lying areas. Water enters {count} houses. Storm water drains not cleaned for {years} years.",
        "garbage": "Garbage not collected for {days} days. Piling up on streets attracting rats and insects. Foul smell making life unbearable for residents.",
        "hospital_shortage": "Nearest hospital is {km} km away. Emergency cases face life-threatening delays. Pregnant women forced to travel long distances.",
    }
    
    for district, constituencies in TAMIL_NADU_CONSTITUENCIES.items():
        for constituency in constituencies:
            # Generate 2-4 issues per constituency
            num_issues = random.randint(2, 4)
            used_categories = set()
            
            for _ in range(num_issues):
                # Pick a category not yet used for this constituency
                available_cats = [c for c in categories if c not in used_categories]
                if not available_cats:
                    available_cats = categories
                
                category = random.choice(available_cats)
                used_categories.add(category)
                
                problem_id = random.choice(problems_by_category[category])
                title_info = titles.get(problem_id, {"en": "Local Issue", "ta": "உள்ளூர் பிரச்சனை"})
                
                # Generate description with random values
                desc_template = descriptions.get(category, descriptions.get("water_shortage"))
                description = desc_template.format(
                    months=random.randint(2, 12),
                    cost=random.randint(500, 2000),
                    km=random.randint(1, 5),
                    count=random.randint(5, 50),
                    length=random.randint(1, 5),
                    accidents=random.randint(2, 10),
                    hours=random.randint(2, 8),
                    years=random.randint(2, 5),
                    days=random.randint(3, 15)
                )
                
                issues.append({
                    "district": district,
                    "constituency": constituency,
                    "category": category,
                    "problem_id": problem_id,
                    "title_ta": f"{constituency} - {title_info['ta']}",
                    "title_en": f"{constituency} - {title_info['en']}",
                    "description": description,
                    "severity": random.choice(["critical", "high", "medium"]),
                    "affected_people": random.choice(["only_me", "10-50", "50-500", "entire_area"])
                })
    
    return issues

async def main():
    print("🌱 Seeding Makkal Kural with Real Tamil Nadu Issues...")
    print("=" * 60)
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    await db.issues.delete_many({})
    await db.votes.delete_many({})
    await db.users.delete_many({})
    
    # Create sample users for each district
    print("\n👥 Creating users for each district...")
    users = []
    user_count = 0
    
    for district in TAMIL_NADU_CONSTITUENCIES.keys():
        for i in range(5):  # 5 users per district
            user_id = str(uuid.uuid4())
            phone = f"9{random.randint(100000000, 999999999)}"
            users.append({
                "id": user_id,
                "mobile": phone,
                "name": f"Citizen {user_count + 1}",
                "district": district,
                "local_body_type": random.choice(["Corporation", "Municipality", "Town Panchayat"]),
                "local_body_name": f"{district} Local Body",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "issues_raised": 0,
                "votes_cast": 0
            })
            user_count += 1
    
    await db.users.insert_many(users)
    print(f"   ✓ Created {len(users)} users across {len(TAMIL_NADU_CONSTITUENCIES)} districts")
    
    # Combine real issues with generated issues
    all_issues = REAL_ISSUES + generate_constituency_issues()
    print(f"\n📋 Preparing {len(all_issues)} issues...")
    
    # Create issues
    issue_docs = []
    for issue_data in all_issues:
        district = issue_data["district"]
        district_users = [u for u in users if u["district"] == district]
        if not district_users:
            district_users = users
        
        creator = random.choice(district_users)
        issue_id = str(uuid.uuid4())
        
        # Generate support/oppose counts
        support_count = random.randint(10, 500)
        oppose_count = random.randint(0, int(support_count * 0.3))
        total_votes = support_count + oppose_count
        support_percentage = round((support_count / total_votes * 100)) if total_votes > 0 else 0
        
        # Determine status based on support
        if support_count >= 100:
            status = "serious_issue"
            current_level = random.randint(3, 5)
        elif support_count >= 25:
            status = "area_concern"
            current_level = random.randint(2, 3)
        else:
            status = "pending"
            current_level = 1
        
        # Random chance of resolution
        if random.random() < 0.1:
            status = "resolved"
        
        created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))
        
        issue_doc = {
            "id": issue_id,
            "user_id": creator["id"],
            "user_name": creator["name"],
            "user_mobile": creator["mobile"][-4:],
            "district": district,
            "constituency": issue_data.get("constituency", ""),
            "local_body_type": creator["local_body_type"],
            "local_body_name": creator["local_body_name"],
            "ward": f"Ward {random.randint(1, 50)}",
            "category": issue_data["category"],
            "category_name_en": ISSUE_CATEGORIES_DETAILED.get(issue_data["category"], {}).get("name_en", issue_data["category"]),
            "category_name_ta": ISSUE_CATEGORIES_DETAILED.get(issue_data["category"], {}).get("name_ta", issue_data["category"]),
            "problem_id": issue_data["problem_id"],
            "problem_name_en": issue_data.get("title_en", issue_data["problem_id"]),
            "problem_name_ta": issue_data.get("title_ta", issue_data["problem_id"]),
            "description": issue_data["description"],
            "frequency": random.choice(["daily", "weekly", "seasonal", "emergency"]),
            "affected_people": issue_data.get("affected_people", "50-500"),
            "duration": random.choice(["weeks", "months", "years"]),
            "media_urls": [],
            "is_anonymous": random.random() < 0.1,
            "status": status,
            "support_count": support_count,
            "oppose_count": oppose_count,
            "support_percentage": support_percentage,
            "publicly_validated": support_percentage >= 60,
            "comment_count": random.randint(0, 20),
            "current_level": current_level,
            "escalation_history": [
                {
                    "level": 1,
                    "name": "Village Administrative Officer",
                    "reached_at": created_at.isoformat(),
                    "sla_deadline": (created_at + timedelta(days=7)).isoformat()
                }
            ],
            "created_at": created_at.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add more escalation history if level > 1
        for level in range(2, current_level + 1):
            level_names = {
                2: "Block Development Officer",
                3: "District Collector",
                4: "Department Secretary",
                5: "Concerned Minister",
                6: "Chief Secretary",
                7: "Chief Minister"
            }
            level_days = {2: 14, 3: 30, 4: 45, 5: 60, 6: 75, 7: 90}
            
            reached_date = created_at + timedelta(days=level_days.get(level-1, 7))
            issue_doc["escalation_history"].append({
                "level": level,
                "name": level_names.get(level, f"Level {level}"),
                "reached_at": reached_date.isoformat(),
                "sla_deadline": (reached_date + timedelta(days=level_days.get(level, 30))).isoformat()
            })
        
        issue_docs.append(issue_doc)
    
    # Insert issues
    await db.issues.insert_many(issue_docs)
    print(f"   ✓ Created {len(issue_docs)} issues")
    
    # Generate votes
    print("\n🗳️  Generating votes...")
    vote_docs = []
    
    for issue in issue_docs:
        # Create support votes
        for _ in range(issue["support_count"]):
            voter = random.choice(users)
            vote_docs.append({
                "id": str(uuid.uuid4()),
                "user_id": voter["id"],
                "issue_id": issue["id"],
                "vote_type": "support",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        # Create oppose votes
        for _ in range(issue["oppose_count"]):
            voter = random.choice(users)
            vote_docs.append({
                "id": str(uuid.uuid4()),
                "user_id": voter["id"],
                "issue_id": issue["id"],
                "vote_type": "oppose",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
    
    # Insert votes in batches
    batch_size = 1000
    for i in range(0, len(vote_docs), batch_size):
        batch = vote_docs[i:i + batch_size]
        await db.votes.insert_many(batch)
    
    print(f"   ✓ Created {len(vote_docs)} votes")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    print(f"   Users: {len(users)}")
    print(f"   Issues: {len(issue_docs)}")
    print(f"   Votes: {len(vote_docs)}")
    print(f"   Districts: {len(TAMIL_NADU_CONSTITUENCIES)}")
    print(f"   Constituencies: 234")
    
    # Show district-wise breakdown
    print("\n📊 District-wise Issue Count:")
    district_counts = {}
    for issue in issue_docs:
        d = issue["district"]
        district_counts[d] = district_counts.get(d, 0) + 1
    
    for district, count in sorted(district_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"   {district}: {count} issues")
    
    print("\n🎯 Top Categories:")
    category_counts = {}
    for issue in issue_docs:
        c = issue["category"]
        category_counts[c] = category_counts.get(c, 0) + 1
    
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"   {category}: {count} issues")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
