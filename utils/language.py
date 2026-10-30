"""Multilingual localization dictionary and helpers for AgriSaathi AI.

Supports English (en), Marathi (mr), and Hindi (hi).
"""

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App & Navigation
    "app_title": {
        "en": "AgriSaathi AI",
        "mr": "कृषी साथी AI",
        "hi": "कृषि साथी AI",
    },
    "tagline": {
        "en": "Your Smart Farming Companion",
        "mr": "शेतकऱ्यांचा स्मार्ट शेती साथी",
        "hi": "किसानों का स्मार्ट खेती साथी",
    },
    "dashboard": {
        "en": "Dashboard",
        "mr": "डॅशबोर्ड",
        "hi": "डैशबोर्ड",
    },
    "my_crops": {
        "en": "My Crops",
        "mr": "माझी पिके",
        "hi": "मेरी फसलें",
    },
    "crop_library": {
        "en": "Crop Knowledge Library",
        "mr": "पीक माहिती ग्रंथालय",
        "hi": "फसल ज्ञान पुस्तकालय",
    },
    "farm_activities": {
        "en": "Farm Diary",
        "mr": "शेती रोजनिशी",
        "hi": "खेत डायरी",
    },
    "farm_expenses": {
        "en": "Farm Expenses",
        "mr": "शेती खर्च",
        "hi": "कृषि खर्च",
    },
    "harvest_records": {
        "en": "Harvest Records",
        "mr": "उत्पादन नोंदी",
        "hi": "उपज रिकॉर्ड",
    },
    "ai_assistant": {
        "en": "AI Farming Assistant",
        "mr": "AI शेती सल्लागार",
        "hi": "AI कृषि सहायक",
    },
    "crop_doctor": {
        "en": "Crop Doctor / Disease Check",
        "mr": "पीक आरोग्य / रोग तपासणी",
        "hi": "फसल स्वास्थ्य / रोग जांच",
    },
    "weather": {
        "en": "Weather Advisory",
        "mr": "हवामान अंदाज",
        "hi": "मौसम सलाह",
    },
    "market_prices": {
        "en": "Mandi Market Prices",
        "mr": "बाजार भाव (मंडी)",
        "hi": "मंडी भाव",
    },
    "government_schemes": {
        "en": "Government Schemes",
        "mr": "शासकीय योजना",
        "hi": "सरकारी योजनाएं",
    },
    "profile": {
        "en": "Farmer Profile",
        "mr": "शेतकरी प्रोफाइल",
        "hi": "किसान प्रोफाइल",
    },
    "settings": {
        "en": "Settings",
        "mr": "सेटिंग्ज",
        "hi": "सेटिंग्स",
    },
    "logout": {
        "en": "Log Out",
        "mr": "लॉग आउट",
        "hi": "लॉग आउट",
    },
    "login": {
        "en": "Log In",
        "mr": "लॉग इन",
        "hi": "लॉग इन",
    },
    "register": {
        "en": "Farmer Registration",
        "mr": "शेतकरी नोंदणी",
        "hi": "किसान पंजीकरण",
    },
    "welcome": {
        "en": "Welcome",
        "mr": "स्वागत आहे",
        "hi": "स्वागत है",
    },
    "select_language": {
        "en": "Select Language",
        "mr": "भाषा निवडा",
        "hi": "भाषा चुनें",
    },

    # Common Actions & Buttons
    "save": {
        "en": "Save",
        "mr": "जतन करा",
        "hi": "सहेजें",
    },
    "cancel": {
        "en": "Cancel",
        "mr": "रद्द करा",
        "hi": "रद्द करें",
    },
    "delete": {
        "en": "Delete",
        "mr": "हटवा",
        "hi": "हटाएं",
    },
    "edit": {
        "en": "Edit",
        "mr": "संपादित करा",
        "hi": "संपादित करें",
    },
    "confirm_delete": {
        "en": "Confirm Delete",
        "mr": "हटवण्याची खात्री करा",
        "hi": "हटाने की पुष्टि करें",
    },
    "add_crop": {
        "en": "Add New Crop",
        "mr": "नवीन पीक जोडा",
        "hi": "नई फसल जोड़ें",
    },
    "add_activity": {
        "en": "Record Activity",
        "mr": "कामाची नोंद करा",
        "hi": "गतिविधि दर्ज करें",
    },
    "add_expense": {
        "en": "Record Expense",
        "mr": "खर्चाची नोंद करा",
        "hi": "खर्च दर्ज करें",
    },
    "add_harvest": {
        "en": "Record Harvest",
        "mr": "उत्पादनाची नोंद करा",
        "hi": "उपज दर्ज करें",
    },
    "send_message": {
        "en": "Send Message",
        "mr": "संदेश पाठवा",
        "hi": "संदेश भेजें",
    },
    "new_conversation": {
        "en": "New Conversation",
        "mr": "नवीन चर्चा",
        "hi": "नई बातचीत",
    },
    "search": {
        "en": "Search",
        "mr": "शोधा",
        "hi": "खोजें",
    },
    "view_details": {
        "en": "View Details",
        "mr": "तपशील पहा",
        "hi": "विवरण देखें",
    },
    "ask_ai_crop": {
        "en": "Ask AI about this crop",
        "mr": "या पिकाबद्दल AI ला विचारा",
        "hi": "इस फसल के बारे में AI से पूछें",
    },

    # Form Fields & Labels
    "full_name": {
        "en": "Full Name",
        "mr": "पूर्ण नाव",
        "hi": "पूरा नाम",
    },
    "email": {
        "en": "Email Address",
        "mr": "ईमेल पत्ता",
        "hi": "ईमेल पता",
    },
    "phone": {
        "en": "Mobile Number",
        "mr": "मोबाईल नंबर",
        "hi": "मोबाइल नंबर",
    },
    "password": {
        "en": "Password",
        "mr": "पासवर्ड",
        "hi": "पासवर्ड",
    },
    "confirm_password": {
        "en": "Confirm Password",
        "mr": "पासवर्ड पुन्हा टाका",
        "hi": "पासवर्ड की पुष्टि करें",
    },
    "state": {
        "en": "State",
        "mr": "राज्य",
        "hi": "राज्य",
    },
    "district": {
        "en": "District",
        "mr": "जिल्हा",
        "hi": "जिला",
    },
    "village": {
        "en": "Village / Locality",
        "mr": "गाव / परिसर",
        "hi": "गाँव / इलाका",
    },
    "farm_size": {
        "en": "Farm Size",
        "mr": "शेताचा आकार",
        "hi": "खेत का आकार",
    },
    "area_unit": {
        "en": "Area Unit",
        "mr": "क्षेत्रफळ एकक",
        "hi": "क्षेत्रफल इकाई",
    },
    "soil_type": {
        "en": "Soil Type",
        "mr": "मातीचा प्रकार",
        "hi": "मिट्टी का प्रकार",
    },
    "irrigation_method": {
        "en": "Irrigation Method",
        "mr": "सिंचन पद्धत",
        "hi": "सिंचाई विधि",
    },
    "crop_name": {
        "en": "Crop Name",
        "mr": "पिकाचे नाव",
        "hi": "फसल का नाम",
    },
    "variety": {
        "en": "Variety / Hybrid",
        "mr": "वाण / जात",
        "hi": "किस्म / संकर",
    },
    "plot_name": {
        "en": "Field / Plot Name",
        "mr": "शेत / तुकड्याचे नाव",
        "hi": "खेत / प्लॉट का नाम",
    },
    "area_planted": {
        "en": "Area Planted",
        "mr": "लागवड क्षेत्र",
        "hi": "बोया गया क्षेत्रफल",
    },
    "sowing_date": {
        "en": "Sowing Date",
        "mr": "पेरणी / लागवड तारीख",
        "hi": "बुआई / रोपाई तिथि",
    },
    "expected_harvest_date": {
        "en": "Expected Harvest Date",
        "mr": "अपेक्षित काढणी तारीख",
        "hi": "संभावित कटाई तिथि",
    },
    "actual_harvest_date": {
        "en": "Actual Harvest Date",
        "mr": "प्रत्यक्ष काढणी तारीख",
        "hi": "वास्तविक कटाई तिथि",
    },
    "growth_stage": {
        "en": "Current Growth Stage",
        "mr": "सध्याची वाढ अवस्था",
        "hi": "वर्तमान विकास चरण",
    },
    "status": {
        "en": "Status",
        "mr": "स्थिती",
        "hi": "स्थिति",
    },
    "active": {
        "en": "Active",
        "mr": "सुरू",
        "hi": "सक्रिय",
    },
    "harvested": {
        "en": "Harvested",
        "mr": "काढणी झालेली",
        "hi": "कटाई पूर्ण",
    },
    "failed": {
        "en": "Failed / Lost",
        "mr": "नुकसानग्रस्त",
        "hi": "नुकसानग्रस्त",
    },
    "notes": {
        "en": "Notes / Observations",
        "mr": "नोंदी / निरीक्षणे",
        "hi": "नोट्स / अवलोकन",
    },
    "amount": {
        "en": "Amount (₹)",
        "mr": "रक्कम (₹)",
        "hi": "राशि (₹)",
    },
    "category": {
        "en": "Category",
        "mr": "प्रवर्ग",
        "hi": "श्रेणी",
    },
    "date": {
        "en": "Date",
        "mr": "तारीख",
        "hi": "तारीख",
    },
    "quantity": {
        "en": "Quantity",
        "mr": "प्रमाण",
        "hi": "मात्रा",
    },
    "unit": {
        "en": "Unit",
        "mr": "एकक",
        "hi": "इकाई",
    },
    "selling_price": {
        "en": "Selling Price (₹)",
        "mr": "विक्री किंमत (₹)",
        "hi": "बिक्री मूल्य (₹)",
    },

    # Dashboard Cards & Metrics
    "total_active_crops": {
        "en": "Active Crops",
        "mr": "सध्याची पिके",
        "hi": "सक्रिय फसलें",
    },
    "total_recorded_expenses": {
        "en": "Total Expenses",
        "mr": "एकूण खर्च",
        "hi": "कुल खर्च",
    },
    "recent_activities": {
        "en": "Recent Farm Activities",
        "mr": "अलीकडील शेती कामे",
        "hi": "हाल की खेत गतिविधियां",
    },
    "upcoming_harvests": {
        "en": "Upcoming Harvests",
        "mr": "येणाऱ्या काढण्या",
        "hi": "आगामी कटाई",
    },
    "no_crops_yet": {
        "en": "No crops registered yet. Click 'Add New Crop' to begin tracking.",
        "mr": "अद्याप कोणतीही पिके नोंदवलेली नाहीत. ट्रॅकिंग सुरू करण्यासाठी 'नवीन पीक जोडा' वर क्लिक करा.",
        "hi": "अभी कोई फसल दर्ज नहीं की गई है। शुरुआत करने के लिए 'नई फसल जोड़ें' पर क्लिक करें।",
    },
    "no_activities_yet": {
        "en": "No farm activities recorded yet.",
        "mr": "अद्याप कोणतीही शेती कामे नोंदवलेली नाहीत.",
        "hi": "अभी कोई खेत गतिविधि दर्ज नहीं है।",
    },
    "no_expenses_yet": {
        "en": "No expenses recorded yet.",
        "mr": "अद्याप कोणताही खर्च नोंदवलेला नाही.",
        "hi": "अभी कोई खर्च दर्ज नहीं किया गया है।",
    },
    "quick_actions": {
        "en": "Quick Actions",
        "mr": "जलद कृती",
        "hi": "त्वरित क्रियाएं",
    },

    # AI Chatbot
    "ask_question_placeholder": {
        "en": "Ask any farming question (e.g. soil prep, pest symptoms, fertilizer, weather)...",
        "mr": "शेतीविषयक कोणताही प्रश्न विचारा (उदा. खत व्यवस्थापन, कीड नियंत्रण, मशागत)...",
        "hi": "कृषि से जुड़ा कोई भी प्रश्न पूछें (उदा. खाद, कीट नियंत्रण, मिट्टी की तैयारी)...",
    },
    "sample_questions_title": {
        "en": "Frequently Asked Questions",
        "mr": "नेहमी विचारले जाणारे प्रश्न",
        "hi": "अक्सर पूछे जाने वाले प्रश्न",
    },
    "sample_q1": {
        "en": "How can I prevent bollworm infestation in cotton organically?",
        "mr": "कापूस पिकातील बोंडअळीचे सेंद्रिय पद्धतीने नियंत्रण कसे करावे?",
        "hi": "कपास में गुलाबी सुंडी की रोकथाम जैविक तरीके से कैसे करें?",
    },
    "sample_q2": {
        "en": "What are the key fertilizer timings for soybean crops?",
        "mr": "सोयाबीन पिकासाठी खत व्यवस्थापनाच्या महत्त्वाच्या वेळा कोणत्या?",
        "hi": "सोयाबीन की फसल के लिए उर्वरक देने का सही समय क्या है?",
    },
    "sample_q3": {
        "en": "What are the eligibility conditions for PM-Kisan Samman Nidhi?",
        "mr": "पीएम-किसान सन्मान निधी योजनेसाठी पात्रता काय आहे?",
        "hi": "पीएम-किसान सम्मान निधि योजना के लिए क्या पात्रता है?",
    },
    "ai_context_crop": {
        "en": "Discussing crop:",
        "mr": "निवडलेले पीक:",
        "hi": "चयनित फसल:",
    },
    "no_crop_context": {
        "en": "General farming inquiry (No specific crop)",
        "mr": "सामान्य शेती विचारणा (विशिष्ट पीक नाही)",
        "hi": "सामान्य कृषि पूछताछ (कोई विशिष्ट फसल नहीं)",
    },
    "ollama_offline_title": {
        "en": "Local AI Assistant Offline",
        "mr": "स्थानिक AI सल्लागार सध्या उपलब्ध नाही",
        "hi": "स्थानीय AI सहायक वर्तमान में उपलब्ध नहीं है",
    },
    "ollama_offline_msg": {
        "en": "Ollama local inference service is currently unreachable. Crop Library, Farm Diary, Expenses, and Schemes remain fully functional.",
        "mr": "स्थानिक ओलामा (Ollama) सेवा सध्या चालू नाही. पीक ग्रंथालय, डायरी, खर्च आणि योजना नेहमीप्रमाणे कार्यक्षम आहेत.",
        "hi": "स्थानीय ओलामा (Ollama) सेवा वर्तमान में उपलब्ध नहीं है। फसल पुस्तकालय, डायरी, खर्च और योजनाएं सामान्य रूप से चालू हैं।",
    },

    # Financials & Summaries
    "total_harvest_revenue": {
        "en": "Recorded Harvest Sales",
        "mr": "नोंदवलेली पीक विक्री",
        "hi": "दर्ज की गई फसल बिक्री",
    },
    "net_crop_balance": {
        "en": "Recorded Net Balance",
        "mr": "अंदाजे निव्वळ शिल्लक",
        "hi": "अनुमानित शुद्ध शेष",
    },
    "financial_disclaimer": {
        "en": "Note: Net balance reflects only manually recorded sales minus recorded expenses. It does not constitute an audited accounting report.",
        "mr": "टीप: निव्वळ शिल्लक केवळ स्वतः नोंदवलेली विक्री आणि खर्च यावर आधारित आहे.",
        "hi": "नोट: शुद्ध शेष केवल आपके द्वारा दर्ज बिक्री और खर्चों का अंतर है।",
    },

    # Safety Disclaimers
    "safety_disclaimer_title": {
        "en": "Important Agricultural Advisory Disclaimer",
        "mr": "महत्त्वाची कृषी सल्लागार सूचना",
        "hi": "महत्वपूर्ण कृषि सलाह अस्वीकरण",
    },
    "safety_disclaimer_text": {
        "en": "AgriSaathi AI provides educational and advisory assistance. Recommendations should be verified with local agricultural extension officers or Krishi Vigyan Kendra (KVK) for exact regional formulations and conditions.",
        "mr": "कृषी साथी AI मार्गदर्शक माहिती पुरवते. अचूक खत आणि औषध मात्रेसाठी स्थानिक कृषी विज्ञान केंद्र (KVK) किंवा कृषी अधिकाऱ्यांशी संपर्क साधावा.",
        "hi": "कृषि साथी AI मार्गदर्शन प्रदान करता है। सटीक दवा व खाद की मात्रा के लिए स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से पुष्टि अवश्य करें।",
    },

    # 5-Section Mobile Navigation
    "nav_home": {
        "en": "Home",
        "mr": "मुख्य",
        "hi": "मुख्य",
    },
    "nav_ask_ai": {
        "en": "Ask AI",
        "mr": "AI सल्ला",
        "hi": "AI सलाह",
    },
    "nav_my_farm": {
        "en": "My Farm",
        "mr": "माझी शेती",
        "hi": "मेरा खेत",
    },
    "nav_market_schemes": {
        "en": "Market & Schemes",
        "mr": "बाजार व योजना",
        "hi": "बाजार और योजनाएं",
    },
    "nav_profile": {
        "en": "My Profile",
        "mr": "माझे खाते",
        "hi": "मेरी प्रोफाइल",
    },

    # Sub-Navigation Tabs
    "tab_crops": {
        "en": "My Crops",
        "mr": "माझी पिके",
        "hi": "मेरी फसलें",
    },
    "tab_diary": {
        "en": "Farm Diary",
        "mr": "शेती दैनंदिनी",
        "hi": "खेत डायरी",
    },
    "tab_expenses": {
        "en": "Expenses",
        "mr": "खर्च नोंद",
        "hi": "खर्च",
    },
    "tab_harvest": {
        "en": "Harvest & Profit",
        "mr": "उत्पादन व नफा",
        "hi": "उपज व लाभ",
    },
    "tab_mandi": {
        "en": "Mandi Rates",
        "mr": "बाजारभाव",
        "hi": "मंडी भाव",
    },
    "tab_weather": {
        "en": "Weather",
        "mr": "हवामान",
        "hi": "मौसम",
    },
    "tab_schemes": {
        "en": "Schemes",
        "mr": "शासकीय योजना",
        "hi": "सरकारी योजनाएं",
    },
    "tab_knowledge": {
        "en": "Crop Library",
        "mr": "कृषी ग्रंथालय",
        "hi": "फसल पुस्तकालय",
    },
    "tab_crop_health": {
        "en": "Leaf Check",
        "mr": "रोग तपासणी",
        "hi": "रोग जांच",
    },

    # Action Tiles
    "tile_ask_ai_title": {
        "en": "Ask AI Assistant",
        "mr": "AI सल्लागार विचारा",
        "hi": "AI सहायक से पूछें",
    },
    "tile_ask_ai_desc": {
        "en": "Instant advice on pests, weather & soil",
        "mr": "कीड, खते व हवामानावर त्वरित उपाय",
        "hi": "कीट, खाद व मौसम पर तुरंत सलाह",
    },
    "tile_scan_leaf_title": {
        "en": "Scan Leaf / Disease",
        "mr": "पानावरील रोग तपासा",
        "hi": "पत्ती रोग की जांच करें",
    },
    "tile_scan_leaf_desc": {
        "en": "Photo check & university guidance",
        "mr": "फोटो व लक्षणानुसार शास्त्रीय सल्ला",
        "hi": "फोटो व लक्षणों से सटीक मार्गदर्शन",
    },
    "tile_mandi_title": {
        "en": "APMC Mandi Rates",
        "mr": "आजचे बाजारभाव",
        "hi": "आज के मंडी भाव",
    },
    "tile_mandi_desc": {
        "en": "Benchmark rates across mandis",
        "mr": "बाजार समित्यांमधील ताजे दर",
        "hi": "विभिन्न मंडियों के ताजा भाव",
    },

    # Spray Weather Badges
    "spray_ok_badge": {
        "en": "🟢 Weather OK for Spraying",
        "mr": "🟢 फवारणीस अनुकूल हवामान",
        "hi": "🟢 छिड़काव के लिए अनुकूल मौसम",
    },
    "spray_warn_badge": {
        "en": "🔴 Postpone Spraying (Wind/Rain Risk)",
        "mr": "🔴 फवारणी पुढे ढकला (पाऊस/वाऱ्याचा धोका)",
        "hi": "🔴 छिड़काव स्थगित करें (हवा/बारिश का जोखिम)",
    },
    "spray_ok_advice": {
        "en": "Calm wind and clear skies. Favorable for foliar applications.",
        "mr": "शांत हवामान व स्वच्छ आकाश. खते व सेंद्रिय फवारणीसाठी योग्य वेळ.",
        "hi": "शांत मौसम और साफ आसमान। छिड़काव के लिए अनुकूल समय।",
    },
    "spray_warn_advice": {
        "en": "High wind speed or rain probability detected. Postpone chemical sprays to prevent wash-off or drift.",
        "mr": "जास्त वारा किंवा पावसाची शक्यता आहे. औषध वाहून जाणे टाळण्यासाठी फवारणी पुढे ढकला.",
        "hi": "तेज हवा या बारिश की संभावना है। दवा व्यर्थ होने से बचाने के लिए छिड़काव टालें।",
    },

    # Empty States & Onboarding
    "empty_crops_title": {
        "en": "No crops registered yet",
        "mr": "अद्याप कोणतेही पीक नोंदवलेले नाही",
        "hi": "अभी कोई फसल दर्ज नहीं की गई है",
    },
    "empty_crops_desc": {
        "en": "Register your active crops to get tailored AI advice, growth-stage care, and expense tracking.",
        "mr": "तुमच्या शेतातील पिकांची नोंद करा, जेणेकरून अचूक AI सल्ला व खर्चाचा हिशोब ठेवता येईल.",
        "hi": "अपनी फसलों को दर्ज करें ताकि सटीक AI सलाह और खर्चों का हिसाब रखा जा सके।",
    },
    "empty_crops_btn": {
        "en": "🌱 Register First Crop",
        "mr": "🌱 पहिले पीक नोंदवा",
        "hi": "🌱 पहली फसल दर्ज करें",
    },
    "empty_diary_title": {
        "en": "Farm diary is empty",
        "mr": "दैनंदिनीत अद्याप कोणतीही नोंद नाही",
        "hi": "खेत डायरी में कोई प्रविष्टि नहीं है",
    },
    "empty_diary_desc": {
        "en": "Record weeding, irrigation, fertilizing, and spraying activities to maintain an accurate farm log.",
        "mr": "खुरपणी, पाणी, खते आणि फवारणीच्या कामांची तारीखवार नोंद ठेवा.",
        "hi": "निराई, सिंचाई, खाद और छिड़काव के कार्यों का समय पर रिकॉर्ड रखें।",
    },
    "empty_diary_btn": {
        "en": "📝 Record First Activity",
        "mr": "📝 पहिली नोंद करा",
        "hi": "📝 पहली गतिविधि दर्ज करें",
    },
    "empty_expenses_title": {
        "en": "No expenses recorded",
        "mr": "खर्चाची कोणतीही नोंद नाही",
        "hi": "कोई खर्च दर्ज नहीं है",
    },
    "empty_expenses_desc": {
        "en": "Track seeds, fertilizer, fuel, and labor costs to know your exact cost of cultivation.",
        "mr": "बियाणे, खते, डिझेल आणि मजुरीचा हिशोब ठेवा जेणेकरून खरा उत्पादन खर्च समजेल.",
        "hi": "बीज, खाद, डीजल और मजदूरी का हिसाब रखें ताकि उत्पादन लागत का पता चले।",
    },
    "empty_expenses_btn": {
        "en": "💵 Add First Expense",
        "mr": "💵 पहिला खर्च जोडा",
        "hi": "💵 पहला खर्च जोड़ें",
    },
    "empty_harvest_title": {
        "en": "No harvest sales recorded",
        "mr": "उत्पादनाची कोणतीही नोंद नाही",
        "hi": "उपज बिक्री का कोई रिकॉर्ड नहीं है",
    },
    "empty_harvest_desc": {
        "en": "Log yields and market sales rates to automatically calculate your real net farm profit.",
        "mr": "शेतमाल उत्पादन व विक्री दर नोंदवून खरा निव्वळ नफा आपोआप जाणून घ्या.",
        "hi": "उत्पादन और बिक्री मूल्य दर्ज करें ताकि असली शुद्ध लाभ का हिसाब मिल सके।",
    },
    "empty_harvest_btn": {
        "en": "💰 Record Harvest Sales",
        "mr": "💰 उत्पादन नोंद जोडा",
        "hi": "💰 उपज बिक्री जोड़ें",
    },
    "onboarding_welcome": {
        "en": "Welcome to AgriSaathi AI!",
        "mr": "कृषी साथी AI मध्ये आपले स्वागत आहे!",
        "hi": "कृषि साथी AI में आपका स्वागत है!",
    },
    "onboarding_steps": {
        "en": "Get started in 3 simple steps: 1. Add your crops, 2. Check the daily spray advisory, 3. Ask AI for expert farming advice!",
        "mr": "सुरू करण्यासाठी ३ सोप्या पायऱ्या: १. पीक नोंदवा, २. रोजचा फवारणी सल्ला तपासा, ३. AI ला कोणताही शेती प्रश्न विचारा!",
        "hi": "3 आसान चरणों में शुरुआत करें: 1. फसल जोड़ें, 2. दैनिक छिड़काव सलाह देखें, 3. AI से कोई भी सवाल पूछें!",
    },
    "quick_add_expense": {
        "en": "Add Expense",
        "mr": "खर्च जोडा",
        "hi": "खर्च जोड़ें",
    },
    "quick_add_diary": {
        "en": "Record Activity",
        "mr": "काम नोंदवा",
        "hi": "काम दर्ज करें",
    },
    "app_tagline": {
        "en": "Trusted Digital Farming Companion",
        "mr": "शेतकऱ्यांचा विश्वासू डिजिटल साथीदार",
        "hi": "किसानों का सच्चा डिजिटल साथी",
    },
    "quick_links": {
        "en": "Quick Links",
        "mr": "जलद दुवे",
        "hi": "त्वरित लिंक",
    },
    "agri_advisory": {
        "en": "Agricultural Advisory",
        "mr": "कृषी सल्ला",
        "hi": "कृषि सलाह",
    },
    "weather_wind": {
        "en": "Wind",
        "mr": "वारा",
        "hi": "हवा",
    },
    "weather_humidity": {
        "en": "Humidity",
        "mr": "आर्द्रता",
        "hi": "नमी",
    },
    "weather_rain": {
        "en": "Rain",
        "mr": "पाऊस",
        "hi": "बारिश",
    },
    "btn_ask_ai_tile": {
        "en": "Ask AI 💬",
        "mr": "AI ला विचारा 💬",
        "hi": "AI से पूछें 💬",
    },
    "btn_scan_tile": {
        "en": "Scan Leaf 📷",
        "mr": "तपासा 📷",
        "hi": "पत्ती जांचें 📷",
    },
    "btn_mandi_tile": {
        "en": "View Rates 📊",
        "mr": "दर पहा 📊",
        "hi": "मंडी भाव देखें 📊",
    },
    "finances_title": {
        "en": "Farm Finances",
        "mr": "आर्थिक स्थिती",
        "hi": "आर्थिक स्थिति",
    },
    "sales_revenue": {
        "en": "Sales Revenue",
        "mr": "विक्री उत्पन्न",
        "hi": "बिक्री आय",
    },
    "net_balance": {
        "en": "Net Profit / Loss",
        "mr": "निव्वळ नफा / तोटा",
        "hi": "शुद्ध लाभ / हानि",
    },
    "profit_label": {
        "en": "Profit",
        "mr": "नफा",
        "hi": "लाभ",
    },
    "loss_label": {
        "en": "Loss",
        "mr": "तोटा",
        "hi": "हानि",
    },
    "view_finances_btn": {
        "en": "View Accounts 📊",
        "mr": "हिशोब पहा 📊",
        "hi": "हिसाब देखें 📊",
    },
    "recent_entries": {
        "en": "Recent Entries",
        "mr": "अलिकडील नोंदी",
        "hi": "हाल की प्रविष्टियां",
    },
    "crop_area_lbl": {
        "en": "Area",
        "mr": "क्षेत्र",
        "hi": "क्षेत्रफल",
    },
    "growth_stage_lbl": {
        "en": "Growth Stage",
        "mr": "अवस्था",
        "hi": "अवस्था",
    },
    "sowing_date_lbl": {
        "en": "Sowing Date",
        "mr": "पेरणी",
        "hi": "बुवाई",
    },
    "btn_register_new_crop": {
        "en": "Register New Crop",
        "mr": "नवीन पीक नोंदवा",
        "hi": "नई फसल जोड़ें",
    },
    "btn_save_crop": {
        "en": "Save Crop",
        "mr": "पीक जतन करा",
        "hi": "फसल सहेजें",
    },
    "active_crops_tab": {
        "en": "Active Crops",
        "mr": "चालू पिके",
        "hi": "सक्रिय फसलें",
    },
    "harvested_crops_tab": {
        "en": "Harvested Crops",
        "mr": "काढणी झालेली पिके",
        "hi": "काटी गई फसलें",
    },

    # Multi-Market APMC Comparison Page Strings
    "mandi_title": {
        "en": "APMC Mandi Market Price Comparison",
        "mr": "कृषी उत्पन्न बाजार समिती (APMC) बाजारभाव तुलना",
        "hi": "एपीएमसी मंडी भाव तुलना",
    },
    "mandi_subtitle": {
        "en": "Compare live rates across mandis, calculate transport & net profit",
        "mr": "विविध बाजार समित्यांमधील दरांची तुलना करा, वाहतूक खर्च व निव्वळ नफा जाणून घ्या",
        "hi": "विभिन्न मंडियों के भाव की तुलना करें, परिवहन लागत और शुद्ध लाभ जानें",
    },
    "mandi_best_price_today": {
        "en": "🏆 Best Price Today",
        "mr": "🏆 आजचा सर्वाधिक भाव",
        "hi": "🏆 आज का सर्वाधिक भाव",
    },
    "mandi_select_crop": {
        "en": "Select Commodity / Crop",
        "mr": "शेतमाल / पीक निवडा",
        "hi": "फसल / जींस चुनें",
    },
    "mandi_state": {
        "en": "State",
        "mr": "राज्य",
        "hi": "राज्य",
    },
    "mandi_district": {
        "en": "District (Optional)",
        "mr": "जिल्हा (ऐच्छिक)",
        "hi": "जिला (वैकल्पिक)",
    },
    "mandi_variety": {
        "en": "Variety (Optional)",
        "mr": "वाण (ऐच्छिक)",
        "hi": "किस्म (वैकल्पिक)",
    },
    "mandi_all_commodities": {
        "en": "All Commodities",
        "mr": "सर्व पिके",
        "hi": "सभी फसलें",
    },
    "mandi_all_districts": {
        "en": "All Districts",
        "mr": "सर्व जिल्हे",
        "hi": "सभी जिले",
    },
    "mandi_all_varieties": {
        "en": "All Varieties",
        "mr": "सर्व वाण",
        "hi": "सभी किस्में",
    },
    "mandi_transport_rate": {
        "en": "Transport Cost (₹ / Quintal / 100 km)",
        "mr": "वाहतूक खर्च (₹ / क्विंटल / १०० किमी)",
        "hi": "परिवहन खर्च (₹ / क्विंटल / १०० किमी)",
    },
    "mandi_quantity": {
        "en": "Quantity to Sell (Quintals)",
        "mr": "विक्रीयोग्य प्रमाण (क्विंटल)",
        "hi": "बिक्री योग्य मात्रा (क्विंटल)",
    },
    "mandi_sort_by": {
        "en": "Sort Markets By",
        "mr": "बाजार क्रमवारी",
        "hi": "मंडियों की क्रमबद्धता",
    },
    "mandi_sort_modal_price": {
        "en": "Highest Modal Price",
        "mr": "सर्वाधिक मॉडेल भाव",
        "hi": "उच्चतम मॉडल भाव",
    },
    "mandi_sort_net_price": {
        "en": "Highest Net Price (After Transport)",
        "mr": "सर्वाधिक निव्वळ भाव (वाहतूक वजा)",
        "hi": "उच्चतम शुद्ध भाव (परिवहन पश्चात)",
    },
    "mandi_sort_distance": {
        "en": "Closest Distance",
        "mr": "जवळचे बाजार",
        "hi": "निकटतम मंडी",
    },
    "mandi_sort_latest_date": {
        "en": "Latest Arrival Date",
        "mr": "नवीनतम तारीख",
        "hi": "नवीनतम तारीख",
    },
    "mandi_market_name": {
        "en": "Market APMC",
        "mr": "बाजार समिती",
        "hi": "मंडी",
    },
    "mandi_modal_price": {
        "en": "Modal Price",
        "mr": "मॉडेल भाव",
        "hi": "मॉडल भाव",
    },
    "mandi_min_max": {
        "en": "Min - Max Price",
        "mr": "किमान - कमाल भाव",
        "hi": "न्यूनतम - अधिकतम भाव",
    },
    "mandi_distance": {
        "en": "Distance",
        "mr": "अंतर",
        "hi": "दूरी",
    },
    "mandi_transport_deduction": {
        "en": "Est. Transport Deduction",
        "mr": "अंदाजे वाहतूक वजावट",
        "hi": "अनुमानित परिवहन कटौती",
    },
    "mandi_net_price": {
        "en": "Est. Net Price",
        "mr": "अंदाजे निव्वळ भाव",
        "hi": "अनुमानित शुद्ध भाव",
    },
    "mandi_gross_revenue": {
        "en": "Est. Gross Revenue",
        "mr": "अंदाजे एकूण उत्पन्न",
        "hi": "अनुमानित कुल आय",
    },
    "mandi_net_revenue": {
        "en": "Est. Net In-Hand Revenue",
        "mr": "हातात येणारे निव्वळ उत्पन्न",
        "hi": "हाथ में आने वाली शुद्ध आय",
    },
    "mandi_freshness_today": {
        "en": "🟢 Today",
        "mr": "🟢 आजचे",
        "hi": "🟢 आज",
    },
    "mandi_freshness_1_2_days": {
        "en": "🟡 1-2 Days Old",
        "mr": "🟡 १-२ दिवस जुने",
        "hi": "🟡 १-२ दिन पुराना",
    },
    "mandi_freshness_older": {
        "en": "🔴 Older Data",
        "mr": "🔴 जुने दर",
        "hi": "🔴 पुराना भाव",
    },
    "mandi_local_compare_title": {
        "en": "Compare with My Local District Market",
        "mr": "माझ्या स्थानिक जिल्हा बाजाराशी तुलना",
        "hi": "मेरे स्थानीय जिला बाजार से तुलना",
    },
    "mandi_local_compare_desc": {
        "en": "Difference between top market and your local APMC",
        "mr": "सर्वोत्तम बाजार आणि स्थानिक बाजार यातील फरक",
        "hi": "सर्वश्रेष्ठ मंडी और स्थानीय मंडी में अंतर",
    },
    "mandi_better_by": {
        "en": "Higher by",
        "mr": "जास्त",
        "hi": "ज्यादा",
    },
    "mandi_lower_by": {
        "en": "Lower by",
        "mr": "कमी",
        "hi": "कम",
    },
    "mandi_per_quintal": {
        "en": "per Quintal",
        "mr": "प्रति क्विंटल",
        "hi": "प्रति क्विंटल",
    },
    "mandi_chart_top_markets": {
        "en": "Top Markets Price Comparison (₹ / Quintal)",
        "mr": "प्रमुख बाजारांमधील भाव तुलना (₹ / क्विंटल)",
        "hi": "प्रमुख मंडियों में भाव तुलना (₹ / क्विंटल)",
    },
    "mandi_price_trend_title": {
        "en": "Historical Price Trend (Last 30 Days)",
        "mr": "ऐतिहासिक बाजारभाव कल (गेले ३० दिवस)",
        "hi": "ऐतिहासिक भाव रुझान (पिछले ३० दिन)",
    },
    "mandi_whatsapp_share": {
        "en": "Share on WhatsApp 📲",
        "mr": "व्हॉट्सअ‍ॅपवर शेअर करा 📲",
        "hi": "व्हाट्सएप पर साझा करें 📲",
    },
    "mandi_whatsapp_copied": {
        "en": "Market summary copied to clipboard!",
        "mr": "बाजारभाव सारांश क्लिपबोर्डवर कॉपी झाला!",
        "hi": "मंडी सारांश क्लिपबोर्ड पर कॉपी हो गया!",
    },
    "mandi_price_alert_title": {
        "en": "Set Price Alert",
        "mr": "भाव अलर्ट सूचना सेट करा",
        "hi": "भाव अलर्ट सेट करें",
    },
    "mandi_price_alert_desc": {
        "en": "Notify me when modal price reaches or exceeds ₹",
        "mr": "जेव्हा भाव खालील रुपयांवर किंवा पुढे जाईल तेव्हा मला कळवा ₹",
        "hi": "जब भाव इस स्तर पर या ऊपर पहुंचे तो सूचित करें ₹",
    },
    "mandi_set_alert_btn": {
        "en": "🔔 Save Alert",
        "mr": "🔔 अलर्ट जतन करा",
        "hi": "🔔 अलर्ट सहेजें",
    },
    "mandi_alert_success": {
        "en": "Price alert set successfully!",
        "mr": "भाव अलर्ट यशस्वीरीत्या सेट केला!",
        "hi": "भाव अलर्ट सफलतापूर्वक सेट किया गया!",
    },
    "mandi_disclaimer_notice": {
        "en": "Prices sourced from Agmarknet (data.gov.in). Actual auction rates may vary depending on moisture and quality grade. Verify with the APMC yard before dispatching harvest.",
        "mr": "दर Agmarknet (data.gov.in) वरून प्राप्त झालेले आहेत. ओलावा, स्वच्छता व प्रतवारीनुसार प्रत्यक्ष लिलावात फरक असू शकतो. शेतमाल वाहतूक करण्यापूर्वी संबंधित बाजार समितीशी खात्री करावी.",
        "hi": "भाव Agmarknet (data.gov.in) से प्राप्त हैं। नमी, सफाई और गुणवत्ता के अनुसार वास्तविक नीलामी में अंतर हो सकता है। माल रवाना करने से पहले संबंधित मंडी से पुष्टि अवश्य करें।",
    },
    "mandi_no_records_found": {
        "en": "No market price records found for this selection.",
        "mr": "या निकषांनुसार कोणतेही बाजारभाव आढळले नाहीत.",
        "hi": "इस चयन के लिए कोई मंडी भाव नहीं मिला।",
    },
    "mandi_records_count": {
        "en": "Available APMC Market Records",
        "mr": "उपलब्ध बाजारभाव नोंदी",
        "hi": "उपलब्ध मंडी भाव रिकॉर्ड",
    },
    "mandi_data_source": {
        "en": "Data Source",
        "mr": "माहिती स्रोत",
        "hi": "डेटा स्रोत",
    },
    "mandi_retrieved_at": {
        "en": "Retrieved at",
        "mr": "प्राप्त वेळ",
        "hi": "प्राप्त समय",
    },
    "mandi_transport_calc_title": {
        "en": "Transport Cost & Net Profit Calculator",
        "mr": "वाहतूक खर्च व निव्वळ नफा गणक",
        "hi": "परिवहन खर्च व शुद्ध लाभ कैलकुलेटर",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Retrieve localized text for a key and language code.

    Falls back to English if the translation or language is missing.
    """
    if lang not in ["en", "mr", "hi"]:
        lang = "en"

    entry = TRANSLATIONS.get(key)
    if not entry:
        return key.replace("_", " ").title()

    return entry.get(lang) or entry.get("en") or key.replace("_", " ").title()
