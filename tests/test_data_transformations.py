import numpy as np
import pandas as pd
import pytest

from covid_shared.data_transformations import make_round_trip_invariant


@pytest.fixture(scope='function')
def time_series():
    # 30 elements.  Linear ramp, flat, linear ramp.
    time_series = np.hstack([
        np.arange(1, 11),
        11 * np.ones(10),
        2 * np.arange(11, 21)
    ])
    dates = pd.date_range(start='2021-01-15', periods=time_series.size)
    location_ids = [123, 456, 789, 987, 654, 321]
    s = []
    for location_id in location_ids:
        idx = pd.MultiIndex.from_product([[location_id], dates], names=['location_id', 'date'])
        s.append(pd.Series(time_series, index=idx))
    return pd.concat(s)


def invariant_transform(ts):
    return ts.groupby('location_id').diff().fillna(0).groupby('location_id').cumsum()


def test_make_round_trip_invariant_no_side_effect(time_series):
    ts_copy = time_series.copy(deep=True)
    new_ts = make_round_trip_invariant(time_series)
    assert not new_ts.equals(time_series)
    assert ts_copy.equals(time_series)


def test_make_round_trip_invariant(time_series):
    assert not time_series.equals(invariant_transform(time_series))
    new_ts = make_round_trip_invariant(time_series)
    assert time_series.equals(new_ts.loc[time_series.index])
    assert new_ts.equals(invariant_transform(new_ts))


def test_make_round_trip_invariant_idempotent(time_series):
    assert not time_series.equals(invariant_transform(time_series))
    new_ts = make_round_trip_invariant(time_series)
    new_ts2 = make_round_trip_invariant(new_ts)
    assert new_ts.equals(new_ts2)


@pytest.mark.parametrize('region', [0, 1, 2])
def test_make_round_trip_invariant_interp(time_series, region):
    def _drop_data_in_region(x):
        x.iloc[10*region+3:10*region+8] = np.nan
        return x

    time_series_with_nulls = time_series.groupby('location_id').apply(_drop_data_in_region)
    new_ts = make_round_trip_invariant(time_series_with_nulls)
    assert time_series_with_nulls.dropna().equals(new_ts.loc[time_series_with_nulls.dropna().index])
    assert new_ts.equals(invariant_transform(new_ts))
