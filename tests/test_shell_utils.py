from pathlib import Path

import pytest

from covid_shared.shell_tools import mkdir


@pytest.fixture(params=range(0o700, 0o1000, 3))
def mode(request):
    return request.param


@pytest.fixture(params=[True, False])
def parents(request):
    return request.param


def test_mkdir_no_args(mode: int, tmp_path: Path):
    tmp_path.rmdir()
    assert not tmp_path.exists()
    mkdir(tmp_path, mode=mode)
    assert tmp_path.exists()
    assert oct(tmp_path.stat().st_mode)[-3:] == oct(mode)[-3:]


def test_mkdir_no_parents(mode: int, tmp_path: Path):
    tmp_path.rmdir()
    assert not tmp_path.exists()

    child_dir = tmp_path / 'child'
    with pytest.raises(FileNotFoundError):
        mkdir(child_dir, mode)


def test_mkdir_parents(mode: int, tmp_path: Path):
    tmp_path.rmdir()
    assert not tmp_path.exists()

    child_dir = tmp_path / 'child'
    mkdir(child_dir, mode, parents=True)
    assert tmp_path.exists()
    assert oct(tmp_path.stat().st_mode)[-3:] == oct(mode)[-3:]
    assert child_dir.exists()
    assert oct(child_dir.stat().st_mode)[-3:] == oct(mode)[-3:]


def test_mkdir_exists(mode: int, parents: bool, tmp_path: Path):
    assert tmp_path.exists()
    perms = oct(tmp_path.stat().st_mode)[-3:]

    with pytest.raises(FileExistsError):
        mkdir(tmp_path, mode, parents=parents)

    mkdir(tmp_path, mode, parents=parents, exists_ok=True)
    assert oct(tmp_path.stat().st_mode)[-3:] == perms
