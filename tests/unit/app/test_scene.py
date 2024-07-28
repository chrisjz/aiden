import io
import sys
from unittest.mock import patch
import pytest
from aiden.app.scene import Scene
from aiden.models.brain import Sensory
from aiden.models.scene import (
    Door,
    EntityType,
    FieldOfView,
    Object,
    SceneConfig,
    Position,
    Room,
    Player,
    Size,
    Interaction,
    States,
)


def capture_output(func, *args, **kwargs):
    captured_output = io.StringIO()
    with patch("sys.stdout", new=captured_output), patch(
        "sys.stdin", io.StringIO("exit\n")
    ):
        func(*args, **kwargs)
    return captured_output.getvalue()


@pytest.fixture
def simple_scene():
    player = Player(
        position=Position(x=0, y=0),
        orientation="S",
        fieldOfView=FieldOfView(angle=45, radius=3),
    )
    rooms = [
        Room(
            name="Test Room", position=Position(x=0, y=0), size=Size(width=5, height=5)
        )
    ]
    config = SceneConfig(rooms=rooms, player=player)
    return Scene(config)


@pytest.fixture
def complex_scene():
    player = Player(
        position=Position(x=1, y=1),
        orientation="N",
        fieldOfView=FieldOfView(angle=45, radius=3),
    )
    rooms = [
        Room(
            name="Living Room",
            position=Position(x=0, y=0),
            size=Size(width=5, height=5),
            objects=[
                Object(
                    name="Sofa",
                    position=Position(x=2, y=2),
                    senses={},
                    initialStates={},
                    interactions=[],
                )
            ],
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
            objects=[
                Object(
                    name="Bed",
                    position=Position(x=7, y=1),
                    senses={},
                    initialStates={},
                    interactions=[],
                )
            ],
        ),
    ]
    config = SceneConfig(rooms=rooms, player=player)
    return Scene(config)


@pytest.fixture
def interactive_scene():
    player = Player(
        position=Position(x=2, y=2),
        orientation="S",
        fieldOfView=FieldOfView(angle=45, radius=3),
    )
    sofa = Object(
        name="Sofa",
        position=Position(x=2, y=3),
        symbol="🛋️",
        interactions=[],
        initialStates={},
    )
    tv = Object(
        name="TV",
        position=Position(x=2, y=2),
        symbol="📺",
        interactions=[
            Interaction(
                command="turn on",
                description="Turn the TV on.",
                states=States(
                    requiredStates={"isOn": False}, nextStates={"isOn": True}
                ),
                senses={
                    "vision": "TV playing a sports game",
                    "auditory": "You hear an audience cheer from the TV segment playing",
                },
            ),
            Interaction(
                command="turn off",
                description="Turn the TV off.",
                states=States(
                    requiredStates={"isOn": True}, nextStates={"isOn": False}
                ),
                senses={
                    "vision": "TV which is switched off",
                    "auditory": "No sound coming from the TV",
                },
            ),
        ],
        initialStates={"isOn": False},
    )
    rooms = [
        Room(
            name="Living Room",
            position=Position(x=0, y=0),
            size=Size(width=5, height=5),
            objects=[sofa, tv],
            senses=Sensory(
                vision="A spacious living room with large windows",
                auditory="A constant low hum from an air conditioner",
                olfactory="Freshly brewed coffee",
                tactile="Smooth, cool wooden floors underfoot",
                gustatory="",
            ),
        )
    ]
    config = SceneConfig(rooms=rooms, player=player)
    scene = Scene(config)
    scene.object_states = {
        "TV": {"isOn": False},
        "Sofa": {},
    }  # Mocking the state dictionary
    return scene


def test_move_forward(simple_scene):
    simple_scene.process_action("forward")
    assert simple_scene.player_position == (0, 1), "Should move South"


def test_backwards_movement(simple_scene):
    simple_scene.process_action(
        "backward"
    )  # Initially facing south, moving backward should keep the same position
    assert simple_scene.player_position == (
        0,
        0,
    ), "Backward movement should not exit the room boundary"


def test_turn_right(simple_scene):
    simple_scene.turn_right()
    assert (
        simple_scene.player_orientation == "W"
    ), "Should turn to West when initially facing South"


def test_turn_left(simple_scene):
    simple_scene.turn_left()
    assert (
        simple_scene.player_orientation == "E"
    ), "Should turn to East when initially facing South"


