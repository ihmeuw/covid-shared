import pandas as pd


def make_round_trip_invariant(cumulative_time_series: pd.Series) -> pd.Series:
    """Drops nulls, interpolates, and adds a leading zero.

    This function drops nulls from the cumulative time series, interpolates
    missing days linearly, and then pads the front of the
    series with a 0 so that the resulting series has the property:

        s == s.groupby('location_id').diff().fillna(0).groupby('location_id').cumsum()

    which is to say we can preserve the counts under conversions between daily
    and cumulative space.

    Parameters
    ----------
    cumulative_time_series
        A series with indexed by location id and date.

    Returns
    -------
    pd.Series
        A series with interior null values interpolated and with a leading
        zero such that transforming to daily and back to cumulative is
        an invariant transformation.

    """
    name = cumulative_time_series.name if cumulative_time_series.name else 'value'
    cumulative_time_series = cumulative_time_series.rename(name)

    data = cumulative_time_series.dropna()

    non_zero_data = data.loc[data != 0.]
    min_date = non_zero_data.reset_index().groupby('location_id').date.min()
    prepend_date = min_date - pd.Timedelta(days=1)
    prepend_idx = prepend_date.reset_index().set_index(['location_id', 'date']).index
    prepend_idx = prepend_idx.difference(data.index)
    prepend = pd.Series(0., index=prepend_idx, name=name)
    data = data.append(prepend).sort_index()

    loc_ids = data.reset_index().location_id.unique()
    final_series = []
    for loc_id in loc_ids:
        s = (data
             .loc[loc_id]
             .asfreq('D')
             .interpolate()
             .reset_index())
        s['location_id'] = loc_id
        final_series.append(s.set_index(['location_id', 'date'])[name])
    return pd.concat(final_series).rename(cumulative_time_series.name).sort_index()
