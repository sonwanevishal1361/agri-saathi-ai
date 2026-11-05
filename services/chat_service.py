"""Chat service orchestrating conversation history, RAG, and AI inference (Gemini & Ollama)."""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Generator
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.conversation import Conversation, Message
from models.crop import Crop
from models.user import User
from services.ollama_service import ollama_service
from services.gemini_service import gemini_service
from services.knowledge_service import KnowledgeService
from services.mandi_service import MandiService, COMMODITY_MAPPING, DISTRICT_COORDINATES
from utils.prompts import build_system_prompt
from core.exceptions import NotFoundError, AIInferenceError, ValidationError, ConfigurationError
from core.auth import verify_farmer_ownership
from config import settings
from utils.logging_config import logger

SAFETY_TRIGGER_KEYWORDS = [
    # English
    "pesticide", "insecticide", "fungicide", "weedicide", "herbicide",
    "chemical", "dosage", "dose", "spray", "poison", "toxicity",
    "chlorpyrifos", "monocrotophos", "mancozeb", "imidacloprid", "cypermethrin",
    "disease", "fungus", "blight", "rot", "wilt", "borer", "bollworm", "aphid",
    "infestation", "mildew", "rust",
    # Marathi
    "कीटकनाशक", "बुरशीनाशक", "फवारणी", "रासायनिक", "औषध", "डोस", "मात्रा",
    "रोग", "कीड", "अळी", "करपा", "तांबेरा", "मर", "भुरी", "मावा", "तुडतुडे",
    # Hindi
    "कीटनाशक", "फफूंदनाशक", "छिड़काव", "दवा", "कीड़ा", "बीमारी", "झुलसा",
]


def append_safety_disclaimer_if_needed(content: str, language: str = "en") -> str:
    """Append a localized KCC (1800-180-1551) and KVK advisory notice if content touches on chemicals, dosages, or diseases."""
    if not content:
        return content

    # If disclaimer already present, avoid duplication
    if "1800-180-1551" in content:
        return content

    content_lower = content.lower()
    is_triggered = any(kw.lower() in content_lower for kw in SAFETY_TRIGGER_KEYWORDS)
    if not is_triggered:
        return content

    lang = (language or "en").lower()
    if lang == "mr":
        notice = (
            "\n\n---\n⚠️ **महत्त्वाची कृषी सुरक्षा व सल्ला (KCC & KVK Advisory)**:\n"
            "रासायनिक कीटकनाशके किंवा बुरशीनाशकांची फवारणी करण्यापूर्वी अचूक मात्रा आणि सुरक्षिततेसाठी "
            "आपल्या जवळच्या **कृषी विज्ञान केंद्र (KVK)** किंवा कृषी सहाय्यकांचा प्रत्यक्ष सल्ला घ्या. "
            "मोफत मार्गदर्शनासाठी **किसान कॉल सेंटर (Kisan Call Centre)** टोल-फ्री क्रमांक **1800-180-1551** वर संपर्क साधा."
        )
    elif lang == "hi":
        notice = (
            "\n\n---\n⚠️ **महत्वपूर्ण कृषि सुरक्षा सलाह (KCC & KVK Advisory)**:\n"
            "रासायनिक कीटनाशक अथवा फफूंदनाशक का छिड़काव करने से पूर्व सटीक मात्रा हेतु "
            "अपने नजदीकी **कृषि विज्ञान केंद्र (KVK)** अथवा कृषि अधिकारी से परामर्श लें। "
            "नि:शुल्क त्वरित मार्गदर्शन हेतु **किसान कॉल सेंटर (Kisan Call Centre)** टोल-फ्री नंबर **1800-180-1551** पर संपर्क करें।"
        )
    else:
        notice = (
            "\n\n---\n⚠️ **Important Agricultural Safety Advisory (KCC & KVK Notice)**:\n"
            "Before applying chemical pesticides, fungicides, or determining exact dosages, "
            "consult your local **Krishi Vigyan Kendra (KVK)** or agricultural field officer. "
            "For free instant expert advice, call the **Kisan Call Centre toll-free at 1800-180-1551**."
        )

    return content + notice


