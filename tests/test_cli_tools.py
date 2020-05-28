from datetime import datetime
from pathlib import Path
import random
from typing import Callable

import pytest

from covid_shared import cli_tools, paths

MOCK_DATETIME = datetime(2020, 4, 25, 17, 5, 55)
ABSOLUTE_PATH_1 = Path('/absolute/path/one')
ABSOLUTE_PATH_2 = Path('/absolute/path/two')
RELATIVE_PATH = Path('some/relative/path')


@pytest.fixture
def mock_datetime(mocker):

    class _mydatetime:

        @classmethod
        def now(cls):
            return MOCK_DATETIME

        @classmethod
        def strptime(cls, s, _format):
            return datetime.strptime(s, _format)

    return mocker.patch('covid_shared.cli_tools.run_directory.datetime.datetime', _mydatetime)


@pytest.fixture()
def empty_run_dir_root(tmp_path: Path):
    cli_tools.setup_directory_structure(tmp_path, with_production=True)
    return tmp_path


@pytest.fixture()
def run_dir_root(empty_run_dir_root, mock_datetime):
    for _ in range(10):
        run_dir = cli_tools.get_run_directory(empty_run_dir_root)
        run_dir.mkdir()
    return empty_run_dir_root


def _get_random_run_dir(root_dir: Path):
    # Run dirs are dot separated.
    sub_dirs = [d for d in root_dir.iterdir() if '.' in d.name]
    return random.choice(sub_dirs)


def test_get_run_directory(tmp_path: Path, mock_datetime):
    dir_date = MOCK_DATETIME.strftime('%Y_%m_%d')
    run_dir = cli_tools.get_run_directory(tmp_path)
    assert run_dir.name == f'{dir_date}.01'
    run_dir.mkdir()

    run_dir = cli_tools.get_run_directory(tmp_path)
    assert run_dir.name == f'{dir_date}.02'


def test_setup_directory_structure_no_production(tmp_path: Path):
    cli_tools.setup_directory_structure(tmp_path)
    assert tmp_path.exists()
    for subdir in [paths.BEST_LINK, paths.LATEST_LINK]:
        assert (tmp_path / subdir).exists()
        assert (tmp_path / subdir).is_dir()
        assert not (tmp_path / subdir).is_symlink()

    assert not (tmp_path / paths.PRODUCTION_RUN).exists()


def test_setup_directory_structure(tmp_path: Path):
    cli_tools.setup_directory_structure(tmp_path, with_production=True)
    assert tmp_path.exists()
    for subdir in [paths.BEST_LINK, paths.LATEST_LINK, paths.PRODUCTION_RUN]:
        assert (tmp_path / subdir).exists()
        assert (tmp_path / subdir).is_dir()
        assert not (tmp_path / subdir).is_symlink()


def test_setup_directory_structure_noop(empty_run_dir_root: Path):
    cli_tools.setup_directory_structure(empty_run_dir_root)
    assert empty_run_dir_root.exists()
    for subdir in [paths.BEST_LINK, paths.LATEST_LINK, paths.PRODUCTION_RUN]:
        assert (empty_run_dir_root / subdir).exists()
        assert (empty_run_dir_root / subdir).is_dir()
        assert not (empty_run_dir_root / subdir).is_symlink()


def test_move_link_dir(run_dir_root: Path):
    link_dir = (run_dir_root / 'test_link_dir')
    link_dir.mkdir()
    target_dir = _get_random_run_dir(run_dir_root)
    cli_tools.move_link(link_dir, target_dir)
    assert link_dir.exists()
    assert link_dir.is_dir()
    assert link_dir.is_symlink()
    assert link_dir.resolve() == target_dir


def test_move_link_file_fail(run_dir_root: Path):
    link_file = (run_dir_root / 'test_link_dir')
    link_file.touch()
    target_dir = _get_random_run_dir(run_dir_root)
    with pytest.raises(ValueError, match='not a symlink or a directory'):
        cli_tools.move_link(link_file, target_dir)


def test_move_link_existing_link(run_dir_root: Path):
    link_dir = (run_dir_root / 'test_link_dir')
    link_dir.mkdir()
    target_dir = _get_random_run_dir(run_dir_root)
    cli_tools.move_link(link_dir, target_dir)
    assert link_dir.resolve() == target_dir
    new_target_dir = _get_random_run_dir(run_dir_root)
    cli_tools.move_link(link_dir, new_target_dir)
    assert link_dir.exists()
    assert link_dir.is_dir()
    assert link_dir.is_symlink()
    assert link_dir.resolve() == new_target_dir


