"""Board Room tests — verifies concurrent execution and consensus."""
import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.nivel1.board_room import BoardRoom, AGENT_PROMPTS, BoardConsensus


class MockLLMAdapter:
    """Mock LLM for testing without Ollama."""

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=1024):
        response = MagicMock()
        response.content = '{"analysis":"Test","justification":"Test","vote":"PROCEED","confidence":80,"key_strengths":["s1"],"key_concerns":["c1"],"questions":["q1"]}'
        response.model = "mock"
        response.duration_s = 0.1
        return response


@pytest.fixture
def mock_llm():
    return MockLLMAdapter()


@pytest.fixture
def board_room(mock_llm):
    return BoardRoom(mock_llm)


def test_board_room_runs_all_four_agents(board_room):
    """Board Room must run all 4 agents."""
    result = asyncio.run(
        board_room.run("Test problem")
    )
    assert isinstance(result, BoardConsensus)
    assert len(result.votes) == 4
    agent_names = {v.agent for v in result.votes}
    assert agent_names == {"CEO", "CTO", "CFO", "CMO"}


def test_board_room_has_consensus(board_room):
    """Board Room must produce a consensus decision."""
    result = asyncio.run(
        board_room.run("Test problem")
    )
    assert result.decision in ["PROCEED", "PIVOT", "STOP"]
    assert 0 <= result.score <= 100
    assert 0 <= result.confidence <= 100
    assert result.summary is not None


def test_board_room_votes_have_required_fields(board_room):
    """Each vote must have required fields."""
    result = asyncio.run(
        board_room.run("Test problem")
    )
    for vote in result.votes:
        assert vote.agent in ["CEO", "CTO", "CFO", "CMO"]
        assert vote.vote in ["PROCEED", "PIVOT", "STOP"]
        assert 0 <= vote.confidence <= 100
        assert vote.analysis is not None
        assert vote.justification is not None


def test_board_room_concurrent_execution(mock_llm):
    """Agents must run concurrently, not sequentially."""
    call_times = []

    async def timed_chat(messages, **kwargs):
        call_times.append(("start", time.monotonic()))
        await asyncio.sleep(0.1)  # Simulate work
        call_times.append(("end", time.monotonic()))
        response = MagicMock()
        response.content = '{"analysis":"Test","justification":"Test","vote":"PROCEED","confidence":80,"key_strengths":[],"key_concerns":[],"questions":[]}'
        response.model = "mock"
        response.duration_s = 0.1
        return response

    mock_llm.chat = timed_chat
    board_room = BoardRoom(mock_llm)

    start = time.monotonic()
    result = asyncio.run(
        board_room.run("Test problem")
    )
    total_time = time.monotonic() - start

    # If concurrent, total time should be ~0.1s (one sleep), not ~0.4s (four sleeps)
    assert total_time < 0.3, f"Board Room took {total_time:.2f}s, expected <0.3s for concurrent"
    assert len(call_times) == 8  # 4 starts + 4 ends


def test_consensus_majority_rule(board_room):
    """Consensus follows majority vote."""
    result = asyncio.run(
        board_room.run("Test problem")
    )
    # With mock returning PROCEED for all, consensus should be PROCEED
    assert result.decision == "PROCEED"