MANDI_INTENT_KEYWORDS = [
    # Marathi
    "भाव", "दर", "बाजार भाव", "बाजारभाव", "मंडी", "लिलाव", "क्विंटल", "बाजार समिती", "हमीभाव", "बाजार",
    # Hindi
    "भाव", "दर", "मंडी भाव", "मंडी", "दाम", "रेट", "नीलामी", "क्विंटल", "समर्थन मूल्य",
    # English
    "mandi", "rate", "price", "apmc", "market price", "auction", "quintal", "msp", "market",
]

MR_DISTRICT_MAP = {
    "नागपूर": "Nagpur",
    "नागपुर": "Nagpur",
    "नाशिक": "Nashik",
    "नासिक": "Nashik",
    "पुणे": "Pune",
    "अमरावती": "Amravati",
    "वर्धा": "Wardha",
    "यवतमाळ": "Yavatmal",
    "अकोला": "Akola",
    "जळगाव": "Jalgaon",
    "सोलापूर": "Solapur",
    "कोल्हापूर": "Kolhapur",
    "संभाजीनगर": "Aurangabad",
    "औरंगाबाद": "Aurangabad",
    "नांदेड": "Nanded",
    "लातूर": "Latur",
    "बीड": "Beed",
    "अहमदनगर": "Ahmednagar",
    "अहिल्यानगर": "Ahmednagar",
    "सातारा": "Satara",
    "सांगली": "Sangli",
    "बुलढाणा": "Buldhana",
    "जालना": "Jalna",
    "परभणी": "Parbhani",
    "हिंगोली": "Hingoli",
    "वाशिम": "Washim",
    "भंडारा": "Bhandara",
    "गोंदिया": "Gondia",
    "चंद्रपूर": "Chandrapur",
    "गडचिरोली": "Gadchiroli",
    "उस्मानाबाद": "Osmanabad",
    "धाराशिव": "Osmanabad",
    "धुळे": "Dhule",
    "नंदुरबार": "Nandurbar",
    "रायगड": "Raigad",
    "रत्नागिरी": "Ratnagiri",
    "सिंधुदुर्ग": "Sindhudurg",
    "ठाणे": "Thane",
    "पालघर": "Palghar",
}


def detect_mandi_intent(user_text: str) -> Dict[str, Any]:
    """Detect if the user query asks about APMC mandi prices and extract commodity & district."""
    if not user_text:
        return {"is_mandi": False, "commodity": None, "district": None}

    lower_text = user_text.lower()
    # Mask agricultural pest attack terms that contain "भाव" (e.g. प्रादुर्भाव) so they are not misclassified as price queries
    sanitized_for_keywords = lower_text.replace("प्रादुर्भाव", "कीड_आक्रमण")
    has_keyword = any(kw.lower() in sanitized_for_keywords for kw in MANDI_INTENT_KEYWORDS)

    detected_comm = None

    # Check multilingual crop inflection roots (Marathi stem variations, e.g. कापूस -> कापसाचा)
    crop_roots = {
        "Cotton (Kapas)": ["कापूस", "कापस", "kapas", "cotton", "कपास"],
        "Soybean": ["सोयाबीन", "soybean", "soyabean"],
        "Onion": ["कांदा", "कांद्या", "कांद", "kanda", "onion", "प्याज"],
        "Wheat": ["गहू", "गव्हा", "gehu", "wheat", "गेहूं"],
        "Pigeon Pea (Tur)": ["तूर", "तुरी", "tur", "arhar", "अरहर"],
        "Gram (Chana)": ["हरभरा", "हरभऱ्या", "हरभ", "chana", "चना", "gram"],
        "Tomato": ["टोमॅटो", "tomato", "टमाटर"],
    }
    for comm_name, roots in crop_roots.items():
        if any(r.lower() in lower_text for r in roots):
            detected_comm = comm_name
            break

    if not detected_comm:
        commodities = COMMODITY_MAPPING.get("commodities", [])
        for item in commodities:
            names_to_check = [
                item.get("id", "").lower(),
                item.get("en", "").lower(),
                item.get("mr", "").lower(),
                item.get("hi", "").lower(),
            ] + [a.lower() for a in item.get("aliases", [])]
            for name in names_to_check:
                if name and name in lower_text:
                    detected_comm = item["en"]
                    break
            if detected_comm:
                break

    detected_district = None
    districts = list(DISTRICT_COORDINATES.keys())
    for d in districts:
        if d.lower() in lower_text:
            detected_district = d
            break

    if not detected_district:
        for mr_name, en_dist in MR_DISTRICT_MAP.items():
            if mr_name in user_text:
                detected_district = en_dist
                break

    is_mandi = has_keyword or (
        detected_comm is not None and any(w in sanitized_for_keywords for w in ["भाव", "दर", "rate", "price"])
    )
    return {
        "is_mandi": is_mandi,
        "commodity": detected_comm,
        "district": detected_district,
    }


