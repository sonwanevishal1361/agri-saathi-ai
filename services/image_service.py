"""Crop image management, symptom assessment, and health observation service."""

import os
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from config import settings
from models.health_observation import HealthObservation
from core.exceptions import ValidationError
from utils.validation import validate_image_file, sanitize_filename
from utils.logging_config import logger

# Agronomic symptom guide database based on ICAR and State Agricultural University advisories
SYMPTOM_DISEASE_KNOWLEDGE: List[Dict[str, Any]] = [
    {
        "crops": ["cotton"],
        "keywords": ["yellowing", "leaf curl", "vein clearing", "curling"],
        "possible_condition": "Cotton Leaf Curl Virus (CLCuV) / Sucking Pest Injury",
        "primary_causes": "Transmitted primarily by Whiteflies (Bemisia tabaci) or severe nutrient imbalance.",
        "management_guidelines": (
            "1. Monitor whitefly populations using yellow sticky traps (15-20 traps/acre).\n"
            "2. Avoid excessive nitrogenous fertilizers which favor sucking pest multiplication.\n"
            "3. Spray neem oil (5ml/L) or botanical formulations in early infestation.\n"
            "4. Consult your local Krishi Vigyan Kendra (KVK) for recommended pest threshold-based interventions."
        ),
        "source": "Central Institute for Cotton Research (CICR) Advisory",
    },
    {
        "crops": ["cotton"],
        "keywords": ["boll", "worm", "hole", "dropping", "pink"],
        "possible_condition": "Pink Bollworm / American Bollworm Attack",
        "primary_causes": "Larvae boring into squares, flowers, and bolls, causing premature shedding.",
        "management_guidelines": (
            "1. Install pheromone traps at 5 traps/acre for monitoring moth emergence.\n"
            "2. Handpick and destroy affected rosetted flowers and dropped bolls.\n"
            "3. Erect bird perches (10-15 per acre) to encourage natural predators.\n"
            "4. Follow ETL (Economic Threshold Level) guidelines before applying any university-recommended sprays."
        ),
        "source": "ICAR - CICR Nagpur Guidelines",
    },
    {
        "crops": ["soybean"],
        "keywords": ["yellow", "mosaic", "leaf spots", "mottling"],
        "possible_condition": "Soybean Yellow Mosaic Virus (YMV)",
        "primary_causes": "Viral disease vectored by whiteflies in humid/warm monsoon weather.",
        "management_guidelines": (
            "1. Rogue out and safely destroy virus-infected plants during early vegetative stage.\n"
            "2. Keep fields weed-free, as weeds act as alternate hosts for whiteflies.\n"
            "3. Use yellow sticky traps to reduce vector population.\n"
            "4. Do not harvest seeds from infected plants for future sowing."
        ),
        "source": "ICAR - Indian Institute of Soybean Research (IISR) Indore",
    },
    {
        "crops": ["soybean", "cotton", "chana", "gram"],
        "keywords": ["wilting", "root rot", "drying", "drooping", "stem black"],
        "possible_condition": "Fusarium Wilt / Rhizoctonia Root Rot",
        "primary_causes": "Soil-borne fungal pathogens active during alternating moisture stress and waterlogging.",
        "management_guidelines": (
            "1. Avoid water stagnation; ensure excellent field drainage.\n"
            "2. In future sowings, practice seed treatment with Trichoderma viride (10g/kg seed).\n"
            "3. Follow 3-year crop rotation with non-host crops such as sorghum or millets.\n"
            "4. Remove and burn severely wilted plants to prevent pathogen spore spread."
        ),
        "source": "State Agricultural Universities (SAUs) Package of Practices",
    },
    {
        "crops": ["tomato"],
        "keywords": ["blight", "spots", "brown", "concentric rings", "leaf burning"],
        "possible_condition": "Early Blight (Alternaria solani) / Late Blight",
        "primary_causes": "Fungal infection thriving in high humidity, wet foliage, and temperatures between 20-30°C.",
        "management_guidelines": (
            "1. Avoid overhead sprinkler irrigation; switch to drip to keep foliage dry.\n"
            "2. Prune lower diseased leaves touching the soil surface and safely dispose of them.\n"
            "3. Mulch soil around tomato plants to prevent soil-splash onto lower foliage.\n"
            "4. Apply protective copper-based or university-recommended fungicide under KVK agronomic guidance."
        ),
        "source": "ICAR - Indian Institute of Horticultural Research (IIHR)",
    },
    {
        "crops": ["wheat"],
        "keywords": ["rust", "orange", "yellow stripes", "powder", "pustules"],
        "possible_condition": "Yellow (Stripe) Rust / Brown Rust (Puccinia spp.)",
        "primary_causes": "Airborne fungal spores favored by cool, moist morning dew conditions.",
        "management_guidelines": (
            "1. Regularly survey fields for initial yellow pustule development on leaf blades.\n"
            "2. Grow certified rust-resistant varieties recommended by ICAR-IIWBR.\n"
            "3. Avoid excessive nitrogen applications.\n"
            "4. Consult district agriculture officer immediately upon spot confirmation."
        ),
        "source": "ICAR - Indian Institute of Wheat and Barley Research (IIWBR) Karnal",
    },
    {
        "crops": ["general", "all"],
        "keywords": ["yellowing", "pale", "stunted", "nitrogen", "deficiency"],
        "possible_condition": "Nutrient Deficiency (Likely Nitrogen / Micronutrient)",
        "primary_causes": "Insufficient soil organic matter, high soil alkalinity, or leached soil nutrients.",
        "management_guidelines": (
            "1. Conduct a Soil Health Card laboratory test to verify exact N-P-K and micronutrient deficits.\n"
            "2. Apply well-decomposed Farm Yard Manure (FYM) or vermicompost to improve soil structure.\n"
            "3. Consider balanced foliar spray of water-soluble 19:19:19 or zinc/iron sulphate if recommended."
        ),
        "source": "Department of Agriculture & Farmers Welfare, GoI",
    },
]


