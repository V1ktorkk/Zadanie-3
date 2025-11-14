import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, GlossaryDatabase

client = TestClient(app)


@pytest.fixture
def test_db(tmp_path):
    test_file = tmp_path / "test_glossary.json"
    test_file.write_text(json.dumps({
        "glossary": [
            {
                "id": 1,
                "title": "Test Term",
                "definition": "This is a test definition for testing purposes",
                "category": "Test",
                "examples": ["example1"],
                "related_terms": [],
                "source": "test",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
    }))
    return GlossaryDatabase(test_file)


class TestHealthCheck:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert response.json()["name"] == "Glossary API"


class TestGetAllTerms:
    def test_get_all_terms(self):
        response = client.get("/api/glossary")
        assert response.status_code == 200
        assert "success" in response.json()
        assert response.json()["success"] == True

    def test_get_all_terms_pagination(self):
        response = client.get("/api/glossary?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data["data"]
        assert "items" in data["data"]


class TestCreateTerm:
    def test_create_valid_term(self):
        new_term = {
            "title": "Test DApp Term",
            "definition": "This is a comprehensive test definition for a new DApp related term",
            "category": "Test Category",
            "examples": ["example1", "example2"],
            "related_terms": ["term1", "term2"]
        }
        response = client.post("/api/glossary", json=new_term)
        assert response.status_code == 201
        assert response.json()["success"] == True
        assert response.json()["data"]["title"] == new_term["title"]

    def test_create_term_invalid_title(self):
        invalid_term = {
            "title": "",
            "definition": "This is a test definition but title is invalid"
        }
        response = client.post("/api/glossary", json=invalid_term)
        assert response.status_code == 422

    def test_create_term_short_definition(self):
        invalid_term = {
            "title": "Short",
            "definition": "Short"
        }
        response = client.post("/api/glossary", json=invalid_term)
        assert response.status_code == 422


class TestSearchTerms:
    def test_search_existing_term(self):
        response = client.get("/api/glossary/search/DApp")
        assert response.status_code == 200
        assert response.json()["success"] == True

    def test_search_empty_keyword(self):
        response = client.get("/api/glossary/search/")
        assert response.status_code == 422


class TestUpdateTerm:
    def test_update_existing_term(self):
        response = client.get("/api/glossary?limit=1")
        if response.json()["data"]["items"]:
            term_id = response.json()["data"]["items"][0]["id"]
            update_data = {
                "definition": "Updated test definition with more comprehensive information"
            }
            response = client.put(f"/api/glossary/{term_id}", json=update_data)
            assert response.status_code == 200
            assert response.json()["success"] == True

    def test_update_nonexistent_term(self):
        update_data = {
            "definition": "Updated definition that should not be applied"
        }
        response = client.put("/api/glossary/99999", json=update_data)
        assert response.status_code == 404


class TestDeleteTerm:
    def test_delete_nonexistent_term(self):
        response = client.delete("/api/glossary/99999")
        assert response.status_code == 404
        assert response.json()["success"] == False


class TestStatistics:
    def test_get_statistics(self):
        response = client.get("/api/statistics")
        assert response.status_code == 200
        assert response.json()["success"] == True
        data = response.json()["data"]
        assert "total_terms" in data
        assert "categories" in data
        assert "categories_count" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
