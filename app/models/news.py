from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field, field_validator


class NewsStatus(str, Enum):
    """Status possíveis para uma notícia"""

    DRAFT = "draft"
    PUBLISHED = "published"


class NewsBase(BaseModel):
    """Campos base compartilhados entre modelos"""

    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    status: NewsStatus = NewsStatus.DRAFT

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Valida formato do slug"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug deve conter apenas letras, números e hífens")
        return v.lower()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Remove tags vazias e duplicadas"""
        return list(set(tag.strip().lower() for tag in v if tag.strip()))


class News(NewsBase):
    """Modelo completo de notícia (leitura do banco)"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    published_at_fmt: Optional[str] = None  # Campo calculado para exibição

    class Config:
        from_attributes = True
        use_enum_values = True  # Converte enum para string

    def format_published_date(self) -> None:
        """Formata data de publicação para exibição"""
        if self.published_at:
            self.published_at_fmt = self.published_at.strftime("%d/%m/%Y")


class NewsCreate(NewsBase):
    """Modelo para criar nova notícia"""

    published_at: Optional[datetime] = None

    @field_validator("published_at")
    @classmethod
    def validate_published_consistency(
        cls, v: Optional[datetime], values
    ) -> Optional[datetime]:
        """Valida consistência entre status e published_at"""
        status = values.data.get("status")

        if status == NewsStatus.DRAFT and v is not None:
            raise ValueError(
                "Notícia em rascunho não pode ter data de publicação"
            )
        if status == NewsStatus.PUBLISHED and v is None:
            # Se publicada mas sem data, define como agora
            return datetime.now()
        return v


class NewsUpdate(BaseModel):
    """Modelo para atualizar notícia (todos os campos opcionais)"""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    status: Optional[NewsStatus] = None
    published_at: Optional[datetime] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug deve conter apenas letras, números e hífens")
        return v.lower() if v else None

    @field_validator("tags")
    @classmethod
    def validate_tags(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        if v is not None:
            return list(set(tag.strip().lower() for tag in v if tag.strip()))
        return None


class NewsListItem(BaseModel):
    """Modelo simplificado para listagem de notícias"""

    id: uuid.UUID
    title: str
    slug: str
    summary: str
    tags: List[str]
    status: NewsStatus
    published_at: Optional[datetime] = None
    published_at_fmt: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True

    def format_published_date(self) -> None:
        """Formata data de publicação para exibição"""
        if self.published_at:
            self.published_at_fmt = self.published_at.strftime("%d/%m/%Y")


class NewsDetail(News):
    """Modelo completo para exibição de detalhes"""
    pass


class NewsPublish(BaseModel):
    """Modelo para publicar uma notícia"""

    published_at: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True
