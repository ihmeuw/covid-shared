def validate_options_with_q(quick: int, mark_best: bool, production_tag: str):
    """
    Quick runs should never be marked 'best' or for production
    """
    if quick and (mark_best or production_tag):
        raise ValueError("Cannot mark a quick snapshot as best or for production.")
