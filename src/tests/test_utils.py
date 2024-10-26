import pytest
from unittest.mock import patch, MagicMock

from geolocator import utils


@pytest.mark.parametrize(
    "model_file_contents, expected",
    [
        ("Raspberry Pi 5", True),
        ("raspberry pi", True),
        ("test", False),
        ("Test PC", False),
    ],
)
def test_is_raspberry_pi(monkeypatch, model_file_contents, expected):
    def mock_open(*args, **kwargs):
        class MockFile:
            def read(self):
                return model_file_contents

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

        return MockFile()

    monkeypatch.setattr(utils.io, "open", mock_open)

    assert utils.is_raspberrypi() == expected


@patch("geolocator.utils.subprocess.run")
@patch("geolocator.utils.is_raspberrypi")
@pytest.mark.parametrize(
    "can_update_time, time_to_set",
    [
        (
            True,
            "2022-01-01 12:00:00",
        ),
        (False, "2022-01-01 12:00:00"),
    ],
)
def test_update_system_datetime(
    mock_is_raspberrypi: MagicMock,
    mock_subprocess_run: MagicMock,
    can_update_time: bool,
    time_to_set: str,
):
    mock_is_raspberrypi.return_value = can_update_time
    utils.update_system_datetime(time_to_set)

    if can_update_time:
        mock_subprocess_run.assert_called_once_with(["sudo", "date", "-s", time_to_set])
    else:
        mock_subprocess_run.assert_not_called()


@pytest.mark.parametrize(
    "env_var_value, default, expected",
    [
        ("True", False, True),
        ("False", True, False),
        ("", True, True),
        ("", False, False),
    ],
)
def test_get_boolean_env_var(monkeypatch, env_var_value, default, expected):
    monkeypatch.setenv("TEST_VAR", env_var_value)
    assert utils.get_boolean_env_var("TEST_VAR", default) == expected