def test_mark_explicit(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    for link_name in [paths.BEST_LINK, paths.LATEST_LINK, 'other_link']:
        cli_tools.mark_explicit(run_dir, run_dir_root, link_name)
        link_path = run_dir_root / link_name
        assert link_path.exists()
        assert link_path.is_dir()
        assert link_path.is_symlink()
        assert link_path.resolve() == run_dir


def test_mark_explicit_nested_version_root(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    prod_dir = run_dir_root / paths.PRODUCTION_RUN
    link_name = 'prod_run'
    link_path = prod_dir / link_name
    cli_tools.mark_explicit(run_dir, prod_dir, link_name)
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


@pytest.mark.parametrize(('mark_func', 'link_name'),
                         ((cli_tools.mark_latest_explicit, paths.LATEST_LINK),
                          (cli_tools.mark_best_explicit, paths.BEST_LINK)),
                         ids=lambda x: x if isinstance(x, str) else '')
def test_mark_link_explicit(mark_func: Callable, link_name: str, run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    prod_dir = run_dir_root / paths.PRODUCTION_RUN
    for root_dir in [run_dir_root, prod_dir]:
        link_path = root_dir / link_name
        mark_func(run_dir, root_dir)
        assert link_path.exists()
        assert link_path.is_dir()
        assert link_path.is_symlink()
        assert link_path.resolve() == run_dir


@pytest.mark.parametrize(('mark_func', 'link_name'),
                         ((cli_tools.mark_latest, paths.LATEST_LINK),
                          (cli_tools.mark_best, paths.BEST_LINK)),
                         ids=lambda x: x if isinstance(x, str) else '')
def test_mark_link(mark_func: Callable, link_name: str, run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    mark_func(run_dir)
    link_path = run_dir_root / link_name
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


def test_mark_production_explicit_no_date(run_dir_root: Path, mock_datetime):
    run_dir = _get_random_run_dir(run_dir_root)
    cli_tools.mark_production_explicit(run_dir, run_dir_root / paths.PRODUCTION_RUN)
    link_path = run_dir_root / paths.PRODUCTION_RUN / MOCK_DATETIME.strftime('%Y_%m_%d')
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


def test_mark_production_explicit_fail(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    date = 'the_time_is_now'
    with pytest.raises(ValueError):
        cli_tools.mark_production_explicit(run_dir, run_dir_root / paths.PRODUCTION_RUN, date)


def test_mark_production_explicit(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    date = '2020_04_25'
    cli_tools.mark_production(run_dir, date)
    link_path = run_dir_root / paths.PRODUCTION_RUN / date
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


def test_mark_production_no_date(run_dir_root: Path, mock_datetime):
    run_dir = _get_random_run_dir(run_dir_root)
    cli_tools.mark_production(run_dir)
    link_path = run_dir_root / paths.PRODUCTION_RUN / MOCK_DATETIME.strftime('%Y_%m_%d')
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


def test_mark_production_fail(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    date = 'the_time_is_now'
    with pytest.raises(ValueError):
        cli_tools.mark_production(run_dir, date)


def test_mark_production(run_dir_root: Path):
    run_dir = _get_random_run_dir(run_dir_root)
    date = '2020_04_25'
    cli_tools.mark_production(run_dir, date)
    link_path = run_dir_root / paths.PRODUCTION_RUN / date
    assert link_path.exists()
    assert link_path.is_dir()
    assert link_path.is_symlink()
    assert link_path.resolve() == run_dir


@pytest.mark.parametrize(('last_stage_version', 'last_stage_directory', 'last_stage_root', 'result'),
                         [(ABSOLUTE_PATH_1, ABSOLUTE_PATH_2, None, ABSOLUTE_PATH_2),
                          (ABSOLUTE_PATH_1, ABSOLUTE_PATH_2, ABSOLUTE_PATH_1, ABSOLUTE_PATH_2),
                          (ABSOLUTE_PATH_1, None, None, ABSOLUTE_PATH_1),
                          (ABSOLUTE_PATH_1, None, ABSOLUTE_PATH_2, ABSOLUTE_PATH_1),
                          (None, ABSOLUTE_PATH_1, None, ABSOLUTE_PATH_1),
                          (ABSOLUTE_PATH_1, RELATIVE_PATH, ABSOLUTE_PATH_2, ABSOLUTE_PATH_2 / RELATIVE_PATH),
                          (RELATIVE_PATH, None, ABSOLUTE_PATH_1, ABSOLUTE_PATH_1 / RELATIVE_PATH),
                          ])
def test_get_last_stage_directory(last_stage_version, last_stage_directory, last_stage_root, result):
    assert cli_tools.get_last_stage_directory(last_stage_version, last_stage_directory, last_stage_root) == result


@pytest.mark.parametrize(('last_stage_version', 'last_stage_directory', 'last_stage_root'),
                         [(ABSOLUTE_PATH_1, RELATIVE_PATH, None),
                          (RELATIVE_PATH, None, None),
                          (RELATIVE_PATH, None, RELATIVE_PATH),
                          (RELATIVE_PATH, RELATIVE_PATH, RELATIVE_PATH)
                          ])
def test_get_last_stage_directory_errors(last_stage_version, last_stage_directory, last_stage_root):
    with pytest.raises(ValueError):
        cli_tools.get_last_stage_directory(last_stage_version, last_stage_directory, last_stage_root)
