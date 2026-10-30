"""Tests for Agricultural Knowledge Library and TF-IDF RAG retrieval."""

import pytest
from models.knowledge import CropKnowledge, KnowledgeDocument
from services.knowledge_service import KnowledgeService


@pytest.fixture
def seed_knowledge(db_session):
    # Add crop
    c1 = CropKnowledge(
        crop_name="Cotton",
        description="Cotton commercial fiber crop",
        soil_requirements="Black clay",
        climate_requirements="Warm",
        sowing_information="June-July",
        irrigation_information="Squaring and flowering",
        nutrient_management="100:50:50 NPK",
        pest_disease_information="Pink bollworm, whiteflies",
        harvesting_information="Pick fully opened clean bolls",
        source_name="ICAR-CICR",
        source_url="https://cicr.icar.gov.in/",
    )
    # Add document
    d1 = KnowledgeDocument(
        title="Pink Bollworm IPM Strategy",
        topic="pest_control",
        content="Install pheromone traps at 5 traps per acre to monitor pink bollworm in Bt cotton.",
        source_name="ICAR-CICR Advisory",
        source_url="https://cicr.icar.gov.in/",
        language="en",
    )
    d2 = KnowledgeDocument(
        title="Soybean Yellow Mosaic Virus",
        topic="disease_control",
        content="Soybean yellow mosaic is transmitted by whiteflies. Rogue out infected plants early.",
        source_name="ICAR-IISR",
        source_url="https://iisrindore.icar.gov.in/",
        language="en",
    )
    db_session.add_all([c1, d1, d2])
    db_session.commit()


def test_crop_knowledge_lookup(db_session, seed_knowledge):
    ck = KnowledgeService.get_crop_knowledge(db_session, "Cotton")
    assert ck is not None
    assert "Black clay" in ck.soil_requirements


def test_rag_tfidf_document_retrieval(db_session, seed_knowledge):
    # Query for pink bollworm trap
    docs = KnowledgeService.retrieve_relevant_documents(db_session, "pink bollworm pheromone trap", top_k=2)
    assert len(docs) >= 1
    assert docs[0]["title"] == "Pink Bollworm IPM Strategy"
    assert "ICAR-CICR" in docs[0]["source_name"]


def test_empty_query_retrieval(db_session, seed_knowledge):
    docs = KnowledgeService.retrieve_relevant_documents(db_session, "")
    assert docs == []

