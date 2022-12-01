from multiprocessing import Pool as StdLibPool
from typing import Any, Callable, List, Optional

import pandas as pd
import tqdm
from pathos.multiprocessing import ProcessPool as PathosPool

Loader = Callable[[Any, Optional[pd.Index], int, int, bool], pd.DataFrame]


def is_notebook() -> bool:
    """Are we running code in a jupyter notebook?

    Code from https://stackoverflow.com/a/39662359
    """
    try:
        # The get_ipython function will be in the global namespace if we're in
        # an ipython-like environment (including jupyter notebooks).
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def run_parallel(
    runner: Callable,
    arg_list: List,
    num_cores: int,
    progress_bar: bool = False,
    notebook_fallback: bool = False,
) -> List[Any]:
    """Runs a single argument function in parallel over a list of arguments.

    This function dodges multiprocessing if only a single process is requested to
    make functions more flexible to debugging. It also supports progress bars if
    requested.

    Parameters
    ----------
    runner
        A single argument function to be run in parallel.
    arg_list
        A list of arguments to be run over in parallel.
    num_cores
        Maximum number of processes to be run in parallel. If num_cores == 1,
        The jobs will be run serially without invoking multiprocessing.
    progress_bar
        Whether to display a progress bar for the running jobs.
    notebook_fallback
        Whether to fallback to standard multiprocessing in a notebook. We use `pathos`
        for multiprocessing as it uses a more robust serialization library, but `pathos`
        has some leaky state and doesn't properly close down child processes when
        interrupted in a jupyter notebook.

    Returns
    -------
    List[Any]
        A list of the results of the parallel calls of the runner.

    """

    if num_cores == 1:
        result = []
        for arg in tqdm.tqdm(arg_list, disable=not progress_bar):
            result.append(runner(arg))
    else:
        if is_notebook() and notebook_fallback:
            processing_pool_class = StdLibPool
        else:
            processing_pool_class = PathosPool

        with processing_pool_class(num_cores) as pool:
            result = list(
                tqdm.tqdm(
                    pool.imap(runner, arg_list),
                    total=len(arg_list),
                    disable=not progress_bar,
                )
            )
    return result
