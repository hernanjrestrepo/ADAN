"""
Tests para el Tool Execution Framework — WO-005.
"""

import pytest
import asyncio
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import User, Company, Project, Level
from app.ems.models import EMSBase
from app.tef.interfaces import ToolMetadata, ToolContext, ToolResult
from app.tef.registry import ToolRegistry
from app.tef.executor import ToolExecutor
from app.tef.tools import (
    CalculatorTool, FileReaderTool, HttpRequestTool,
    SqlQueryTool, PythonSandboxTool, EmailSenderTool,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    EMSBase.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def test_company(db_session):
    from app.core.auth import hash_password
    user = User(
        email="tef@test.com",
        name="TEF Tester",
        hashed_password=hash_password("test123"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    company = Company(
        name="TEF Test Corp",
        description="Test company for TEF",
        industry="technology",
        country="Argentina",
        maturity=0.5,
        primary_user_id=user.id,
        created_by=user.id,
    )
    db_session.add(company)
    db_session.commit()

    return company, user


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(CalculatorTool())
    reg.register(FileReaderTool())
    reg.register(HttpRequestTool())
    reg.register(PythonSandboxTool())
    reg.register(EmailSenderTool())
    return reg


@pytest.fixture
def executor(registry, db_session):
    return ToolExecutor(registry, db_session)


@pytest.fixture
def context(test_company):
    company, user = test_company
    return ToolContext(
        company_id=str(company.id),
        user_id=str(user.id),
        trace_id="test-trace-001",
    )


# ============================================================
# Tests: Registry
# ============================================================

class TestRegistry:
    def test_register_tool(self, registry):
        assert registry.count() == 5

    def test_get_tool(self, registry):
        tool = registry.get("calculator")
        assert tool is not None
        assert tool.metadata().id == "calculator"

    def test_get_nonexistent(self, registry):
        tool = registry.get("nonexistent")
        assert tool is None

    def test_list_all(self, registry):
        tools = registry.list_all()
        assert len(tools) == 5
        assert all(isinstance(t, ToolMetadata) for t in tools)

    def test_discover_by_query(self, registry):
        results = registry.discover("calcular número")
        assert len(results) > 0
        assert results[0].id == "calculator"

    def test_discover_by_category(self, registry):
        results = registry.list_by_category("computation")
        assert len(results) == 1
        assert results[0].id == "calculator"


# ============================================================
# Tests: Tools
# ============================================================

class TestCalculatorTool:
    @pytest.mark.asyncio
    async def test_calculate_simple(self, context):
        tool = CalculatorTool()
        result = await tool.execute({"expression": "2 + 2"}, context)
        assert result.status == "success"
        assert result.output["result"] == 4

    @pytest.mark.asyncio
    async def test_calculate_complex(self, context):
        tool = CalculatorTool()
        result = await tool.execute({"expression": "sqrt(144) + pi"}, context)
        assert result.status == "success"
        assert result.output["result"] > 13

    @pytest.mark.asyncio
    async def test_calculate_invalid(self, context):
        tool = CalculatorTool()
        result = await tool.execute({"expression": "import os"}, context)
        assert result.status == "error"

    def test_validate(self):
        tool = CalculatorTool()
        is_valid, error = tool.validate({"expression": "1+1"})
        assert is_valid is True

    def test_validate_missing_param(self):
        tool = CalculatorTool()
        is_valid, error = tool.validate({})
        assert is_valid is False
        assert "required" in error


class TestPythonSandboxTool:
    @pytest.mark.asyncio
    async def test_execute_simple(self, context):
        tool = PythonSandboxTool()
        result = await tool.execute({"code": "print(42)"}, context)
        assert result.status == "success"
        assert "42" in result.output["result"]

    @pytest.mark.asyncio
    async def test_execute_with_result(self, context):
        tool = PythonSandboxTool()
        result = await tool.execute({"code": "import math; print(math.sqrt(16))"}, context)
        assert result.status == "success"
        assert "4.0" in result.output["result"]


class TestEmailSenderTool:
    @pytest.mark.asyncio
    async def test_send_email_mock(self, context):
        tool = EmailSenderTool()
        result = await tool.execute({
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello",
        }, context)
        assert result.status == "success"
        assert result.output["status"] == "sent (mock)"
        assert "message_id" in result.output


# ============================================================
# Tests: Executor
# ============================================================

class TestExecutor:
    @pytest.mark.asyncio
    async def test_execute_calculator(self, executor, context):
        result = await executor.execute(
            "calculator",
            {"expression": "10 * 5"},
            context,
        )
        assert result.status == "success"
        assert result.output["result"] == 50

    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, executor, context):
        result = await executor.execute(
            "nonexistent",
            {},
            context,
        )
        assert result.status == "error"
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_execute_invalid_params(self, executor, context):
        result = await executor.execute(
            "calculator",
            {},
            context,
        )
        assert result.status == "error"
        assert "required" in result.error

    @pytest.mark.asyncio
    async def test_execute_dry_run(self, executor, context):
        result = await executor.execute(
            "calculator",
            {"expression": "1+1"},
            context,
            dry_run=True,
        )
        assert result.status == "dry_run"

    @pytest.mark.asyncio
    async def test_audit_log(self, executor, context):
        await executor.execute("calculator", {"expression": "1+1"}, context)
        log = executor.get_audit_log()
        assert len(log) >= 1
        assert log[-1]["tool_id"] == "calculator"
        assert log[-1]["status"] == "success"


# ============================================================
# Tests: Integration
# ============================================================

class TestTEFIntegration:
    @pytest.mark.asyncio
    async def test_full_flow(self, registry, executor, context):
        """Test completo: discover → execute → audit."""
        # 1. Discover
        tools = registry.discover("calcular")
        assert len(tools) > 0
        tool_id = tools[0].id

        # 2. Execute
        result = await executor.execute(
            tool_id,
            {"expression": "2 ** 10"},
            context,
        )
        assert result.status == "success"
        assert result.output["result"] == 1024

        # 3. Audit
        log = executor.get_audit_log()
        assert len(log) >= 1
        assert log[-1]["tool_id"] == tool_id
        assert log[-1]["status"] == "success"

    @pytest.mark.asyncio
    async def test_error_handling(self, registry, executor, context):
        """Test de manejo de errores."""
        # Ejecutar con parámetros inválidos
        result = await executor.execute(
            "calculator",
            {"expression": "invalid!"},
            context,
        )
        assert result.status == "error"

        # Verificar auditoría
        log = executor.get_audit_log()
        assert any(e["status"] == "failed" for e in log)
