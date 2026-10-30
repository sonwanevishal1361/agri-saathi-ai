"""Seed verified agricultural knowledge and RAG documents into database."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import get_db, init_db
from models.knowledge import CropKnowledge, KnowledgeDocument
from utils.logging_config import logger


CROPS_KNOWLEDGE_DATA = [
    {
        "crop_name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "description": "Cotton is one of the most significant commercial fiber crops in India, extensively grown in Maharashtra, Gujarat, Telangana, and Punjab.",
        "soil_requirements": "Deep, well-drained black clay soils (regur) with good water retention capacity and neutral to slightly alkaline pH (6.5 to 8.0). Avoid waterlogged soils.",
        "climate_requirements": "Warm, sunny climate with minimum 180 to 200 frost-free days. Optimum temperature between 21°C and 30°C. High sunshine required during boll maturation.",
        "sowing_information": "Kharif sowing begins with monsoon onset (June - July). Seed rate: 1.5 - 2.5 kg/acre for Bt hybrids. Spacing: 90 cm x 60 cm or 120 cm x 45 cm depending on soil depth.",
        "irrigation_information": "Critical irrigation stages: Squaring (40-45 DAS), flowering (65-70 DAS), and boll development (85-110 DAS). Drip irrigation saves 30-40% water.",
        "nutrient_management": "Recommended N:P:K 100:50:50 kg/ha. Apply nitrogen in three equal splits: at sowing, square initiation, and peak flowering. Apply 25 kg/ha ZnSO4 in deficient soils.",
        "pest_disease_information": "Key pests: Pink bollworm, Whiteflies, Thrips, Aphids. Diseases: Bacterial leaf blight, Leaf curl virus. Use pheromone traps (5/acre) and yellow sticky traps (15/acre).",
        "harvesting_information": "Pick mature, fully opened clean bolls in morning hours after dew has dried. Avoid trash, dried bracts, or immature bolls. Store in dry, moisture-free godowns.",
        "source_name": "ICAR - Central Institute for Cotton Research (CICR) Nagpur",
        "source_url": "https://cicr.icar.gov.in/",
    },
    {
        "crop_name": "Soybean",
        "scientific_name": "Glycine max",
        "description": "Soybean is a vital Kharif oilseed and protein crop cultivated across Madhya Pradesh, Maharashtra, Rajasthan, and Karnataka.",
        "soil_requirements": "Well-drained fertile loamy to clay soils with pH between 6.0 and 7.5. Soybean is sensitive to waterlogging and soil salinity.",
        "climate_requirements": "Warm and moist tropical climate. Ideal temperature range 25°C to 32°C. Requires 600 - 800 mm evenly distributed rainfall during vegetative and pod-filling stages.",
        "sowing_information": "Sow between June 20 and July 10 upon receiving at least 75-100 mm rain. Seed rate: 25-30 kg/acre. Treat seeds with Rhizobium japonicum and Trichoderma viride.",
        "irrigation_information": "Primarily rainfed. If dry spells occur, protective irrigation at flowering (35-40 DAS) and pod-filling (55-65 DAS) is critical to prevent yield collapse.",
        "nutrient_management": "Recommended N:P:K 20:60:40 kg/ha + 20 kg Sulphur/ha. Being a legume, soybean fixes atmospheric nitrogen; avoid excessive nitrogen which causes vegetative lodging.",
        "pest_disease_information": "Pests: Girdle beetle, Spodoptera litura, Whitefly. Diseases: Yellow Mosaic Virus (YMV), Charcoal rot. Rogue out YMV-infected plants early to check whitefly vectors.",
        "harvesting_information": "Harvest when 90% leaves turn yellow and drop, and pods make a rattling sound when shaken. Thresh at optimum moisture (12-14%) to avoid seed coat cracking.",
        "source_name": "ICAR - Indian Institute of Soybean Research (IISR) Indore",
        "source_url": "https://iisrindore.icar.gov.in/",
    },
    {
        "crop_name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "description": "Wheat is the premier Rabi cereal staple crop in India, widely grown in the Indo-Gangetic plains, Punjab, Haryana, UP, and central India.",
        "soil_requirements": "Well-drained fertile loam or clay loam soils with balanced organic matter. Tolerates neutral to mildly alkaline soils (pH 6.5 to 8.2).",
        "climate_requirements": "Cool winter growing season with bright sunshine followed by warm dry weather at grain ripening. Ideal temperature: 20-25°C for germination, 15-20°C for tillering.",
        "sowing_information": "Timely sowing: November 1 to November 25. Seed rate: 40-45 kg/acre for timely sown, 50-55 kg/acre for late sown. Row spacing: 20-22.5 cm with depth 4-5 cm.",
        "irrigation_information": "Requires 4-6 irrigations. The Crown Root Initiation (CRI) stage at 20-25 DAS is the most critical; missing CRI irrigation causes up to 30% yield loss.",
        "nutrient_management": "Recommended N:P:K 120:60:40 kg/ha. Apply full P and K + 1/3 N as basal dose. Apply remaining N in two equal top-dressings at 1st and 2nd irrigation.",
        "pest_disease_information": "Key diseases: Yellow (stripe) rust, Brown (leaf) rust, Loose smut, Karnal bunt. Pests: Aphids, Armyworm. Cultivate certified resistant varieties (e.g. DBW, HD series).",
        "harvesting_information": "Harvest when straw turns yellow and brittle and grains contain less than 15% moisture. Combine harvester or manual sickle cutting followed by mechanical threshing.",
        "source_name": "ICAR - Indian Institute of Wheat and Barley Research (IIWBR) Karnal",
        "source_url": "https://iiwbr.icar.gov.in/",
    },
    {
        "crop_name": "Rice (Paddy)",
        "scientific_name": "Oryza sativa",
        "description": "Rice is India's principal staple cereal, cultivated widely during Kharif (monsoon) across eastern, southern, and northern canal/tube-well irrigated belts.",
        "soil_requirements": "Deep, heavy clay or clay-loam soils capable of holding standing water. pH range 5.5 to 7.0.",
        "climate_requirements": "Hot and humid climate with abundant sunlight and assured water supply. Temperature range 22°C to 34°C during growing season.",
        "sowing_information": "Nursery sowing: May - June; Transplanting 20-25 day old seedlings in puddled field in July. Spacing: 20 cm x 15 cm with 2-3 seedlings per hill.",
        "irrigation_information": "Maintain 2-5 cm shallow standing water during tillering and panicle initiation. Alternate wetting and drying (AWD) can save 20-25% water without yield reduction.",
        "nutrient_management": "Recommended N:P:K 100:50:50 kg/ha. Apply zinc sulphate 25 kg/ha basal to avoid Khaira disease. Top-dress nitrogen at tillering and panicle emergence.",
        "pest_disease_information": "Pests: Brown Plant Hopper (BPH), Stem Borer, Leaf Folder. Diseases: Bacterial Leaf Blight, Blast, Sheath Blight. Avoid excessive urea which aggravates blast and BPH.",
        "harvesting_information": "Harvest when 80-85% grains in panicles turn golden yellow. Drain water 7-10 days before harvesting. Dry grain down to 14% moisture before milling/storage.",
        "source_name": "ICAR - National Rice Research Institute (NRRI) Cuttack",
        "source_url": "https://icar-nrri.gov.in/",
    },
    {
        "crop_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "description": "Tomato is a premier vegetable cash crop grown year-round across Maharashtra, Karnataka, Andhra Pradesh, and Madhya Pradesh.",
        "soil_requirements": "Well-drained sandy loam to clay loam rich in organic matter. pH 6.0 to 7.0. Very sensitive to waterlogging.",
        "climate_requirements": "Warm season crop. Optimum day temperature 21-26°C. Temperatures above 35°C lead to flower drop and poor fruit set.",
        "sowing_information": "Seed rate: 60-80 g/acre for hybrid varieties. Raise seedlings in pro-trays under shade net; transplant 25-30 day old seedlings on raised beds with mulching.",
        "irrigation_information": "Drip irrigation with fertigation is strongly recommended. Regular, uniform moisture is necessary to prevent blossom end rot and fruit cracking.",
        "nutrient_management": "Apply 15-20 tonnes/ha FYM. Recommended N:P:K 150:100:100 kg/ha applied through fertigation schedule across vegetative, flowering, and fruiting phases.",
        "pest_disease_information": "Pests: Tuta absoluta, Whiteflies, Fruit borer (Helicoverpa). Diseases: Early blight, Late blight, Leaf curl virus, Bacterial wilt. Stake plants to keep fruit off soil.",
        "harvesting_information": "Harvest at turning / pink stage for distant markets; red ripe stage for local processing. Pick fruits carefully with pedicel intact in morning or late afternoon.",
        "source_name": "ICAR - Indian Institute of Horticultural Research (IIHR) Bengaluru",
        "source_url": "https://www.iihr.res.in/",
    },
    {
        "crop_name": "Onion",
        "scientific_name": "Allium cepa",
        "description": "Onion is an indispensable commercial bulb vegetable crop grown in Kharif, Late Kharif, and Rabi seasons, with Maharashtra producing over 35% of national output.",
        "soil_requirements": "Deep, well-drained friable sandy loam to clay loam soils with high organic matter, pH 6.5 to 7.5.",
        "climate_requirements": "Cool mild climate during initial vegetative growth (13-24°C) and higher temperature (30-35°C) with dry sunny weather during bulb development and maturity.",
        "sowing_information": "Seed rate: 3-4 kg/acre. Transplant 6-7 week old healthy seedlings on raised broad beds (BBF) at 15 cm x 10 cm spacing.",
        "irrigation_information": "Frequent light irrigations at 7-10 day intervals. Stop irrigation 10-15 days prior to harvest to allow outer scale drying and enhance keeping quality.",
        "nutrient_management": "Apply 10 tonnes FYM/acre + N:P:K 40:20:25 kg/acre + 15 kg Sulphur/acre. Sulphur is essential for pungent flavor and storage firmness.",
        "pest_disease_information": "Pests: Thrips (Thrips tabaci) causing silvering of leaves. Diseases: Purple blotch (Alternaria porri), Stemphylium blight, Basal rot. Use blue sticky traps for thrips.",
        "harvesting_information": "Harvest when 50% tops fall down (neck fall). Field cure for 3-5 days in shade followed by proper neck clipping leaving 2-3 cm attached to bulb.",
        "source_name": "ICAR - Directorate of Onion and Garlic Research (DOGR) Rajgurunagar",
        "source_url": "https://dogr.icar.gov.in/",
    },
    {
        "crop_name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "description": "Sugarcane is a major long-duration commercial agro-industrial cash crop supporting millions of farmers and sugar/ethanol mills in Maharashtra, UP, and Karnataka.",
        "soil_requirements": "Deep, fertile, well-drained medium-black to loamy soils with good drainage, depth >= 1 meter, and pH 6.5 - 8.0.",
        "climate_requirements": "Tropical to sub-tropical climate. Requires high temperature (28-35°C) and high humidity during elongation stage, and cool sunny weather during maturity.",
        "sowing_information": "Planting seasons: Adsali (July-Aug), Pre-seasonal (Oct-Nov), Suru (Jan-Feb). Use 2-bud setts (25,000-30,000 setts/ha) or single-eye budlings at 4-5 ft row spacing.",
        "irrigation_information": "Water requirement: 2000-2500 mm. Drip irrigation / subsurface drip saves up to 50% water and significantly improves cane weight and sugar recovery.",
        "nutrient_management": "Apply 250-400 kg N, 115-170 kg P2O5, and 115-170 kg K2O per hectare in split applications corresponding to germination, tillering, and grand growth phases.",
        "pest_disease_information": "Pests: Early shoot borer, Top borer, Pyrilla, White grub. Diseases: Red rot, Smut, Grassy shoot disease. Practice sett treatment before planting.",
        "harvesting_information": "Harvest at peak maturity when brix reading reaches 19-21% using hand refractometer. Cut cane flush with ground level where sucrose concentration is highest.",
        "source_name": "Vasantdada Sugar Institute (VSI) Pune & ICAR - IISR Lucknow",
        "source_url": "https://www.vsisugar.com/",
    },
    {
        "crop_name": "Maize (Corn)",
        "scientific_name": "Zea mays",
        "description": "Maize is a versatile high-yielding cereal crop cultivated for food, poultry feed, starch industry, and silage across Karnataka, MP, Maharashtra, and Bihar.",
        "soil_requirements": "Deep, fertile, well-drained loamy soils rich in organic matter, pH 6.0 to 7.5. Highly intolerant of water stagnation.",
        "climate_requirements": "Warm climate with daytime temperatures 21-30°C. Adequate warmth and sunshine are vital from germination through grain filling.",
        "sowing_information": "Kharif sowing: June - July; Rabi sowing: October - November. Seed rate: 7-8 kg/acre for hybrids. Spacing: 60 cm x 20 cm.",
        "irrigation_information": "Critical irrigation stages: Knee-high stage, tasseling, silking, and dough stage. Moisture stress at tasseling and silking drastically cuts cob yield.",
        "nutrient_management": "Recommended N:P:K 120:60:40 kg/ha + 25 kg Zinc sulphate/ha. Apply 1/3 N + full P and K at sowing; remaining N split at knee-high and tasseling.",
        "pest_disease_information": "Pests: Fall Armyworm (Spodoptera frugiperda), Stem borer (Chilo partellus). Diseases: Maydis leaf blight, Turcicum leaf blight. Monitor whorls for FAW pinholes.",
        "harvesting_information": "Harvest when outer cob sheaths dry to light brown and a black layer forms at the grain base (physiological maturity). Moisture should be <= 20% at harvest.",
        "source_name": "ICAR - Indian Institute of Maize Research (IIMR) Ludhiana",
        "source_url": "https://iimr.icar.gov.in/",
    },
    {
        "crop_name": "Gram (Chana / Chickpea)",
        "scientific_name": "Cicer arietinum",
        "description": "Gram (Chickpea) is India's leading Rabi pulse crop, fixing atmospheric nitrogen and contributing significantly to farmer soil health and pulse production.",
        "soil_requirements": "Well-drained medium to heavy black soils or alluvial loams. Tolerates dry conditions but cannot endure waterlogging or salinity.",
        "climate_requirements": "Cool, dry Rabi climate. Ideal temperature 18-26°C. Excessive rains or cloudiness during flowering causes massive flower drop.",
        "sowing_information": "Sow from October 15 to November 15. Seed rate: 25-30 kg/acre for Desi; 35-40 kg/acre for Kabuli varieties. Treat with Trichoderma and Rhizobium culture.",
        "irrigation_information": "Generally grown on conserved residual soil moisture. If irrigation is available, apply 1-2 light waterings at pre-flowering (40-45 DAS) and pod development (65-70 DAS).",
        "nutrient_management": "Recommended N:P:K 20:50:20 kg/ha + 20 kg Sulphur/ha as basal dose. Being a legume, it fixes nitrogen; do not apply excessive urea.",
        "pest_disease_information": "Pests: Gram pod borer (Helicoverpa armigera). Diseases: Fusarium wilt, Dry root rot, Ascochyta blight. Install pheromone traps and spray botanical neem or NPV.",
        "harvesting_information": "Harvest when leaves turn reddish-brown and dry out completely, and pods rattle when shaken. Avoid over-drying in the field to minimize shattering.",
        "source_name": "ICAR - Indian Institute of Pulses Research (IIPR) Kanpur",
        "source_url": "https://iipr.icar.gov.in/",
    },
]

KNOWLEDGE_DOCUMENTS_DATA = [
    {
        "title": "Integrated Pest Management (IPM) for Pink Bollworm in Cotton",
        "topic": "pest_management",
        "language": "en",
        "source_name": "ICAR-CICR Advisory Bulletin 2026",
        "source_url": "https://cicr.icar.gov.in/",
        "content": (
            "Pink bollworm (Pectinophora gossypiella) has developed resistance to older Cry toxins in Bt cotton. "
            "Effective IPM strategies include: 1) Strictly avoid planting off-season or summer cotton to break pest lifecycle. "
            "2) Install 5 pheromone traps per acre at 45 days after sowing for regular monitoring. "
            "3) When trap catches exceed 8 moths/trap/night for 3 consecutive days, trigger ETL threshold actions. "
            "4) Handpick and destroy rosetted flowers. "
            "5) Release Trichogramma egg parasitoids at weekly intervals. "
            "6) Never apply unapproved pesticide cocktails. Always consult your district KVK."
        ),
    },
    {
        "title": "Soil Health Card Nutrient Calculation and Balanced Fertilizer Management",
        "topic": "soil_health",
        "language": "en",
        "source_name": "Ministry of Agriculture & Farmers Welfare, GoI",
        "source_url": "https://soilhealth.dac.gov.in/",
        "content": (
            "Over-reliance on urea (Nitrogen) degrades soil microbial activity and leads to soil acidification or salinity. "
            "The Soil Health Card evaluates 12 parameters: Macro-nutrients (N, P, K), Secondary nutrient (S), "
            "Micro-nutrients (Zn, Fe, Cu, Mn, Bo), and Physical parameters (pH, EC, Organic Carbon). "
            "For optimal crop uptake: Apply bulky organic manure (FYM or compost) at 2-3 tonnes/acre before sowing. "
            "Apply phosphorus and potassium as basal placement near the root zone. Split nitrogen applications into 2-3 stages "
            "to maximize Nitrogen Use Efficiency (NUE) and prevent groundwater leaching."
        ),
    },
    {
        "title": "Water-Saving Micro-Irrigation (Drip & Sprinkler) Operational Guidelines",
        "topic": "irrigation",
        "language": "en",
        "source_name": "PM Krishi Sinchayee Yojana Guidelines",
        "source_url": "https://pmksy.gov.in/",
        "content": (
            "Micro-irrigation achieves 85-90% water application efficiency compared to 35-40% under traditional flood irrigation. "
            "Best operational practices: 1) Clean screen and disc filters weekly to prevent emitter clogging. "
            "2) Flush sub-mains and lateral lines every fortnight by opening end flush valves. "
            "3) Irrigate based on crop water requirements according to stage rather than running pumps continuously. "
            "4) Combine drip with water-soluble fertigation to save 25-30% fertilizer expense."
        ),
    },
    {
        "title": "Safe Handling of Plant Protection Chemicals and Farmer Health Safeguards",
        "topic": "agricultural_safety",
        "language": "en",
        "source_name": "ICAR Farmer Safety Advisory",
        "source_url": "https://icar.org.in/",
        "content": (
            "Farmer safety when handling chemical pesticides and fungicides: "
            "1) Always wear Personal Protective Equipment (PPE): mask, gloves, goggles, and full-sleeve apron. "
            "2) Never spray pesticides against the wind direction. "
            "3) Do not eat, drink, or smoke while preparing chemical spray solutions. "
            "4) Never use mouth to clear blocked spray nozzles; use a thin wire or water wash. "
            "5) Observe Pre-Harvest Intervals (PHI) strictly before picking vegetables or fruits for sale. "
            "6) Triple rinse empty pesticide containers, puncture them, and dispose of them safely away from water bodies."
        ),
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY) Crop Loss Claim Procedure",
        "topic": "government_schemes",
        "language": "en",
        "source_name": "PMFBY Official Operational Guidelines",
        "source_url": "https://pmfby.gov.in/",
        "content": (
            "In case of localized natural calamities (hailstorm, landslide, inundation, cloudburst, unseasonal excessive rain): "
            "The affected insured farmer must report the crop loss within 72 hours through the 'Crop Insurance App' (Krishi Rakshak), "
            "or contact the designated insurance company toll-free number or bank/agriculture office. "
            "Include farmer policy number, crop name, survey number, and geotagged photograph of inundated field for expeditious survey and claim settlement."
        ),
    },
    {
        "title": "पिकांवरील कीड व रोग नियंत्रण: शेतकरी मार्गदर्शक सूचना",
        "topic": "pest_management",
        "language": "mr",
        "source_name": "महात्मा फुले कृषी विद्यापीठ (राहुरी) कृषी सल्ला",
        "source_url": "https://mpkv.ac.in/",
        "content": (
            "कीड व्यवस्थापनासाठी एकात्मिक कीड व्यवस्थापन (IPM) पद्धतीचा अवलंब करा. "
            "रासायनिक कीटकनाशकांचा बेसुमार वापर टाळावा. सुरुवातीच्या काळात निंबोळी अर्क (५%) किंवा ५ मिली निमतेल प्रति लिटर पाण्यात मिसळून फवारणी करावी. "
            "रसशोषक किडींसाठी पिवळे व निळे चिकट सापळे एकरी १५ ते २० लावावेत. "
            "कोणत्याही कीटकनाशकाचा वापर करण्यापूर्वी स्थानिक कृषी सहाय्यक किंवा कृषी विज्ञान केंद्र (KVK) च्या शास्त्रज्ञांचा सल्ला घ्यावा."
        ),
    },
    {
        "title": "फसलों में एकीकृत पोषक तत्व एवं खाद प्रबंधन",
        "topic": "soil_health",
        "language": "hi",
        "source_name": "भारतीय कृषि अनुसंधान परिषद (ICAR) नई दिल्ली",
        "source_url": "https://icar.org.in/",
        "content": (
            "रासायनिक खादों का असंतुलित उपयोग जमीन की उपजाऊ क्षमता को घटाता है। "
            "मृदा स्वास्थ्य कार्ड (Soil Health Card) की रिपोर्ट के आधार पर ही यूरिया, डीएपी और पोटाश का संतुलित प्रयोग करें। "
            "बुवाई से पूर्व प्रति एकड़ 2-3 टन अच्छी सड़ी गोबर की खाद या केंचुआ खाद मिलाएं। "
            "दालों और तिलहनों में बीज को राइजोबियम और ट्राइकोडर्मा से उपचारित करके ही बोएं।"
        ),
    },
]


def seed_database():
    """Seed crop knowledge and documents into database."""
    init_db()
    with get_db() as db:
        # Seed Crops Knowledge
        for c_data in CROPS_KNOWLEDGE_DATA:
            existing = db.query(CropKnowledge).filter(CropKnowledge.crop_name == c_data["crop_name"]).first()
            if not existing:
                ck = CropKnowledge(
                    crop_name=c_data["crop_name"],
                    scientific_name=c_data["scientific_name"],
                    description=c_data["description"],
                    soil_requirements=c_data["soil_requirements"],
                    climate_requirements=c_data["climate_requirements"],
                    sowing_information=c_data["sowing_information"],
                    irrigation_information=c_data["irrigation_information"],
                    nutrient_management=c_data["nutrient_management"],
                    pest_disease_information=c_data["pest_disease_information"],
                    harvesting_information=c_data["harvesting_information"],
                    source_name=c_data["source_name"],
                    source_url=c_data["source_url"],
                    verification_status="Verified",
                )
                db.add(ck)
                logger.info(f"Seeded Crop Knowledge: {c_data['crop_name']}")

        # Seed Knowledge Documents for RAG
        for doc in KNOWLEDGE_DOCUMENTS_DATA:
            existing_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.title == doc["title"]).first()
            if not existing_doc:
                kd = KnowledgeDocument(
                    title=doc["title"],
                    topic=doc["topic"],
                    language=doc["language"],
                    source_name=doc["source_name"],
                    source_url=doc["source_url"],
                    content=doc["content"],
                    verification_status="Verified",
                )
                db.add(kd)
                logger.info(f"Seeded Knowledge Document: {doc['title']}")

        db.commit()
    print("Database knowledge seed completed successfully.")


if __name__ == "__main__":
    seed_database()

