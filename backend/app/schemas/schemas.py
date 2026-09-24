"""Pydantic schemas — API request/response models."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.core.disclaimer import AI_DISCLAIMER


# --- Auth ---

class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


# --- Companies ---

class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    industry: str | None = None
    country: str | None = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    description: str | None
    industry: str | None
    country: str | None
    maturity: float
    status: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Projects ---

class ProjectResponse(BaseModel):
    id: str
    company_id: str
    name: str
    status: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Levels ---

class LevelResponse(BaseModel):
    id: str
    project_id: str
    number: int
    name: str
    status: str
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# --- Cards ---

class CardResponse(BaseModel):
    id: str
    level_id: str
    title: str
    description: str | None
    card_type: str
    status: str

    model_config = {"from_attributes": True}


# --- Conversations ---

class ConversationResponse(BaseModel):
    id: str
    card_id: str
    title: str | None
    status: str
    summary: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    agent_name: str | None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Scores ---

class ScoreResponse(BaseModel):
    id: str
    project_id: str
    score_type: str
    value: float
    confidence_level: float
    reasoning: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Decisions ---

class DecisionResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str | None
    proposed_by: str | None
    status: str
    reasoning: str | None
    confidence_level: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionAction(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")


# --- Documents ---

class DocumentResponse(BaseModel):
    id: str
    project_id: str
    title: str
    content: str | None
    doc_type: str
    origin: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Chat ---

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    message: MessageResponse
    conversation_id: str
    card_id: str | None = None
    disclaimer: str = AI_DISCLAIMER


# --- Dashboard ---

class DashboardResponse(BaseModel):
    company: CompanyResponse | None
    project: ProjectResponse | None
    current_level: LevelResponse | None
    scores: list[ScoreResponse]
    recent_decisions: list[DecisionResponse]
    progress: dict  # {completed_levels: int, total_levels: 7}


# --- Gate Review ---

class GateReviewRequest(BaseModel):
    level_number: int


class GateReviewResponse(BaseModel):
    approved: bool
    scores: list[ScoreResponse]
    decisions: list[DecisionResponse]
    level_status: str
    message: str
    disclaimer: str = AI_DISCLAIMER
