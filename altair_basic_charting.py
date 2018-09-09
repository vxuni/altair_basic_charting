import altair as alt
import pandas as pd
from typing import Tuple


open_close_color = alt.condition("datum.Open < datum.Close",
                                 alt.value("#06982d"),
                                 alt.value("#ae1325"))

def build_candlestick_charts(eth_price: pd.DataFrame) -> Tuple[alt.Chart, alt.Chart, alt.Chart]:
    """Given coinmarketcap price table, build candlestick + volume chart."""

    # adapted from https://altair-viz.github.io/gallery/candlestick_chart.html

    base = alt.Chart(eth_price).encode(x='Date')

    rule = base.mark_rule().encode(
        y=alt.Y(
            'Low',
            scale=alt.Scale(zero=False),
            axis=alt.Axis(title='Price')
        ),
        y2=alt.Y2('High'),
        color=open_close_color
    )

    bar = base.mark_bar().encode(
        y='Open',
        y2='Close',
        color=open_close_color
    )

    volume: alt.Chart = base.properties(height=100).mark_bar().encode(
        y=alt.Y(
            'Volume',
            # scale: map from domain to range
            # zero=False: don't include 0 baseline value
            scale=alt.Scale(zero=False)
        )
    )

    return rule, bar, volume

def pan_zoom_vconcat(rule: alt.Chart, bar: alt.Chart, volume: alt.Chart, method=0) -> alt.VConcatChart:
    """Build composite chart with linked pan and zoom."""

    # had to dig into vega-lite documentation to figure this out:
    # https://vega.github.io/vega-lite/docs/bind.html#scale-binding

    if method == 0:
        combined = ((rule + bar).interactive() & volume).resolve_scale(x='shared')

    else:
        scales = alt.selection_interval(bind='scales')
        candlesticks = rule.add_selection(scales) + bar
        # & == alt.vconcat
        combined = (candlesticks & volume).resolve_scale(x='shared')

    return combined