def build_mandi_summary_text(mandi_res: Dict[str, Any], language: str = "en") -> str:
    """Generate deterministic, hallucination-free APMC market rate table in the farmer's language."""
    records = mandi_res.get("records", []) if mandi_res else []
    lang = (language or "en").lower()

    if not records:
        if lang == "mr":
            return "सध्या या पिकासाठी अधिकृत Agmarknet (Data.gov.in) वर थेट बाजारभाव नोंदी उपलब्ध नाहीत. कृपया आपल्या स्थानिक बाजार समितीशी संपर्क साधावा."
        elif lang == "hi":
            return "वर्तमान में इस फसल के लिए आधिकारिक Agmarknet (Data.gov.in) पर कोई मंडी भाव रिकॉर्ड उपलब्ध नहीं हैं। कृपया अपनी स्थानीय मंडी से संपर्क करें।"
        return "No official APMC market rates are currently published for this commodity on Agmarknet (Data.gov.in). Please check directly with your local market yard."

    latest_date = mandi_res.get("latest_arrival_date") or records[0].get("data_date", "")
    source_type = mandi_res.get("source", "live")
    is_live = mandi_res.get("has_today_prices", False) and source_type == "live"

    lines = []
    if lang == "mr":
        header_tag = "आजचे थेट लिलाव दर" if is_live else f"उपलब्ध नवीनतम बाजारभाव ({latest_date})"
        lines.append(f"📈 **कृषी उत्पन्न बाजार समिती (APMC) दर — {header_tag}**")
        lines.append(f"स्रोत: Agmarknet (Data.gov.in) | आवक दिनांक: {latest_date}\n")
        lines.append("| बाजार समिती | वाण | किमान (₹/क्विंटल) | कमाल (₹/क्विंटल) | **मॉडेल भाव (₹/क्विंटल)** |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")
        for r in records[:5]:
            lines.append(f"| {r.get('market')} ({r.get('district')}) | {r.get('variety')} | ₹{int(r.get('min_price', 0))} | ₹{int(r.get('max_price', 0))} | **₹{int(r.get('modal_price', 0))}** |")
        lines.append("\n💡 *टीप: लिलाव दर शेतमालाच्या प्रत व ओलाव्यावर अवलंबून बदलू शकतात.*")
    elif lang == "hi":
        header_tag = "आज के लाइव नीलामी भाव" if is_live else f"उपलब्ध नवीनतम मंडी भाव ({latest_date})"
        lines.append(f"📈 **कृषि उपज मंडी समिति (APMC) भाव — {header_tag}**")
        lines.append(f"स्रोत: Agmarknet (Data.gov.in) | आवक तिथि: {latest_date}\n")
        lines.append("| मंडी | किस्म | न्यूनतम (₹/क्विंटल) | अधिकतम (₹/क्विंटल) | **मॉडल भाव (₹/क्विंटल)** |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")
        for r in records[:5]:
            lines.append(f"| {r.get('market')} ({r.get('district')}) | {r.get('variety')} | ₹{int(r.get('min_price', 0))} | ₹{int(r.get('max_price', 0))} | **₹{int(r.get('modal_price', 0))}** |")
        lines.append("\n💡 *नोट: नीलामी दर उपज की गुणवत्ता और नमी पर निर्भर करते हैं।*")
    else:
        header_tag = "Today's Live Rates" if is_live else f"Latest Available Arrivals ({latest_date})"
        lines.append(f"📈 **APMC Mandi Market Rates — {header_tag}**")
        lines.append(f"Source: Agmarknet (Data.gov.in) | Arrival Date: {latest_date}\n")
        lines.append("| Market | Variety | Min (₹/Qtl) | Max (₹/Qtl) | **Modal Price (₹/Qtl)** |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")
        for r in records[:5]:
            lines.append(f"| {r.get('market')} ({r.get('district')}) | {r.get('variety')} | ₹{int(r.get('min_price', 0))} | ₹{int(r.get('max_price', 0))} | **₹{int(r.get('modal_price', 0))}** |")
        lines.append("\n💡 *Note: Auction rates vary based on moisture and quality grading.*")

    return "\n".join(lines)


