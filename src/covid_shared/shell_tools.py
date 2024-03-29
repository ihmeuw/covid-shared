import os
import shlex
import subprocess
from pathlib import Path
from typing import Union


def wget(url: str, output_path: Union[str, Path]) -> None:
    """Retrieves content at the url and stores it an an output path.

    Parameters
    ----------
    url
        The url to retrieve the content from.
    output_path
        Where we'll save the output to.

    """
    subprocess.run(shlex.split(f"wget -O {output_path} {url}"), check=True)


def unzip_and_delete_archive(
    archive_path: Union[str, Path], output_path: Union[str, Path]
) -> None:
    """Unzips an archive file to a directory and then deletes the archive.

    Parameters
    ----------
    archive_path
        The path to the archive we want to unzip.
    output_path
        The place to store the unzipped contents.

    """
    subprocess.run(shlex.split(f"unzip {archive_path} -d {output_path}"), check=True)
    subprocess.run(shlex.split(f"rm {archive_path}"), check=True)


def mkdir(
    path: Union[str, Path],
    mode: int = 0o775,
    exists_ok: bool = False,
    parents: bool = False,
) -> None:
    """Creates a directory and its parents with the specified mode.

    This method is meant to combat permissions errors generated by the default
    umask behavior when creating parent directories (i.e. ignore the mode
    argument and use the default permissions).

    Parameters
    ----------
    path
        Path of the directory to create.
    mode
        Mode of directory to be created.
    exists_ok
        If False, raises FileExistsError if the directory already exists.
    parents
        If False, raises FileNotFoundError if the directory's parent doesn't
        exist.

    """
    path = Path(path)
    old_umask = os.umask(0o777 - mode)
    try:
        path.mkdir(exist_ok=exists_ok, parents=parents)
    finally:
        os.umask(old_umask)