class ImageService:

    @staticmethod
    def save_uploaded_crop_image(file_bytes: bytes, filename: str) -> str:
        """Validate and save an uploaded crop image file securely.

        Returns relative stored filepath.
        """
        # Validate format and size
        validate_image_file(file_bytes, filename)

        # Generate safe random filename to prevent directory traversal or collision
        clean_name = sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower() or ".jpg"
        unique_name = f"crop_{uuid.uuid4().hex}{ext}"

        save_path = settings.UPLOAD_DIR / unique_name
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"Saved verified crop image: {unique_name} ({len(file_bytes)} bytes)")
        return str(unique_name)

    @staticmethod
    def analyze_crop_symptoms(
        crop_name: str,
        symptom_text: str,
        plant_part: str = "Leaves",
        onset: str = "Gradual",
    ) -> Dict[str, Any]:
        """Analyze reported symptoms against verified agronomic knowledge.

        Adheres strictly to safety protocols:
        - Explains that automated vision inference is not configured for local text model (Qwen 2.5 3B).
        - Matches verified university diagnostic symptoms.
        - Provides non-hazardous agronomic guidance with explicit KVK safety disclaimers.
        """
        crop_clean = crop_name.strip().lower()
        query_text = f"{symptom_text} {plant_part} {onset}".lower()

        # Match against knowledge rules
        matched_conditions = []
        for rule in SYMPTOM_DISEASE_KNOWLEDGE:
            rule_crops = [c.lower() for c in rule["crops"]]
            # Check crop match or general
            crop_match = "general" in rule_crops or "all" in rule_crops or any(c in crop_clean for c in rule_crops)
            if not crop_match:
                continue

            # Check keyword match score
            matched_kw = [kw for kw in rule["keywords"] if kw in query_text]
            if matched_kw:
                matched_conditions.append({
                    "condition": rule["possible_condition"],
                    "causes": rule["primary_causes"],
                    "management": rule["management_guidelines"],
                    "source": rule["source"],
                    "relevance_score": len(matched_kw),
                })

        # Sort by relevance score
        matched_conditions.sort(key=lambda x: x["relevance_score"], reverse=True)

        disclaimer = (
            "IMPORTANT AGRI-SAFETY NOTICE: This text assessment is grounded in verified ICAR / University "
            "agronomic literature for educational assistance. It is NOT a definitive diagnosis. Never apply "
            "chemical pesticides or fungicides without physical sample confirmation from your local Krishi "
            "Vigyan Kendra (KVK) or Agriculture Extension Officer."
        )

        model_note = (
            "Note: The local AI model (Qwen 2.5 3B) operates as a text and reasoning engine. Automated "
            "computer vision diagnosis is not currently enabled, to avoid hallucinated or risky chemical prescriptions."
        )

        return {
            "status": "success",
            "crop": crop_name,
            "reported_symptoms": symptom_text,
            "plant_part": plant_part,
            "matches_found": len(matched_conditions),
            "diagnoses": matched_conditions[:2] if matched_conditions else [],
            "general_advice": (
                "If symptoms are spreading rapidly, isolate affected plants, take physical sample leaves in a clean "
                "envelope, and visit the nearest Taluka Agriculture Office or KVK diagnostic clinic."
            ) if not matched_conditions else None,
            "model_notice": model_note,
            "safety_disclaimer": disclaimer,
        }

    @staticmethod
    def record_health_observation(
        db: Session,
        farmer_id: str,
        crop_id: Optional[str],
        symptom_description: str,
        image_storage_path: Optional[str],
        analysis_result: Dict[str, Any],
    ) -> HealthObservation:
        """Store crop health observation record in database with farmer ownership."""
        if not symptom_description.strip():
            raise ValidationError("Symptom description cannot be empty.")

        causes_text = ""
        advice_text = ""
        source_text = "ICAR Agricultural Guidelines"

        if analysis_result and analysis_result.get("diagnoses"):
            primary = analysis_result["diagnoses"][0]
            causes_text = f"Condition: {primary.get('condition')}\nCauses: {primary.get('causes')}"
            advice_text = primary.get("management", "")
            source_text = primary.get("source", source_text)

        obs = HealthObservation(
            farmer_id=farmer_id,
            crop_id=crop_id,
            symptom_description=symptom_description.strip(),
            image_storage_path=image_storage_path,
            possible_causes=causes_text,
            advice_summary=advice_text,
            source_reference=source_text,
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        logger.info(f"Recorded health observation: {obs.id} for farmer {farmer_id}")
        return obs

    @staticmethod
    def list_farmer_observations(db: Session, farmer_id: str, limit: Optional[int] = None) -> List[HealthObservation]:
        """List all health observation records owned by farmer."""
        query = (
            db.query(HealthObservation)
            .filter(HealthObservation.farmer_id == farmer_id)
            .order_by(HealthObservation.created_at.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()
