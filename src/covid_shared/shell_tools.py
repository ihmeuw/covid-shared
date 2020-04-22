import os
from pathlib import Path
import shlex
import subprocess
from typing import Union


def wget(url: str, output_path: Union[str, Path]):
    """Retrieves content at the url and stores it an an output path.

    Parameters
    ----------
    url
        The url to retrieve the content from.
    output_path
        Where we'll save the output to.

    """
    subprocess.run(shlex.split(f'wget -O {output_path} {url}'), check=True)


def unzip_and_delete_archive(archive_path: Union[str, Path], output_path: Union[str, Path]):
    """Unzips an archive file to a directory and then deletes the archive.

    Parameters
    ----------
    archive_path
        The path to the archive we want to unzip.
    output_path
        The place to store the unzipped contents.

    """
    subprocess.run(shlex.split(f'unzip {archive_path} -d {output_path}'), check=True)
    subprocess.run(shlex.split(f'rm {archive_path}'), check=True)


def mkdir(path: Union[str, Path], umask: int = 0o002, exists_ok: bool = False, parents: bool = False) -> None:
    """Creates a directory with permissions specified by the umask

    Parameters
    ----------
    path
        path of the directory to create
    umask
        umask specifying the desired permissions - defaults to 0o002
    exists_ok
        if False, raises FileExistsError if the directory already exists
    parents
        if False, raises FileNotFoundError if the directory's parent doesn't exist

    """
    path = Path(path)
    old_umask = os.umask(umask)
    try:
        path.mkdir(exist_ok=exists_ok, parents=parents)
    finally:
        os.umask(old_umask)