def verify_mandi_reply_integrity(reply_text: str, records: List[Dict[str, Any]]) -> bool:
    """Verify that numbers quoted in reply as prices are grounded in verified records."""
    if not records or not reply_text:
        return True

    ignored = {"2024", "2025", "2026", "2027", "1800", "1551", "100", "50", "10"}
    valid_exact = set()
    min_possible = min(float(r.get("min_price", 0)) for r in records)
    max_possible = max(float(r.get("max_price", 0)) for r in records)

    for r in records:
        for p_key in ("modal_price", "min_price", "max_price"):
            val = r.get(p_key)
            if val is not None:
                valid_exact.add(int(round(float(val))))

    cleaned_reply = reply_text.replace(",", "")
    p1 = re.findall(r'(?:₹|rs\.?|रू\.?|inr)\s*(\d{3,6})', cleaned_reply, re.IGNORECASE)
    p2 = re.findall(r'(\d{3,6})\s*(?:रुपये|रु|rs|/-|प्रति|भाव|दर)', cleaned_reply, re.IGNORECASE)
    found_prices = []
    for num_str in p1 + p2:
        if num_str not in ignored:
            found_prices.append(int(num_str))

    if not found_prices:
        return True

    for p in found_prices:
        if p not in valid_exact and not (min_possible * 0.9 <= p <= max_possible * 1.1):
            return False

    return True


