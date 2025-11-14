__version__ = "1.0.0"

from app.main import app, GlossaryDatabase, GlossaryTerm, GlossaryTermCreate

__all__ = [
    "app",
    "GlossaryDatabase",
    "GlossaryTerm",
    "GlossaryTermCreate",
]
