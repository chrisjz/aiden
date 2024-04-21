import pytest
from aiden.app.scene import Scene
from aiden.models.scene import Door, Object, SceneConfig, Position, Room, Player, Size


@pytest.fixture
def sample_scene():
    player = Player(position=Position(x=0, y=0), orientation="S", fieldOfView=3)
    rooms = [
        Room(
            name="Test Room", position=Position(x=0, y=0), size=Size(width=5, height=5)
        )
    ]
    config = SceneConfig(rooms=rooms, player=player)
    return Scene(config)


@pytest.fixture
def complex_scene():
    player = Player(position=Position(x=1, y=1), orientation="N", fieldOfView=3)
    rooms = [
        Room(
            name="Living Room",
            position=Position(x=0, y=0),
            size=Size(width=5, height=5),
            objects=[Object(name="Sofa", position=Position(x=2, y=2), senses={})],
            doors=[
                Door(
                    to="Bedroom",
                    position={"entry": Position(x=4, y=2), "exit": Position(x=0, y=0)},
                )
            ],
        ),
        Room(
            name="Bedroom",
            position=Position(x=5, y=0),
            size=Size(width=5, height=5),
            objects=[Object(name="Bed", position=Position(x=7, y=1), senses={})],
        ),
    ]
    config = SceneConfig(rooms=rooms, player=player)
    return Scene(config)


def test_move_forward(sample_scene):
    sample_scene.advance()
    assert sample_scene.player_position == (0, 1), "Should move South"


def test_backwards_movement(sample_scene):
    sample_scene.move_player(
        "s"
    )  # Initially facing south, moving backward should keep the same position
    assert sample_scene.player_position == (
        0,
        0,
    ), "Backward movement should not exit the room boundary"


def test_turn_right(sample_scene):
    sample_scene.turn_right()
    assert (
        sample_scene.player_orientation == "W"
    ), "Should turn to West when initially facing South"


def test_turn_left(sample_scene):
    sample_scene.turn_left()
    assert (
        sample_scene.player_orientation == "E"
    ), "Should turn to East when initially facing South"


def test_teleport_to_room_via_door(complex_scene):
    complex_scene.player_position = (4, 3)  # Position at the door entry
    complex_scene.move_player("w")  # Expected to teleport
    assert complex_scene.player_position == (
        0,
        0,
    ), "Should teleport to the bedroom exit position"


def test_object_interaction(complex_scene):
    complex_scene.move_player("w")  # Move north to y=0
    complex_scene.move_player("d")  # Move east to x=2
    complex_scene.move_player("d")  # Move east to x=2, position of the sofa
    assert (
        complex_scene.find_object_by_position((2, 2)).name == "Sofa"
    ), "Should be at the position of the Sofa"


def test_view_field_sensing_objects(complex_scene):
    complex_scene.player_position = (6, 1)
    complex_scene.player_orientation = "E"  # Look east towards the bedroom
    visible_objects = complex_scene.get_field_of_view()
    assert "Bed" in [
        obj.name for obj in visible_objects
    ], "Should see the Bed in the bedroom"


def test_no_movement_on_obstruction(complex_scene):
    complex_scene.player_position = (4, 0)  # On the northern boundary of the room
    complex_scene.move_player("w")  # Trying to move out of the room's northern boundary
    assert complex_scene.player_position == (
        4,
        0,
    ), "Should not move when an obstruction is faced"
