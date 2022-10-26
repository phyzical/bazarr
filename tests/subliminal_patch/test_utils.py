import pytest
import os

from subliminal_patch.providers import utils
from zipfile import ZipFile
from rarfile import RarFile


@pytest.mark.parametrize(
    "sub_names,forced,episode,expected",
    [
        (("breaking bad s01e01.srt",), False, 1, "breaking bad s01e01.srt"),
        (("taxi.driver.1976.srt",), False, None, "taxi.driver.1976.srt"),
        (("taxi.driver.1976.s01e01.srt",), False, None, "taxi.driver.1976.s01e01.srt"),
        (("breaking.bad.s01e02.srt", "breaking.bad.s01e03.srt"), False, 1, None),
        (
            ("breaking.bad.s01e02.srt", "breaking.bad.s01e01.srt"),
            False,
            1,
            "breaking.bad.s01e01.srt",
        ),
        (("dummy.forced.srt",), True, None, "dummy.forced.srt"),
        (("dummy.forced.srt",), False, 1, None),
    ],
)
def test_get_matching_sub(sub_names, episode, forced, expected):
    assert utils._get_matching_sub(sub_names, forced, episode) == expected


def test_get_matching_sub_complex_season_pack():
    files = [
        "30. Hard Drive Courage. The Ride Of The Valkyries.srt",
        "34. So In Louvre Are We Two. Night Of The Scarecrow.srt",
        "31. Scuba Scuba Doo. Conway The Contaminationist.srt",
        "32. Katz Under The Sea. Curtain Of Cruelty.srt",
        "27. Muriel Meets Her Match. Courage Vs. Mecha-Courage.srt",
        "36. Fishy Business. Angry Nasty People.srt",
        "28. Campsite Of Terror. The Record Deal.srt",
        "33. Feast Of The Bullfrogs. Tulip's Worm.srt",
        "37. Dome Of Doom. Snowman's Revenge.srt",
        "35. Mondo Magic. Watch The Birdies.srt",
        "29. Stormy Weather. The Sandman Sleeps.srt",
        "38. The Quilt Club. Swindlin' Wind.srt",
    ]
    # Courage the Cowardly Dog S03E17 "Mondo Magic"
    matched = utils._get_matching_sub(files, False, 17, episode_title="Mondo Magic")
    assert matched == "35. Mondo Magic. Watch The Birdies.srt"


def test_get_matching_sub_complex_season_pack_mixed_files():
    files = [
        "30. Hard Drive Courage. The Ride Of The Valkyries.srt",
        "S03E15.srt",
        "S03E16.srt",
        "S03E17.srt",
        "28. Campsite Of Terror. The Record Deal.srt",
        "33. Feast Of The Bullfrogs. Tulip's Worm.srt",
        "37. Dome Of Doom. Snowman's Revenge.srt",
        "35. Mondo Magic. Watch The Birdies.srt",
        "29. Stormy Weather. The Sandman Sleeps.srt",
        "38. The Quilt Club. Swindlin' Wind.srt",
    ]
    # Courage the Cowardly Dog S03E17 "Mondo Magic"
    matched = utils._get_matching_sub(files, False, 17, episode_title="Mondo Magic")
    assert matched == "S03E17.srt"


def test_get_subtitle_from_archive_movie(data):
    with ZipFile(os.path.join(data, "archive_1.zip")) as zf:
        assert utils.get_subtitle_from_archive(zf) is not None


def test_get_subtitle_from_archive_season_pack(data):
    with RarFile(os.path.join(data, "archive_2.rar")) as zf:
        assert utils.get_subtitle_from_archive(zf, episode=4) is not None


@pytest.mark.parametrize("filename", ["archive_1.zip", "archive_2.rar"])
def test_get_archive_from_bytes_zip(data, filename):
    with open(os.path.join(data, filename), "rb") as zf:
        assert utils.get_archive_from_bytes(zf.read()) is not None


def test_get_archive_from_bytes_none():
    assert utils.get_archive_from_bytes(bytes()) is None


def test_update_matches(movies):
    matches = set()
    utils.update_matches(
        matches, movies["dune"], "Subs for dune 2021 bluray x264\nDune webrip x264"
    )
    assert "source" in matches


@pytest.mark.parametrize(
    "content,expected", [("the.wire.s01e01", True), ("taxi driver 1976", False)]
)
def test_is_episode(content, expected):
    assert utils.is_episode(content) is expected
