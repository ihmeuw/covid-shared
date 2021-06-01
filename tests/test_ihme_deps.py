import pytest

from covid_shared.ihme_deps import _lazy_import_callable


def test_lazy_import_callable_pass():
    from itertools import chain
    chain2 = _lazy_import_callable('itertools', 'chain')
    assert chain is chain2


def test_lazy_import_callable_fail():
    magic = _lazy_import_callable('fairyland', 'magic')
    with pytest.raises(ModuleNotFoundError):
        magic()