def test_teleport_to_room_via_door(complex_scene):
    complex_scene.player_position = (4, 3)  # Position at the door entry
    complex_scene.process_action("forward")
    complex_scene.process_action("use")  # Trigger action to move through door
    assert complex_scene.player_position == (
        0,
        0,
    ), "Should teleport to the bedroom exit position"


def test_object_interaction(complex_scene):
    complex_scene.process_action("forward")  # Move north to y=0
    complex_scene.process_action("right")  # Move east to x=2
    complex_scene.process_action("right")  # Move east to x=2, position of the sofa
    assert (
        complex_scene.get_entity_by_position((2, 2), EntityType.OBJECT).name == "Sofa"
    ), "Should be at the position of the Sofa"


def test_view_field_sensing_objects(complex_scene):
    # given
    complex_scene.player_position = (6, 1)
    complex_scene.player_orientation = "E"  # Look east towards the bedroom

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (1, 0), "Bed should be one position ahead"

    # given
    complex_scene.player_orientation = "S"  # Look south

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 0, "Should not see any objects"

    # given
    complex_scene.player_position = (7, 1)
    complex_scene.player_orientation = "N"  # Look north

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (0, 0), "Should be on the bed"

    # given
    complex_scene.player_position = (5, 1)
    complex_scene.player_orientation = "E"  # Look east

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (2, 0), "Bed should be two positions ahead"

    # given
    complex_scene.player_position = (5, 0)
    complex_scene.player_orientation = "E"  # Look east

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (
        2,
        1,
    ), "Bed should be two positions ahead at 45 degrees"

    # given
    complex_scene.player_position = (5, 2)
    complex_scene.player_orientation = "E"  # Look east

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (
        2,
        -1,
    ), "Bed should be two positions ahead at -45 degrees"

    # given
    complex_scene.player_position = (6, 2)
    complex_scene.player_orientation = "N"  # Look north

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (
        1,
        -1,
    ), "Bed should be one position ahead at -45 degrees"

    # given
    player_fov_radius = complex_scene.player.fieldOfView.radius
    complex_scene.player_position = (7 - player_fov_radius, 1)
    complex_scene.player_orientation = "E"  # Look east

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 1, "Should only see a Bed"
    assert visible_objects[0][0].name == "Bed", "Should see the Bed in the bedroom"
    assert visible_objects[0][1] == (
        player_fov_radius,
        0,
    ), f"Bed should be {player_fov_radius} position ahead"

    # given
    player_fov_radius = complex_scene.player.fieldOfView.radius
    complex_scene.player_position = (7 - player_fov_radius - 1, 1)
    complex_scene.player_orientation = "E"  # Look east

    # when
    visible_objects = complex_scene.get_field_of_view()

    # then
    assert len(visible_objects) == 0, "Bed should be out of view ahead"


def test_no_movement_on_obstruction(complex_scene):
    complex_scene.player_position = (4, 0)  # On the northern boundary of the room
    complex_scene.process_action(
        "w"
    )  # Trying to move out of the room's northern boundary
    assert complex_scene.player_position == (
        4,
        0,
    ), "Should not move when an obstruction is faced"


def test_sensory_data_interaction(complex_scene):
    # Add a Durian with distinct sensory properties to the Living Room
    durian = Object(
        name="Durian",
        position=Position(x=1, y=1),
        senses={
            "vision": "A large spiky Durian fruit on the table",
            "auditory": "Soft buzzing of fruit flies",
            "olfactory": "A strong pungent smell that fills the room",
            "gustatory": "Rich custard taste with hints of almond",
            "tactile": "Spiky and hard outer shell",
        },
        initialStates={},
        interactions=[],
    )
    complex_scene.rooms["Living Room"].objects.append(durian)

    # Move player to the position of the Durian
    complex_scene.player_position = (1, 1)
    current_object = complex_scene.get_entity_by_position((1, 1), EntityType.OBJECT)

    # Ensure the object is the Durian and test each sensory attribute
    assert current_object.name == "Durian", "Should be at the position of the Durian"
    assert (
        current_object.senses.vision == "A large spiky Durian fruit on the table"
    ), "Vision should detect the Durian visually"
    assert (
        current_object.senses.auditory == "Soft buzzing of fruit flies"
    ), "Should hear the sound associated with the Durian"
    assert (
        current_object.senses.olfactory == "A strong pungent smell that fills the room"
    ), "Should smell the Durian's strong odor"
    assert (
        current_object.senses.gustatory == "Rich custard taste with hints of almond"
    ), "Should taste the Durian flavor"
    assert (
        current_object.senses.tactile == "Spiky and hard outer shell"
    ), "Should feel the Durian's texture"


