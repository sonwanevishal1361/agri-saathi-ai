"""Government Agricultural Schemes service providing verified information and official portals."""

from typing import List, Dict, Any, Optional

VERIFIED_GOVERNMENT_SCHEMES: List[Dict[str, Any]] = [
    {
        "id": "pm-kisan",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "hindi_name": "प्रधानमंत्री किसान सम्मान निधि",
        "marathi_name": "प्रधानमंत्री किसान सन्मान निधी",
        "category": "Income Support",
        "scope": "National (Central Sector Scheme)",
        "description": (
            "A central sector scheme providing income support to landholding farmer families across India "
            "to supplement financial needs for agricultural inputs and domestic obligations."
        ),
        "benefits_summary": (
            "Financial benefit of Rs 6,000 per year transferred directly into Aadhaar-linked bank accounts "
            "in three equal 4-monthly installments of Rs 2,000 each (DBT)."
        ),
        "eligibility_summary": (
            "All landholding farmer families with cultivable land in their names. Exclusions apply for "
            "institutional landholders, serving/retired government employees, income tax payees, and professionals."
        ),
        "application_process": (
            "Apply online at the official PM-KISAN portal via 'New Farmer Registration' with Aadhaar card, "
            "land ownership documents (7/12 extract / RoR), and active bank account details, or via local CSC / Village Revenue Officer."
        ),
        "official_url": "https://pmkisan.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "pmfby",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "hindi_name": "प्रधानमंत्री फसल बीमा योजना",
        "marathi_name": "प्रधानमंत्री पीक विमा योजना",
        "category": "Crop Insurance",
        "scope": "National / State Implemented",
        "description": (
            "Comprehensive crop insurance scheme protecting farmers against non-preventable natural risks, "
            "pests, diseases, localized calamities, post-harvest losses, and unseasonal rainfall."
        ),
        "benefits_summary": (
            "Subsidized crop insurance. Maximum premium paid by farmer is 2% for Kharif food/oilseed crops, "
            "1.5% for Rabi food/oilseed crops, and 5% for commercial/horticultural crops. Balance subsidized by Central & State governments."
        ),
        "eligibility_summary": (
            "All farmers growing notified crops in notified areas, including sharecroppers and tenant farmers. "
            "Voluntary for all farmers."
        ),
        "application_process": (
            "Enroll through PMFBY national portal, NCIP portal, designated banks, or Common Service Centers (CSCs) "
            "before the cut-off date for each crop season with sowing certificate and land records."
        ),
        "official_url": "https://pmfby.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "shc",
        "name": "Soil Health Card Scheme (SHC)",
        "hindi_name": "मृदा स्वास्थ्य कार्ड योजना",
        "marathi_name": "मृदा आरोग्य पत्रिका योजना",
        "category": "Soil & Nutrients",
        "scope": "National",
        "description": (
            "Assists State Governments to issue Soil Health Cards to all farmers in the country, detailing the nutrient "
            "status of their soil along with recommendations on appropriate dosage of fertilizers and soil amendments."
        ),
        "benefits_summary": (
            "Provides customized soil test reports covering 12 vital parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) "
            "helping farmers reduce excessive fertilizer expenses and restore soil health."
        ),
        "eligibility_summary": "All agricultural landholders across India.",
        "application_process": (
            "Soil samples are collected by agriculture department field staff from GPS-tagged sample grids, "
            "analyzed in authorized testing laboratories, and results dispatched online."
        ),
        "official_url": "https://soilhealth.dac.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "pmksy",
        "name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY - Per Drop More Crop)",
        "hindi_name": "प्रधानमंत्री कृषि सिंचाई योजना",
        "marathi_name": "प्रधानमंत्री कृषी सिंचन योजना",
        "category": "Micro-Irrigation & Water",
        "scope": "National / State Implemented",
        "description": (
            "Promotes micro-irrigation technologies (drip and sprinkler systems) to maximize water use efficiency "
            "under the 'Per Drop More Crop' initiative."
        ),
        "benefits_summary": (
            "Subsidies on installation of drip and sprinkler irrigation units (typically 45% to 55% subsidy depending on "
            "farmer category—small/marginal vs other—as per state operational guidelines)."
        ),
        "eligibility_summary": (
            "Farmers possessing cultivable land with an assured water source (well, borewell, canal, farm pond)."
        ),
        "application_process": (
            "Apply through respective State Agriculture / Horticulture department portals (e.g. Mahadbt in Maharashtra) "
            "with land revenue records, water source certificate, and quotation from empaneled micro-irrigation manufacturers."
        ),
        "official_url": "https://pmksy.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card (KCC)",
        "hindi_name": "किसान क्रेडिट कार्ड",
        "marathi_name": "किसान क्रेडिट कार्ड",
        "category": "Credit & Loans",
        "scope": "National",
        "description": (
            "Provides timely, affordable institutional credit to farmers for crop cultivation, post-harvest expenses, "
            "working capital for allied activities (animal husbandry, dairy, fisheries), and farm maintenance."
        ),
        "benefits_summary": (
            "Concessional interest rate at 7% per annum for crop loans up to Rs 3 Lakhs, with an additional 3% "
            "prompt repayment incentive (effective interest rate becomes 4% per annum)."
        ),
        "eligibility_summary": (
            "Individual farmers, joint cultivators, tenant farmers, oral lessees, sharecroppers, and SHGs/JLGs."
        ),
        "application_process": (
            "Submit a simple 1-page KCC application form at nearest commercial bank branch, regional rural bank (RRB), "
            "or cooperative bank along with land records, Aadhaar, and identity proof."
        ),
        "official_url": "https://agriwelfare.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "enam",
        "name": "National Agriculture Market (e-NAM)",
        "hindi_name": "राष्ट्रीय कृषि बाजार (ई-नाम)",
        "marathi_name": "राष्ट्रीय कृषी बाजार (ई-नाम)",
        "category": "Market & Trading",
        "scope": "National",
        "description": (
            "Pan-India electronic trading portal networking existing APMC mandis to create a unified national market "
            "for agricultural commodities with transparent price discovery and online payment."
        ),
        "benefits_summary": (
            "Access to nationwide competitive buyers, electronic weighing, online assaying, and direct online settlement into farmer bank accounts."
        ),
        "eligibility_summary": "All farmers and licensed mandi traders.",
        "application_process": (
            "Register on the e-NAM mobile app or portal (enam.gov.in) with bank passbook and Aadhaar, or register at the entry gate "
            "of any designated e-NAM enabled APMC mandi."
        ),
        "official_url": "https://enam.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified Official Central Scheme",
    },
    {
        "id": "namo-shetkari",
        "name": "Namo Shetkari Mahasanman Nidhi Yojana (Maharashtra)",
        "hindi_name": "नमो शेतकरी महासन्मान निधी योजना",
        "marathi_name": "नमो शेतकरी महासन्मान निधी योजना",
        "category": "State Income Support",
        "scope": "Maharashtra",
        "description": (
            "State supplementary cash benefit program launched by the Government of Maharashtra to augment the income of state farmers."
        ),
        "benefits_summary": (
            "Additional Rs 6,000 per year from the Government of Maharashtra to eligible PM-KISAN beneficiaries, "
            "bringing total combined annual support to Rs 12,000 per eligible farmer family."
        ),
        "eligibility_summary": (
            "Farmers residing in Maharashtra who are approved and active beneficiaries of PM-KISAN with active Aadhaar-linked DBT accounts."
        ),
        "application_process": (
            "Automatic linkage for approved PM-KISAN beneficiaries in Maharashtra; monitor status on Mahadbt or PM-KISAN portal."
        ),
        "official_url": "https://mahadbt.maharashtra.gov.in/",
        "last_verified": "2026-10-15",
        "verification_status": "Verified State Scheme",
    },
]


class SchemesService:

    @staticmethod
    def get_all_schemes() -> List[Dict[str, Any]]:
        """Return all verified government schemes."""
        return VERIFIED_GOVERNMENT_SCHEMES

    @staticmethod
    def filter_schemes(
        search: Optional[str] = None,
        category: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter verified schemes by keyword, category, or scope."""
        results = VERIFIED_GOVERNMENT_SCHEMES

        if search:
            q = search.strip().lower()
            results = [
                s for s in results
                if q in s["name"].lower()
                or q in s.get("hindi_name", "").lower()
                or q in s.get("marathi_name", "").lower()
                or q in s["description"].lower()
                or q in s["category"].lower()
            ]

        if category and category != "All":
            results = [s for s in results if s["category"].lower() == category.lower()]

        if scope and scope != "All":
            results = [s for s in results if scope.lower() in s["scope"].lower()]

        return results

    @staticmethod
    def get_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
        """Lookup single verified scheme by its ID."""
        for s in VERIFIED_GOVERNMENT_SCHEMES:
            if s["id"] == scheme_id:
                return s
        return None

