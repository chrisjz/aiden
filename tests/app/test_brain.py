import pytest

from aiden.app.brain import _map_decision_to_action


@pytest.mark.asyncio
async def test_map_decision_to_action():
    assert await _map_decision_to_action("Move forward") == "move_forward"
    assert await _map_decision_to_action("turn_left") == "turn_left"
    assert await _map_decision_to_action("Backward") == "move_backward"
    assert await _map_decision_to_action("right") == "turn_right"
    assert await _map_decision_to_action("0199393921") == "none"
