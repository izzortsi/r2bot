from plotly.subplots import make_subplots
import plotly.graph_objects as go

def plot_single_atr_grid(df, atr, atr_grid, close_ema, hist):
    
    
    fig = make_subplots(rows=3, cols=4,
        specs=[[{'rowspan': 2, 'colspan': 3}, None, None, {'rowspan': 2}],
        [None, None, None, None],
        [{'colspan': 3}, None, None, {}]],
        vertical_spacing=0.075,
        horizontal_spacing=0.08,
        shared_xaxes=True,
        )
    # fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    # %%
    kl_go = go.Candlestick(x=df['init_ts'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])


    atr_go = go.Scatter(x=df.init_ts, y=atr,
                                mode="lines",
                                line=go.scatter.Line(color="gray"),
                                showlegend=False)
                                

    ema_go = go.Scatter(x=df.init_ts, y=close_ema,
                                mode="lines",
                                # line=go.scatter.Line(color="blue"),
                                showlegend=True,
                                line=dict(color='royalblue', width=3),
                                opacity=0.75,
                                )

    def hist_colors(hist):
        diffs = hist.diff()
        colors = diffs.apply(lambda x: "green" if x > 0 else "red")
        return colors


    _hist_colors = hist_colors(hist)


    hist_go = go.Scatter(x=df.init_ts, y=hist,
                                mode="lines+markers",
                                # line=go.scatter.Line(color="blue"),
                                showlegend=False,
                                line=dict(color="black", width=3),
                                opacity=1,
                                marker=dict(color=_hist_colors, size=6),
                                )

    def plot_atr_grid(atr_grid, fig):
        for atr_band in atr_grid:
            if sum(atr_band) >= 1.2 * sum(close_ema):
                color = 'red'
            else:
                color = "teal"
            atr_go = go.Scatter(x=df.init_ts, y=atr_band,
                                mode="lines",
                                # line=go.scatter.Line(color="teal"),
                                showlegend=False,
                                line=dict(color=color, width=0.4), 
                                opacity=.8,
                                hoverinfo='skip')
            fig.add_trace(atr_go, row=1, col=1)


    fig.add_trace(kl_go, row=1, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    #fig.update_layout(title_text="___USDT@15m")
    fig.update()

    fig.add_trace(ema_go, row=1, col=1)
    fig.add_trace(hist_go, row=3, col=1)
    
    plot_atr_grid(atr_grid, fig)

    return fig

def plot_symboL_atr_grid(symbol, data):
    fig = plot_single_atr_grid(
        data[symbol]["data_window"], 
        data[symbol]["atr"], 
        data[symbol]["atr_grid"], 
        data[symbol]["close_ema"], 
        data[symbol]["hist"],
    )
    fig.update_layout(title_text=f"{symbol}@{interval}")
    fig.show()
    # return fig

def plot_all_screened(screened_pairs, data):
    for pair in screened_pairs:
        plot_symboL_atr_grid(pair, data)