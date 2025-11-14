from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# ==================== Pydantic Models ====================

class GlossaryTermBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Название термина")
    definition: str = Field(..., min_length=10, max_length=2000, description="Определение термина")
    category: str = Field(default="General", description="Категория термина")
    examples: Optional[list[str]] = Field(None, description="Примеры использования")
    related_terms: Optional[list[str]] = Field(None, description="Связанные термины")
    source: Optional[str] = Field(None, description="Источник определения")


class GlossaryTermCreate(GlossaryTermBase):
    pass


class GlossaryTermUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    definition: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = None
    examples: Optional[list[str]] = None
    related_terms: Optional[list[str]] = None
    source: Optional[str] = None


class GlossaryTerm(GlossaryTermBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None


DATA_FILE = Path(__file__).parent / "glossary_data.json"


class GlossaryDatabase:
    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath
        self.data = self._load_data()
        self.next_id = self._get_next_id()

    def _load_data(self) -> dict:
        """Загрузить данные из JSON файла"""
        if self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"glossary": []}

    def _save_data(self):
        """Сохранить данные в JSON файл"""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _get_next_id(self) -> int:
        """Получить следующий ID"""
        if not self.data["glossary"]:
            return 1
        return max(term["id"] for term in self.data["glossary"]) + 1

    def get_all(self) -> list:
        """Получить все термины"""
        return self.data["glossary"]

    def get_by_id(self, term_id: int) -> Optional[dict]:
        """Получить термин по ID"""
        for term in self.data["glossary"]:
            if term["id"] == term_id:
                return term
        return None

    def search(self, keyword: str) -> list:
        """Поиск по ключевому слову"""
        keyword_lower = keyword.lower()
        results = []
        for term in self.data["glossary"]:
            if (keyword_lower in term["title"].lower() or
                keyword_lower in term["definition"].lower() or
                (term.get("category") and keyword_lower in term["category"].lower())):
                results.append(term)
        return results

    def create(self, term_data: GlossaryTermCreate) -> dict:
        """Создать новый термин"""
        new_term = {
            "id": self.next_id,
            "title": term_data.title,
            "definition": term_data.definition,
            "category": term_data.category,
            "examples": term_data.examples or [],
            "related_terms": term_data.related_terms or [],
            "source": term_data.source or "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.data["glossary"].append(new_term)
        self.next_id += 1
        self._save_data()
        return new_term

    def update(self, term_id: int, term_data: GlossaryTermUpdate) -> Optional[dict]:
        term = self.get_by_id(term_id)
        if not term:
            return None

        update_data = term_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                term[key] = value

        term["updated_at"] = datetime.now().isoformat()
        self._save_data()
        return term

    def delete(self, term_id: int) -> bool:
        for i, term in enumerate(self.data["glossary"]):
            if term["id"] == term_id:
                self.data["glossary"].pop(i)
                self._save_data()
                return True
        return False


db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    db = GlossaryDatabase()
    yield


app = FastAPI(
    title="Glossary API - Децентрализованные Приложения",
    description="API для управления глоссарием терминов по разработке DApps",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "Glossary API",
        "version": "1.0.0",
        "description": "API для управления глоссарием терминов DApps",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/glossary", response_model=GlossaryResponse, tags=["Glossary"])
async def get_all_terms(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    all_terms = db.get_all()
    paginated_terms = all_terms[skip:skip + limit]

    return GlossaryResponse(
        success=True,
        message=f"Получено {len(paginated_terms)} терминов из {len(all_terms)} всего",
        data={
            "total": len(all_terms),
            "skip": skip,
            "limit": limit,
            "items": paginated_terms
        }
    )


@app.get("/api/glossary/{term_id}", response_model=GlossaryResponse, tags=["Glossary"])
async def get_term(term_id: int):
    term = db.get_by_id(term_id)
    if not term:
        raise HTTPException(
            status_code=404,
            detail=f"Термин с ID {term_id} не найден"
        )

    return GlossaryResponse(
        success=True,
        message="Термин найден",
        data=term
    )


@app.get("/api/glossary/search/{keyword}", response_model=GlossaryResponse, tags=["Glossary"])
async def search_terms(keyword: str = Query(..., min_length=1, max_length=100)):

    results = db.search(keyword)

    return GlossaryResponse(
        success=True,
        message=f"Найдено {len(results)} терминов",
        data=results
    )


@app.post("/api/glossary", response_model=GlossaryResponse, status_code=201, tags=["Glossary"])
async def create_term(term: GlossaryTermCreate):

    new_term = db.create(term)

    return GlossaryResponse(
        success=True,
        message="Новый термин успешно добавлен",
        data=new_term
    )


@app.put("/api/glossary/{term_id}", response_model=GlossaryResponse, tags=["Glossary"])
async def update_term(term_id: int, term_update: GlossaryTermUpdate):

    updated_term = db.update(term_id, term_update)
    if not updated_term:
        raise HTTPException(
            status_code=404,
            detail=f"Термин с ID {term_id} не найден"
        )

    return GlossaryResponse(
        success=True,
        message="Термин успешно обновлен",
        data=updated_term
    )


@app.delete("/api/glossary/{term_id}", response_model=GlossaryResponse, tags=["Glossary"])
async def delete_term(term_id: int):
    success = db.delete(term_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Термин с ID {term_id} не найден"
        )

    return GlossaryResponse(
        success=True,
        message="Термин успешно удален",
        data={"deleted_id": term_id}
    )


@app.get("/api/statistics", response_model=GlossaryResponse, tags=["Info"])
async def get_statistics():
    all_terms = db.get_all()
    categories = {}

    for term in all_terms:
        category = term.get("category", "Unknown")
        categories[category] = categories.get(category, 0) + 1

    return GlossaryResponse(
        success=True,
        message="Статистика глоссария",
        data={
            "total_terms": len(all_terms),
            "categories": categories,
            "categories_count": len(categories)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