def test_available_interactions_based_on_state(interactive_scene, monkeypatch):
    # Ensure the TV is off
    interactive_scene.object_states["TV"] = {"isOn": False}
    # Simulate user input for exiting interaction mode immediately
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    output = capture_output(interactive_scene.interact_with_object)

    assert "turn on" in output, "Turn on command should be available"
    assert "turn off" not in output, "Turn off command should not be available"


def test_interaction_execution_changes_state(interactive_scene, monkeypatch):
    # Prepare the responses for input calls
    inputs = iter(["turn on", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Redirect stdout to capture prints
    captured_output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)

    # Position player correctly and then simulate interaction
    interactive_scene.process_action(
        "e"
    )  # Trigger interaction which should handle inputs

    # Fetch the captured output and check it
    output = captured_output.getvalue()
    assert (
        "TV playing a sports game" in output
    ), f"Expected 'TV playing a sports game' in output, got: {output}"


def test_exit_interaction_command(interactive_scene):
    # Mock input to simulate "exit" command
    with patch("builtins.input", return_value="exit"):
        output = capture_output(interactive_scene.interact_with_object)
    assert "Exiting interaction mode." in output


def test_no_interactions_available(interactive_scene, monkeypatch):
    # Move player to sofa location
    interactive_scene.process_action("w")
    # Simulate user input for exiting interaction mode immediately
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    output = capture_output(interactive_scene.interact_with_object)
    assert (
        "There are no available interactions with Sofa based on its current state."
        in output
    ), "Should indicate no interactions available"
    assert (
        "sit" not in output
    ), "Sit command should not be available since the TV is already on"


@pytest.mark.parametrize(
    "player_position, expected_vision, expected_auditory, expected_olfactory, expected_tactile, expected_gustatory",
    [
        (
            (1, 1),
            "A spacious living room with large windows | TV which is switched off",
            "A constant low hum from an air conditioner | No sound coming from the TV",
            "Freshly brewed coffee",
            "Smooth, cool wooden floors underfoot",
            "",
        ),
        (
            (2, 2),
            "A spacious living room with large windows | TV which is switched off",
            "A constant low hum from an air conditioner | No sound coming from the TV",
            "Freshly brewed coffee",
            "Smooth, cool wooden floors underfoot",
            "",
        ),
    ],
)
def test_update_sensory_data(
    interactive_scene,
    player_position,
    expected_vision,
    expected_auditory,
    expected_olfactory,
    expected_tactile,
    expected_gustatory,
):
    # Set player position
    interactive_scene.player_position = player_position

    # Execute the get_sensory_data function
    sensory_data = interactive_scene.update_sensory_data()

    # Assert each sense is correctly gathered
    assert (
        sensory_data.vision == expected_vision
    ), f"Vision should correctly reflect the player's visual input for position {player_position}"
    assert (
        sensory_data.auditory == expected_auditory
    ), f"Sound should match the environment auditory cues for position {player_position}"
    assert (
        sensory_data.olfactory == expected_olfactory
    ), f"Smell should match the environment olfactory cues for position {player_position}"
    assert (
        sensory_data.tactile == expected_tactile
    ), f"Tactile should match the environment touch feedback for position {player_position}"
    assert (
        sensory_data.gustatory == expected_gustatory
    ), f"Taste should match the environment taste input (if any) for position {player_position}"


@pytest.mark.parametrize(
    "name, relative_position, expected_description",
    [
        ("TV", (1, -1), "The TV is 1.4 meters back-right."),
        ("Sofa", (0, 1), "The Sofa is 1.0 meters in front."),
        ("Lamp", (-1, 0), "The Lamp is 1.0 meters to the left."),
        ("Table", (0, -1), "The Table is 1.0 meters behind."),
        ("Chair", (1, 0), "The Chair is 1.0 meters to the right."),
        ("Desk", (1, 1), "The Desk is 1.4 meters in front-right."),
        ("Shelf", (-1, 1), "The Shelf is 1.4 meters in front-left."),
        ("Bed", (-1, -1), "The Bed is 1.4 meters back-left."),
        ("Plant", (2, 0), "The Plant is 2.0 meters to the right."),
        ("Clock", (0, 2), "The Clock is 2.0 meters in front."),
        ("Window", (-2, 0), "The Window is 2.0 meters to the left."),
        ("Door", (0, -2), "The Door is 2.0 meters behind."),
    ],
)
def test_describe_relative_position(
    simple_scene, name, relative_position, expected_description
):
    assert (
        simple_scene.describe_relative_position(name, relative_position)
        == expected_description
    )
