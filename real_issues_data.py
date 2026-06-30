# Real Issues Data for Tamil Nadu - Based on 2024-2025 Research
# Source: News reports, government data, citizen grievances

REAL_ISSUES_DATA = {
    # Chennai Districts and Constituencies
    "Chennai": {
        "district_issues": [
            {
                "category": "water",
                "problem": "water_shortage",
                "title_en": "Severe Water Shortage in North Chennai",
                "title_ta": "வட சென்னையில் கடும் குடிநீர் பற்றாக்குறை",
                "description": "Minjur desalination plant shutdown causing severe water shortage in Ernavur, Manali, and Thiruvottiyur. Residents forced to rely on expensive private tankers.",
                "affected_areas": ["Thiruvottiyur", "Manali", "Ernavur", "Royapuram"],
                "severity": "critical"
            },
            {
                "category": "flooding",
                "problem": "drainage_flooding",
                "title_en": "Storm Water Drainage Works Causing Flooding",
                "title_ta": "மழைநீர் வடிகால் பணிகள் வெள்ளத்தை ஏற்படுத்துகின்றன",
                "description": "Prolonged storm water drainage works in North Chennai causing chronic traffic jams and flooding during monsoon. Works dragging on for years without completion.",
                "affected_areas": ["Perambur", "Kolathur", "Villivakkam", "Ambattur"],
                "severity": "high"
            },
            {
                "category": "garbage",
                "problem": "waste_dumping",
                "title_en": "Kodungaiyur Dumping Yard Health Hazard",
                "title_ta": "கொடுங்கையூர் குப்பை கிடங்கு உடல்நலக் கேடு",
                "description": "Unsegregated waste dumping at Kodungaiyur causing air and soil pollution, foul odour, and health issues for nearby residents. No proper waste processing.",
                "affected_areas": ["Madhavaram", "Thiruvottiyur"],
                "severity": "critical"
            },
            {
                "category": "roads",
                "problem": "road_damage",
                "title_en": "Poor Road Conditions After Monsoon",
                "title_ta": "பருவமழைக்குப் பிறகு மோசமான சாலை நிலை",
                "description": "Roads in Chennai deteriorating rapidly after monsoon. Potholes causing accidents. New Avadi Road, Paper Mills Road need urgent repair.",
                "affected_areas": ["Avadi", "Ambattur", "Anna Nagar", "Maduravoyal"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Egmore": {"water": 3, "roads": 2, "garbage": 1},
            "Royapuram": {"water": 4, "flooding": 3, "sewage": 2},
            "Harbour": {"flooding": 4, "roads": 2, "pollution": 3},
            "Thiruvottiyur": {"water": 5, "garbage": 4, "health": 2},
            "Perambur": {"flooding": 4, "roads": 3, "garbage": 2},
            "Kolathur": {"flooding": 3, "water": 2, "roads": 2},
            "Villivakkam": {"roads": 3, "flooding": 2, "garbage": 2},
            "Thiru-Vi-Ka-Nagar": {"water": 2, "roads": 3, "sewage": 2},
            "Anna Nagar": {"flooding": 2, "roads": 2, "garbage": 1},
            "Virugampakkam": {"roads": 3, "water": 2, "flooding": 2},
            "Saidapet": {"flooding": 3, "sewage": 2, "roads": 2},
            "Mylapore": {"flooding": 2, "roads": 2, "garbage": 1},
            "Velachery": {"flooding": 4, "roads": 3, "sewage": 3},
            "Sholinganallur": {"flooding": 3, "roads": 3, "water": 2},
            "Alandur": {"flooding": 3, "roads": 2, "garbage": 2},
            "Maduravoyal": {"roads": 3, "flooding": 2, "water": 2},
            "Ambattur": {"roads": 4, "flooding": 3, "garbage": 2},
            "Madhavaram": {"garbage": 4, "water": 3, "roads": 2},
            "Dr. Radhakrishnan Nagar": {"water": 3, "roads": 2, "flooding": 2},
            "Chepauk-Thiruvallikeni": {"flooding": 3, "roads": 2, "heritage": 2},
            "Thousand Lights": {"roads": 2, "flooding": 2, "parking": 2},
            "Thiyagarayanagar": {"roads": 2, "parking": 3, "flooding": 2}
        }
    },
    
    "Coimbatore": {
        "district_issues": [
            {
                "category": "roads",
                "problem": "road_damage",
                "title_en": "Widespread Road Damage Despite Rs 415 Crore Spent",
                "title_ta": "ரூ.415 கோடி செலவிட்டும் பரவலான சாலை சேதம்",
                "description": "Roads in 100+ wards damaged despite Rs 415 crore spent on relaying. Vadavalli-Thondamuthur, Vilankurichi-Thaneerpandal stretches are accident hotspots.",
                "affected_areas": ["Vadavalli", "Thondamuthur", "Vilankurichi", "Sanganoor"],
                "severity": "critical"
            },
            {
                "category": "water",
                "problem": "water_shortage",
                "title_en": "Drinking Water Crisis in Western Areas",
                "title_ta": "மேற்குப் பகுதிகளில் குடிநீர் நெருக்கடி",
                "description": "Borewells dried up in many areas due to drought. Western catchment areas facing acute water shortage. Residents paying high prices for private tankers.",
                "affected_areas": ["Mettupalayam", "Sulur", "Pollachi"],
                "severity": "high"
            },
            {
                "category": "pollution",
                "problem": "industrial_pollution",
                "title_en": "Textile Dyeing Unit Pollution",
                "title_ta": "ஜவுளி சாயப்பட்டறை மாசு",
                "description": "Illegal discharge from textile dyeing units contaminating Noyyal River and groundwater. Farmers unable to use water for irrigation.",
                "affected_areas": ["Tiruppur", "Avanashi", "Palladam"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Coimbatore North": {"roads": 4, "traffic": 3, "parking": 2},
            "Coimbatore South": {"roads": 3, "water": 2, "flooding": 2},
            "Singanallur": {"roads": 3, "flooding": 3, "garbage": 2},
            "Kavundampalayam": {"roads": 3, "water": 2, "sewage": 2},
            "Kinathukadavu": {"water": 4, "roads": 3, "farming": 2},
            "Pollachi": {"water": 4, "roads": 2, "farming": 3},
            "Valparai": {"roads": 3, "health": 2, "transport": 3},
            "Sulur": {"water": 3, "roads": 2, "pollution": 2},
            "Mettupalayam": {"water": 4, "roads": 3, "health": 2},
            "Thondamuthur": {"roads": 4, "water": 3, "farming": 2}
        }
    },
    
    "Madurai": {
        "district_issues": [
            {
                "category": "pollution",
                "problem": "river_pollution",
                "title_en": "Vaigai River Severely Polluted",
                "title_ta": "வைகை ஆறு கடுமையாக மாசுபட்டுள்ளது",
                "description": "Vaigai River has become dirty, odorous and heavily polluted. Raw sewage entering the river affecting downstream groundwater and agriculture.",
                "affected_areas": ["All Madurai constituencies"],
                "severity": "critical"
            },
            {
                "category": "electricity",
                "problem": "power_cuts",
                "title_en": "Frequent Power Cuts During Peak Hours",
                "title_ta": "உச்ச நேரத்தில் அடிக்கடி மின்தடை",
                "description": "Power outages in Kalavasal, Palaganatham, K Pudur, Teppam due to transformer strain. Night cuts from high loads. New substation needed urgently.",
                "affected_areas": ["Kalavasal", "Palaganatham", "K Pudur", "Panagudi"],
                "severity": "high"
            },
            {
                "category": "flooding",
                "problem": "encroachment_flooding",
                "title_en": "Encroachment on Flood Zones Causing Risk",
                "title_ta": "வெள்ளப்பகுதி ஆக்கிரமிப்பு ஆபத்தை ஏற்படுத்துகிறது",
                "description": "Encroachment on Vaigai riverbed and flood-spread zones reducing natural drainage capacity and raising flood risk during monsoon.",
                "affected_areas": ["Madurai Central", "Madurai East", "Madurai West"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Madurai East": {"pollution": 4, "flooding": 3, "roads": 2},
            "Madurai West": {"pollution": 3, "electricity": 3, "roads": 2},
            "Madurai North": {"water": 3, "roads": 3, "health": 2},
            "Madurai South": {"flooding": 3, "sewage": 3, "roads": 2},
            "Madurai Central": {"pollution": 4, "flooding": 3, "traffic": 3},
            "Melur": {"water": 4, "roads": 3, "farming": 3},
            "Sholavandan": {"water": 3, "roads": 2, "farming": 2},
            "Thiruparankundram": {"roads": 3, "water": 2, "flooding": 2},
            "Tirumangalam": {"water": 3, "roads": 3, "health": 2},
            "Usilampatti": {"water": 4, "roads": 3, "farming": 3}
        }
    },
    
    "Tiruppur": {
        "district_issues": [
            {
                "category": "garbage",
                "problem": "illegal_dumping",
                "title_en": "Massive Illegal Waste Dumping in Quarries",
                "title_ta": "குவாரிகளில் பாரிய சட்டவிரோத குப்பை கொட்டுதல்",
                "description": "700-800 metric tonnes of unsegregated municipal waste dumped daily in abandoned quarries at Mudalipalayam and Kalampalayam. Groundwater contamination severe.",
                "affected_areas": ["Mudalipalayam", "Kalampalayam", "Tiruppur North"],
                "severity": "critical"
            },
            {
                "category": "water",
                "problem": "groundwater_contamination",
                "title_en": "Groundwater Contamination from Waste Leachate",
                "title_ta": "குப்பைக் கசிவால் நிலத்தடி நீர் மாசு",
                "description": "TDS levels far above safe limits. Blackish-gray stagnant water in quarries. Crops like banana, coconut, turmeric have become unviable due to polluted water.",
                "affected_areas": ["Tiruppur South", "Palladam", "Avanashi"],
                "severity": "critical"
            },
            {
                "category": "health",
                "problem": "pollution_health_impact",
                "title_en": "Health Crisis from Pollution Exposure",
                "title_ta": "மாசு வெளிப்பாட்டால் சுகாதார நெருக்கடி",
                "description": "Residents suffering from skin ailments, kidney-related illnesses and respiratory complaints due to chronic exposure to leachate and burning waste.",
                "affected_areas": ["Tiruppur North", "Tiruppur South", "Udumalaipettai"],
                "severity": "critical"
            }
        ],
        "constituencies": {
            "Tiruppur North": {"garbage": 5, "pollution": 5, "health": 4},
            "Tiruppur South": {"pollution": 4, "water": 4, "health": 3},
            "Palladam": {"pollution": 4, "water": 3, "roads": 2},
            "Avanashi": {"pollution": 4, "roads": 3, "water": 3},
            "Udumalaipettai": {"water": 3, "roads": 3, "health": 2},
            "Madathukulam": {"water": 4, "farming": 3, "roads": 2}
        }
    },
    
    "Tiruchirappalli": {
        "district_issues": [
            {
                "category": "water",
                "problem": "cauvery_water_dispute",
                "title_en": "Cauvery Water Distribution Issues",
                "title_ta": "காவிரி நீர் பங்கீட்டு பிரச்சனைகள்",
                "description": "Farmers facing water shortage due to irregular release from Mettur dam. Kuruvai and Samba crops affected. Need better water management.",
                "affected_areas": ["Lalgudi", "Musiri", "Manapparai"],
                "severity": "high"
            },
            {
                "category": "roads",
                "problem": "road_damage",
                "title_en": "NH and State Highway Condition Poor",
                "title_ta": "தேசிய நெடுஞ்சாலை மற்றும் மாநில நெடுஞ்சாலை நிலை மோசம்",
                "description": "Several stretches of highways in poor condition causing accidents. Truckers and bus operators complaining of damage to vehicles.",
                "affected_areas": ["Tiruchirappalli East", "Tiruchirappalli West", "Srirangam"],
                "severity": "medium"
            }
        ],
        "constituencies": {
            "Tiruchirappalli East": {"roads": 3, "flooding": 2, "traffic": 3},
            "Tiruchirappalli West": {"roads": 3, "water": 2, "health": 2},
            "Srirangam": {"flooding": 3, "heritage": 2, "roads": 2},
            "Thiruverumbur": {"roads": 3, "water": 2, "sewage": 2},
            "Lalgudi": {"water": 4, "farming": 3, "roads": 2},
            "Manachanallur": {"water": 3, "roads": 2, "farming": 2},
            "Musiri": {"water": 4, "farming": 3, "roads": 2},
            "Manapparai": {"water": 3, "roads": 3, "farming": 2},
            "Thurayur": {"water": 3, "roads": 2, "farming": 2}
        }
    },
    
    "Salem": {
        "district_issues": [
            {
                "category": "roads",
                "problem": "highway_accidents",
                "title_en": "High Accident Rate on Salem-Chennai Highway",
                "title_ta": "சேலம்-சென்னை நெடுஞ்சாலையில் அதிக விபத்து விகிதம்",
                "description": "Salem-Chennai highway has become an accident hotspot. Poor lighting, lack of speed breakers near villages, and encroachments causing fatalities.",
                "affected_areas": ["Salem North", "Salem South", "Omalur"],
                "severity": "high"
            },
            {
                "category": "pollution",
                "problem": "mining_pollution",
                "title_en": "Illegal Mining Causing Environmental Damage",
                "title_ta": "சட்டவிரோத சுரங்கம் சுற்றுச்சூழல் சேதத்தை ஏற்படுத்துகிறது",
                "description": "Illegal sand mining and stone quarrying causing environmental damage. Hill erosion and dust pollution affecting nearby villages.",
                "affected_areas": ["Mettur", "Yercaud", "Sankagiri"],
                "severity": "medium"
            }
        ],
        "constituencies": {
            "Salem West": {"roads": 3, "traffic": 3, "pollution": 2},
            "Salem North": {"roads": 3, "water": 2, "health": 2},
            "Salem South": {"roads": 3, "garbage": 2, "sewage": 2},
            "Veerapandi": {"water": 3, "roads": 2, "farming": 2},
            "Mettur": {"pollution": 3, "water": 3, "roads": 2},
            "Omalur": {"roads": 3, "water": 2, "farming": 2},
            "Edappadi": {"water": 3, "roads": 2, "farming": 2},
            "Sankagiri": {"pollution": 2, "roads": 2, "water": 2}
        }
    },
    
    "Thanjavur": {
        "district_issues": [
            {
                "category": "water",
                "problem": "irrigation_crisis",
                "title_en": "Delta Irrigation Crisis",
                "title_ta": "டெல்டா பாசன நெருக்கடி",
                "description": "Cauvery delta farmers facing severe irrigation crisis. Delayed water release from Mettur affecting paddy cultivation. Government compensation inadequate.",
                "affected_areas": ["Thanjavur", "Kumbakonam", "Papanasam", "Thiruvaiyaru"],
                "severity": "critical"
            },
            {
                "category": "flooding",
                "problem": "cyclone_damage",
                "title_en": "Cyclone Damage to Standing Crops",
                "title_ta": "நிற்கும் பயிர்களுக்கு புயல் சேதம்",
                "description": "Frequent cyclones damaging standing paddy crops. Farmers demanding higher compensation and crop insurance reform.",
                "affected_areas": ["Pattukkottai", "Orathanadu", "Peravurani"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Thanjavur": {"water": 4, "flooding": 3, "heritage": 2},
            "Kumbakonam": {"water": 3, "flooding": 3, "health": 2},
            "Papanasam": {"water": 4, "farming": 4, "roads": 2},
            "Thiruvaiyaru": {"water": 4, "farming": 3, "flooding": 2},
            "Thiruvidaimarudur": {"water": 3, "farming": 3, "roads": 2},
            "Orathanadu": {"water": 4, "farming": 4, "flooding": 3},
            "Pattukkottai": {"flooding": 4, "farming": 3, "roads": 2},
            "Peravurani": {"flooding": 3, "farming": 3, "water": 3}
        }
    },
    
    "Tirunelveli": {
        "district_issues": [
            {
                "category": "water",
                "problem": "dam_water_release",
                "title_en": "Papanasam and Manimuthar Dam Water Issues",
                "title_ta": "பாபநாசம் மற்றும் மணிமுத்தாறு அணை நீர் பிரச்சனைகள்",
                "description": "Irregular water release from dams affecting agriculture. Farmers demanding regulated release schedule and better canal maintenance.",
                "affected_areas": ["Tirunelveli", "Ambasamudram", "Palayamkottai"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Tirunelveli": {"water": 3, "roads": 2, "health": 2},
            "Ambasamudram": {"water": 4, "farming": 3, "roads": 2},
            "Palayamkottai": {"roads": 3, "water": 2, "flooding": 2},
            "Nanguneri": {"water": 3, "roads": 2, "farming": 2},
            "Radhapuram": {"water": 3, "farming": 3, "roads": 2}
        }
    },
    
    "Dharmapuri": {
        "district_issues": [
            {
                "category": "health",
                "problem": "hospital_shortage",
                "title_en": "Severe Doctor and Nurse Shortage",
                "title_ta": "கடுமையான மருத்துவர் மற்றும் செவிலியர் பற்றாக்குறை",
                "description": "PHCs and CHCs understaffed. Patients have to travel long distances for treatment. Rs 57.85 crore sanctioned but implementation slow.",
                "affected_areas": ["Dharmapuri", "Palacode", "Pennagaram"],
                "severity": "high"
            },
            {
                "category": "water",
                "problem": "borewell_failure",
                "title_en": "Mass Borewell Failures Due to Drought",
                "title_ta": "வறட்சியால் வெகுஜன ஆழ்துளை கிணறு செயலிழப்பு",
                "description": "One of the 22 drought-hit districts. Borewells dried up in villages. Rs 150 crore SDRF released but tanker supply irregular.",
                "affected_areas": ["Harur", "Pappireddippatti", "Pennagaram"],
                "severity": "critical"
            }
        ],
        "constituencies": {
            "Dharmapuri": {"health": 4, "water": 4, "roads": 3},
            "Palacode": {"water": 4, "health": 3, "roads": 2},
            "Pennagaram": {"water": 4, "health": 3, "farming": 3},
            "Pappireddippatti": {"water": 4, "health": 2, "roads": 2},
            "Harur": {"water": 4, "roads": 3, "health": 2}
        }
    },
    
    "Erode": {
        "district_issues": [
            {
                "category": "water",
                "problem": "drought_impact",
                "title_en": "Western Catchment Drought Crisis",
                "title_ta": "மேற்கு நீர்ப்பிடிப்பு வறட்சி நெருக்கடி",
                "description": "Part of western catchment drought zone. Turmeric and banana farmers worst affected. Groundwater table dropping rapidly.",
                "affected_areas": ["Gobichettipalayam", "Bhavani", "Sathyamangalam"],
                "severity": "high"
            },
            {
                "category": "pollution",
                "problem": "textile_effluent",
                "title_en": "Textile Mill Effluent Pollution",
                "title_ta": "ஜவுளி ஆலை கழிவு மாசு",
                "description": "Textile dyeing units discharging untreated effluent into Bhavani and Noyyal rivers. Groundwater turning colored in nearby villages.",
                "affected_areas": ["Bhavani", "Gobichettipalayam", "Perundurai"],
                "severity": "high"
            }
        ],
        "constituencies": {
            "Erode East": {"pollution": 3, "roads": 3, "traffic": 2},
            "Erode West": {"pollution": 3, "water": 2, "roads": 2},
            "Modakkurichi": {"water": 3, "farming": 3, "roads": 2},
            "Dharapuram": {"water": 3, "roads": 2, "farming": 2},
            "Kangayam": {"pollution": 3, "water": 3, "farming": 2},
            "Perundurai": {"pollution": 4, "water": 3, "roads": 2},
            "Bhavani": {"pollution": 4, "water": 3, "health": 2},
            "Anthiyur": {"water": 3, "roads": 3, "farming": 2},
            "Gobichettipalayam": {"water": 4, "pollution": 3, "farming": 3},
            "Bhavanisagar": {"water": 3, "farming": 3, "roads": 2}
        }
    }
}

# Category definitions with Tamil translations
ISSUE_CATEGORIES_DETAILED = {
    "water": {
        "name_en": "Water Supply",
        "name_ta": "குடிநீர் வழங்கல்",
        "problems": [
            {"id": "water_shortage", "name_en": "Water Shortage", "name_ta": "நீர் பற்றாக்குறை"},
            {"id": "contaminated_water", "name_en": "Contaminated Water", "name_ta": "மாசுபட்ட நீர்"},
            {"id": "borewell_failure", "name_en": "Borewell Failure", "name_ta": "ஆழ்துளை கிணறு செயலிழப்பு"},
            {"id": "groundwater_contamination", "name_en": "Groundwater Contamination", "name_ta": "நிலத்தடி நீர் மாசு"},
            {"id": "irregular_supply", "name_en": "Irregular Water Supply", "name_ta": "ஒழுங்கற்ற நீர் வழங்கல்"}
        ]
    },
    "roads": {
        "name_en": "Roads & Transport",
        "name_ta": "சாலைகள் & போக்குவரத்து",
        "problems": [
            {"id": "road_damage", "name_en": "Damaged Roads/Potholes", "name_ta": "சேதமடைந்த சாலைகள்/குழிகள்"},
            {"id": "highway_accidents", "name_en": "Accident-Prone Stretches", "name_ta": "விபத்து பகுதிகள்"},
            {"id": "traffic_congestion", "name_en": "Traffic Congestion", "name_ta": "போக்குவரத்து நெரிசல்"},
            {"id": "no_bus_service", "name_en": "No Bus Service", "name_ta": "பேருந்து சேவை இல்லை"},
            {"id": "street_lights", "name_en": "No Street Lights", "name_ta": "தெரு விளக்குகள் இல்லை"}
        ]
    },
    "flooding": {
        "name_en": "Flooding & Drainage",
        "name_ta": "வெள்ளம் & வடிகால்",
        "problems": [
            {"id": "drainage_flooding", "name_en": "Poor Drainage Causing Floods", "name_ta": "மோசமான வடிகால் வெள்ளத்தை ஏற்படுத்துகிறது"},
            {"id": "encroachment_flooding", "name_en": "Encroachment on Water Bodies", "name_ta": "நீர்நிலைகளில் ஆக்கிரமிப்பு"},
            {"id": "cyclone_damage", "name_en": "Cyclone/Storm Damage", "name_ta": "புயல் சேதம்"},
            {"id": "stagnant_water", "name_en": "Stagnant Water/Mosquitoes", "name_ta": "தேங்கும் நீர்/கொசுக்கள்"}
        ]
    },
    "garbage": {
        "name_en": "Garbage & Sanitation",
        "name_ta": "குப்பை & சுகாதாரம்",
        "problems": [
            {"id": "waste_dumping", "name_en": "Illegal Waste Dumping", "name_ta": "சட்டவிரோத குப்பை கொட்டுதல்"},
            {"id": "no_collection", "name_en": "No Garbage Collection", "name_ta": "குப்பை சேகரிப்பு இல்லை"},
            {"id": "open_burning", "name_en": "Open Burning of Waste", "name_ta": "குப்பையை எரித்தல்"},
            {"id": "landfill_issues", "name_en": "Landfill Overflowing", "name_ta": "குப்பை கிடங்கு நிரம்பியது"}
        ]
    },
    "pollution": {
        "name_en": "Pollution",
        "name_ta": "மாசு",
        "problems": [
            {"id": "industrial_pollution", "name_en": "Industrial Pollution", "name_ta": "தொழிற்சாலை மாசு"},
            {"id": "river_pollution", "name_en": "River Pollution", "name_ta": "ஆற்று மாசு"},
            {"id": "air_pollution", "name_en": "Air Pollution", "name_ta": "காற்று மாசு"},
            {"id": "noise_pollution", "name_en": "Noise Pollution", "name_ta": "ஒலி மாசு"},
            {"id": "mining_pollution", "name_en": "Mining/Quarry Pollution", "name_ta": "சுரங்க மாசு"}
        ]
    },
    "electricity": {
        "name_en": "Electricity",
        "name_ta": "மின்சாரம்",
        "problems": [
            {"id": "power_cuts", "name_en": "Frequent Power Cuts", "name_ta": "அடிக்கடி மின்தடை"},
            {"id": "transformer_failure", "name_en": "Transformer Failure", "name_ta": "மின்மாற்றி செயலிழப்பு"},
            {"id": "voltage_fluctuation", "name_en": "Voltage Fluctuation", "name_ta": "மின்னழுத்த ஏற்றத்தாழ்வு"},
            {"id": "no_electricity", "name_en": "No Electricity Connection", "name_ta": "மின் இணைப்பு இல்லை"}
        ]
    },
    "health": {
        "name_en": "Healthcare",
        "name_ta": "சுகாதாரம்",
        "problems": [
            {"id": "hospital_shortage", "name_en": "No Hospital/PHC Nearby", "name_ta": "அருகில் மருத்துவமனை இல்லை"},
            {"id": "doctor_shortage", "name_en": "Doctor/Staff Shortage", "name_ta": "மருத்துவர் பற்றாக்குறை"},
            {"id": "medicine_shortage", "name_en": "Medicine Shortage", "name_ta": "மருந்து பற்றாக்குறை"},
            {"id": "pollution_health_impact", "name_en": "Pollution-Related Health Issues", "name_ta": "மாசு தொடர்பான உடல்நல பிரச்சனைகள்"},
            {"id": "ambulance_delay", "name_en": "Ambulance Service Delay", "name_ta": "ஆம்புலன்ஸ் தாமதம்"}
        ]
    },
    "farming": {
        "name_en": "Agriculture",
        "name_ta": "விவசாயம்",
        "problems": [
            {"id": "irrigation_crisis", "name_en": "Irrigation Water Shortage", "name_ta": "பாசன நீர் பற்றாக்குறை"},
            {"id": "crop_damage", "name_en": "Crop Damage", "name_ta": "பயிர் சேதம்"},
            {"id": "fertilizer_shortage", "name_en": "Fertilizer/Seed Shortage", "name_ta": "உரம் பற்றாக்குறை"},
            {"id": "market_price", "name_en": "Low Market Price", "name_ta": "குறைந்த சந்தை விலை"},
            {"id": "cauvery_water_dispute", "name_en": "Cauvery Water Issues", "name_ta": "காவிரி நீர் பிரச்சனைகள்"}
        ]
    },
    "sewage": {
        "name_en": "Sewage & Drainage",
        "name_ta": "கழிவு நீர்",
        "problems": [
            {"id": "sewage_overflow", "name_en": "Sewage Overflow", "name_ta": "கழிவு நீர் வழிதல்"},
            {"id": "blocked_drains", "name_en": "Blocked Drains", "name_ta": "அடைபட்ட வடிகால்கள்"},
            {"id": "no_sewage_system", "name_en": "No Sewage System", "name_ta": "கழிவு நீர் அமைப்பு இல்லை"},
            {"id": "septic_tank_issues", "name_en": "Septic Tank Issues", "name_ta": "செப்டிக் டேங்க் பிரச்சனைகள்"}
        ]
    }
}

def get_all_real_issues():
    """Get all real issues from all districts"""
    all_issues = []
    for district, data in REAL_ISSUES_DATA.items():
        for issue in data.get("district_issues", []):
            issue["district"] = district
            all_issues.append(issue)
    return all_issues

def get_issues_by_district(district):
    """Get issues for a specific district"""
    return REAL_ISSUES_DATA.get(district, {}).get("district_issues", [])

def get_constituency_stats(district):
    """Get constituency-wise issue stats for a district"""
    return REAL_ISSUES_DATA.get(district, {}).get("constituencies", {})