class ChatService:

    detect_mandi_intent = staticmethod(detect_mandi_intent)
    build_mandi_summary_text = staticmethod(build_mandi_summary_text)
    verify_mandi_reply_integrity = staticmethod(verify_mandi_reply_integrity)

    @staticmethod
    def create_conversation(
        db: Session,
        farmer_id: str,
        title: str = "New Farming Query",
        preferred_language: str = "en",
    ) -> Conversation:
        """Create a new chat conversation for the authenticated farmer."""
        conv = Conversation(
            farmer_id=farmer_id,
            title=title.strip()[:200],
            preferred_language=preferred_language,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def get_conversation(db: Session, farmer_id: str, conversation_id: str) -> Conversation:
        """Get a conversation with farmer ownership check."""
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise NotFoundError(f"Conversation {conversation_id} not found.")
        verify_farmer_ownership(farmer_id, conv.farmer_id, resource_name="Conversation")
        return conv

    @staticmethod
    def list_conversations(db: Session, farmer_id: str, limit: int = 20) -> List[Conversation]:
        """List all conversations owned by the authenticated farmer."""
        return (
            db.query(Conversation)
            .filter(Conversation.farmer_id == farmer_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_conversation(db: Session, farmer_id: str, conversation_id: str) -> bool:
        """Delete a conversation with ownership check."""
        conv = ChatService.get_conversation(db, farmer_id, conversation_id)
        db.delete(conv)
        db.commit()
        return True

    @staticmethod
    def get_daily_user_chat_count(db: Session, farmer_id: str) -> int:
        """Count user queries submitted by this farmer today (UTC day)."""
        start_of_day = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
        return (
            db.query(Message)
            .filter(
                Message.farmer_id == farmer_id,
                Message.role == "user",
                Message.created_at >= start_of_day,
            )
            .count()
        )

    @staticmethod
    def check_daily_limit(db: Session, farmer_id: str) -> bool:
        """Return True if farmer has reached or exceeded their daily AI query quota."""
        count = ChatService.get_daily_user_chat_count(db, farmer_id)
        return count >= settings.AI_DAILY_REQUEST_LIMIT

    @staticmethod
    def get_daily_limit_message(language: str = "en") -> str:
        """Return a warm, respectful localized message when daily AI query limit is reached."""
        limit = settings.AI_DAILY_REQUEST_LIMIT
        lang = (language or "en").lower()
        if lang == "mr":
            return (
                f"🙏 **आजची AI प्रश्न मर्यादा पूर्ण झाली आहे.**\n\n"
                f"शेतकरी मित्रा, आजसाठी तुमची मोफत AI प्रश्न मर्यादा ({limit} प्रश्न) पूर्ण झाली आहे. "
                "आमची AI सल्लागार सेवा उद्या सकाळी पुन्हा उपलब्ध होईल.\n\n"
                "📌 तोपर्यंत तुम्ही तुमच्या इतर सर्व शेती नोंदी, खर्च, हवामान व बाजारभाव तपासू शकता.\n"
                "📞 **तातडीच्या शेती सल्ल्यासाठी**: किसान कॉल सेंटर **1800-180-1551** (टोल-फ्री) वर संपर्क साधा."
            )
        elif lang == "hi":
            return (
                f"🙏 **आज की AI प्रश्न सीमा पूरी हो गई है।**\n\n"
                f"किसान भाई, आज के लिए आपकी AI प्रश्न सीमा ({limit} प्रश्न) पूरी हो चुकी है। "
                "यह सेवा कल सुबह फिर से उपलब्ध होगी।\n\n"
                "📌 तब तक आप अपने सभी फसल रिकॉर्ड, कृषि खर्च, मौसम और मंडी भाव देख सकते हैं।\n"
                "📞 **आपातकालीन कृषि सलाह के लिए**: किसान कॉल सेंटर **1800-180-1551** (टोल-फ्री) पर संपर्क करें।"
            )
        return (
            f"🙏 **Daily AI Question Limit Reached.**\n\n"
            f"Dear Farmer, you have reached your daily limit of {limit} AI queries for today. "
            "Your quota will reset tomorrow morning.\n\n"
            "📌 In the meantime, your farm records, crop diaries, weather forecast, and mandi prices remain fully accessible.\n"
            "📞 **For immediate agricultural assistance**: Contact Kisan Call Centre toll-free at **1800-180-1551**."
        )

    @staticmethod
    def prepare_chat_context(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        user_text: str,
        crop_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Prepare grounded conversation context, persist user message, and build LLM payload."""
        cleaned_text = (user_text or "").strip()
        if not cleaned_text:
            raise ValidationError("Message cannot be empty.")

        conv = ChatService.get_conversation(db, farmer_id, conversation_id)

        # 1. Fetch authorized crop context if specified
        crop_context = None
        crop_name = None
        if crop_id:
            crop = db.query(Crop).filter(Crop.id == crop_id).first()
            if crop:
                verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")
                crop_context = {
                    "name": crop.name,
                    "variety": crop.variety,
                    "area": crop.area,
                    "area_unit": crop.area_unit,
                    "sowing_date": str(crop.sowing_date),
                    "growth_stage": crop.growth_stage,
                    "soil_type": crop.soil_type,
                    "irrigation_method": crop.irrigation_method,
                }
                crop_name = crop.name

        # 2. Retrieve verified knowledge passages via lightweight TF-IDF RAG
        search_query = f"{crop_name or ''} {cleaned_text}"
        retrieved_docs = KnowledgeService.retrieve_relevant_documents(
            db=db,
            query=search_query,
            top_k=2,
        )
        compact_docs = []
        for d in retrieved_docs:
            d_copy = dict(d)
            if len(d_copy.get("content", "")) > 400:
                d_copy["content"] = d_copy["content"][:400] + "..."
            compact_docs.append(d_copy)

        # 3. Construct system prompt
        effective_lang = language or conv.preferred_language or "en"
        system_content = build_system_prompt(
            language=effective_lang,
            crop_context=crop_context,
            retrieved_documents=compact_docs,
        )

        # 3.1 Check for Mandi market rate intent and ground with verified live Agmarknet records
        mandi_intent = detect_mandi_intent(cleaned_text)
        mandi_info = None

        if mandi_intent.get("is_mandi"):
            m_comm = mandi_intent.get("commodity") or crop_name
            farmer_user = db.query(User).filter(User.id == farmer_id).first() if farmer_id else None
            m_dist = mandi_intent.get("district") or (farmer_user.district if farmer_user else None)
            m_state = farmer_user.state if farmer_user and farmer_user.state else "Maharashtra"

            try:
                mandi_res = MandiService.get_mandi_prices(
                    state=m_state,
                    district=m_dist,
                    commodity=m_comm,
                )
                mandi_records = mandi_res.get("records", [])
                latest_date = mandi_res.get("latest_arrival_date") or "N/A"
                source_mode = mandi_res.get("source", "unknown")

                mandi_context_block = (
                    f"\n\n=== VERIFIED API DATA (DATA.GOV.IN AGMARKNET) ===\n"
                    f"Target Commodity: {m_comm or 'All'}\n"
                    f"Location Filter: District={m_dist or 'Any'}, State={m_state}\n"
                    f"Source: {source_mode}\n"
                    f"Latest Available Arrival Date: {latest_date}\n"
                    f"Verified Records Count: {len(mandi_records)}\n"
                )
                if mandi_records:
                    mandi_context_block += "Verified Price Records (Min, Max, Modal in Rs/Quintal):\n"
                    for r in mandi_records[:7]:
                        mandi_context_block += (
                            f"- APMC Market: {r.get('market')} ({r.get('district')}), Variety: {r.get('variety')}, "
                            f"Arrival Date: {r.get('data_date')}, Min: Rs {r.get('min_price')}, "
                            f"Max: Rs {r.get('max_price')}, Modal: Rs {r.get('modal_price')}/Quintal\n"
                        )
                else:
                    mandi_context_block += "No market auction records currently published for this selection on Agmarknet.\n"

                mandi_context_block += (
                    "STRICT GROUNDING INSTRUCTIONS:\n"
                    "1. Quote ONLY the numbers present in the verified records above.\n"
                    "2. NEVER invent, extrapolate, or hallucinate market rates.\n"
                    f"3. Explicitly state the date ({latest_date}). Never say 'today's live rate' unless Source is 'live' and date is today.\n"
                    "4. If no records are listed, clearly inform the farmer that rates are not yet published for this market on Agmarknet.\n"
                    "=== END VERIFIED API DATA ===\n"
                )
                system_content += mandi_context_block
                mandi_info = {
                    "is_mandi": True,
                    "commodity": m_comm,
                    "district": m_dist,
                    "mandi_res": mandi_res,
                }
            except Exception as e:
                logger.warning(f"Error fetching mandi context for chat query: {e}")

        # 4. Load recent message history (bounded context for current conversation only)
        max_history = settings.MAX_CHAT_HISTORY
        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(max_history)
            .all()
        )
        recent_messages.reverse()

        # Build prompt payload
        messages_payload: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        for m in recent_messages:
            messages_payload.append({"role": m.role, "content": m.content})
        messages_payload.append({"role": "user", "content": cleaned_text})

        # 5. Persist the user's message
        user_msg = Message(
            conversation_id=conversation_id,
            farmer_id=farmer_id,
            role="user",
            content=cleaned_text,
        )
        db.add(user_msg)

        # Update conversation title if this is the first message
        if len(recent_messages) == 0:
            title_candidate = cleaned_text[:40].replace("\n", " ").strip()
            if len(cleaned_text) > 40:
                title_candidate += "..."
            conv.title = title_candidate

        db.commit()

        # Check daily quota (including the message just persisted)
        daily_count = ChatService.get_daily_user_chat_count(db, farmer_id)
        limit_reached = daily_count > settings.AI_DAILY_REQUEST_LIMIT

        return {
            "messages_payload": messages_payload,
            "retrieved_docs": retrieved_docs,
            "crop_name": crop_name,
            "effective_lang": effective_lang,
            "conversation": conv,
            "limit_reached": limit_reached,
            "daily_count": daily_count,
            "mandi_info": mandi_info,
        }

    @staticmethod
    def generate_reply(messages_payload: List[Dict[str, str]]) -> str:
        """Call AI provider (Gemini primary, Ollama optional fallback)."""
        provider = (settings.AI_PROVIDER or "gemini").strip().lower()

        if provider == "gemini":
            try:
                return gemini_service.chat_completion(messages_payload)
            except (AIInferenceError, ConfigurationError) as e:
                logger.warning(f"Primary Gemini AI failed: {e}")
                if settings.ENABLE_OLLAMA_FALLBACK:
                    logger.info("Attempting optional Ollama fallback...")
                    try:
                        return ollama_service.chat_completion(messages_payload)
                    except Exception as ollama_err:
                        logger.error(f"Ollama fallback also failed: {ollama_err}")
                        return (
                            f"⚠️ **AI Service Notification**: Google Gemini AI failed ({str(e)}), "
                            f"and Ollama fallback also failed ({str(ollama_err)}).\n\n"
                            "Your question has been saved and your other farm records are fully accessible."
                        )
                # Fallback disabled - do not silently switch to slow Ollama
                return (
                    f"⚠️ **AI Service Notification**: Google Gemini AI assistant is currently unavailable ({str(e)}).\n\n"
                    "Please check your `GEMINI_API_KEY` configuration or network connection. "
                    "Your question has been saved and your other farm records are fully accessible."
                )

        # Provider is Ollama
        try:
            return ollama_service.chat_completion(messages_payload)
        except AIInferenceError as e:
            logger.warning(f"Ollama inference failure: {str(e)}")
            return (
                f"⚠️ **AI Service Notification**: Local AI assistant is currently unavailable ({str(e)}).\n\n"
                "Please ensure Ollama is running locally with the command `ollama serve`.\n"
                "Your question has been saved and your other farm records are fully accessible."
            )

    @staticmethod
    def stream_reply(messages_payload: List[Dict[str, str]], language: str = "en") -> Generator[str, None, None]:
        """Stream AI reply chunks from Gemini, with graceful fallback and automated safety advisory."""
        provider = (settings.AI_PROVIDER or "gemini").strip().lower()
        accumulated: List[str] = []

        def _yield_safety_suffix():
            full_text = "".join(accumulated)
            enhanced = append_safety_disclaimer_if_needed(full_text, language)
            if len(enhanced) > len(full_text):
                yield enhanced[len(full_text):]

        if provider == "gemini":
            try:
                for chunk in gemini_service.stream_chat_completion(messages_payload):
                    accumulated.append(chunk)
                    yield chunk
                yield from _yield_safety_suffix()
                return
            except (AIInferenceError, ConfigurationError) as e:
                logger.warning(f"Primary Gemini stream failed: {e}")
                if settings.ENABLE_OLLAMA_FALLBACK:
                    logger.info("Attempting Ollama fallback for stream request...")
                    try:
                        reply = ollama_service.chat_completion(messages_payload)
                        accumulated.append(reply)
                        yield reply
                        yield from _yield_safety_suffix()
                        return
                    except Exception as ollama_err:
                        yield (
                            f"⚠️ **AI Service Notification**: Google Gemini stream failed ({str(e)}), "
                            f"and Ollama fallback also failed ({str(ollama_err)})."
                        )
                        return
                yield (
                    f"⚠️ **AI Service Notification**: Google Gemini AI assistant is currently unavailable ({str(e)}).\n\n"
                    "Please check your `GEMINI_API_KEY` configuration or network connection. "
                    "Your question has been saved and your other farm records are fully accessible."
                )
                return

        # Provider is Ollama
        try:
            reply = ollama_service.chat_completion(messages_payload)
            accumulated.append(reply)
            yield reply
            yield from _yield_safety_suffix()
        except AIInferenceError as e:
            yield (
                f"⚠️ **AI Service Notification**: Local AI assistant is currently unavailable ({str(e)}).\n\n"
                "Please ensure Ollama is running locally with the command `ollama serve`.\n"
                "Your question has been saved and your other farm records are fully accessible."
            )

    @staticmethod
    def save_assistant_message(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        content: str,
        language: str = "en",
    ) -> Message:
        """Persist assistant reply in the database with safety disclaimers applied."""
        final_content = append_safety_disclaimer_if_needed(content, language)
        assistant_msg = Message(
            conversation_id=conversation_id,
            farmer_id=farmer_id,
            role="assistant",
            content=final_content,
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg

    @staticmethod
    def send_message(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        user_text: str,
        crop_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Process user message synchronously, ground with RAG and authorized crop context, and call LLM."""
        context = ChatService.prepare_chat_context(
            db=db,
            farmer_id=farmer_id,
            conversation_id=conversation_id,
            user_text=user_text,
            crop_id=crop_id,
            language=language,
        )

        if context.get("limit_reached"):
            assistant_reply = ChatService.get_daily_limit_message(language)
        else:
            mandi_info = context.get("mandi_info")
            if mandi_info and mandi_info.get("is_mandi"):
                mandi_res = mandi_info.get("mandi_res") or {}
                records = mandi_res.get("records", [])
                try:
                    raw_reply = ChatService.generate_reply(context["messages_payload"])
                    # Check for hallucinated or unverified numbers
                    if records and not verify_mandi_reply_integrity(raw_reply, records):
                        logger.warning("AI mandi reply contained unverified rates; substituting deterministic summary table.")
                        raw_reply = build_mandi_summary_text(mandi_res, language)
                    assistant_reply = append_safety_disclaimer_if_needed(raw_reply, language)
                except Exception as ai_err:
                    logger.warning(f"AI failed on mandi query; using deterministic table fallback: {ai_err}")
                    raw_reply = build_mandi_summary_text(mandi_res, language)
                    assistant_reply = append_safety_disclaimer_if_needed(raw_reply, language)
            else:
                raw_reply = ChatService.generate_reply(context["messages_payload"])
                assistant_reply = append_safety_disclaimer_if_needed(raw_reply, language)

        assistant_msg = ChatService.save_assistant_message(
            db=db,
            farmer_id=farmer_id,
            conversation_id=conversation_id,
            content=assistant_reply,
            language=language,
        )

        return {
            "response": assistant_reply,
            "sources": context["retrieved_docs"],
            "crop_context_used": context["crop_name"],
            "message_id": assistant_msg.id,
            "mandi_info": context.get("mandi_info"),
        }
