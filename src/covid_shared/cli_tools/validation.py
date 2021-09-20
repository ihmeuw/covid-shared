def validate_best_and_production_tags(modifier: bool, mark_best: bool, production_tag: str):
    """
    Incomplete runs should never be marked 'best' or for production, eg quick, trial-run, etc
    """
    if modifier and (mark_best or production_tag):
        raise ValueError("Cannot mark an incomplete run as best or for production.")
