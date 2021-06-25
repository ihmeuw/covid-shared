import os


def validate_options_with_q(quick: int, mark_best: bool, production_tag: str):
    """
    Quick runs should never be marked 'best' or for production
    """
    if quick and (mark_best or production_tag):
        raise ValueError("Cannot mark a quick snapshot as best or for production.")


def ensure_archive_access():
    """ Check that node includes archive access """
    hostname = os.getenv('HOSTNAME')
    if 'archive' not in hostname:
        raise RuntimeError(f"Snapshot needs snfs access (currently on {hostname}); include '-l archive=TRUE' in your login request")
