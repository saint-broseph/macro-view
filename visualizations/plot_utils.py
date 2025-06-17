import plotly.express as px

def line_chart(df, title, x="Year", y="Value"):
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        template="plotly_white"
    )
    return fig

def multi_country_chart(df, title, x="Year", y="Value", color="Country"):
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=f"{title} – Multi-Country Comparison",
        markers=True
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        legend_title="Country",
        template="plotly_white"
    )
    return fig
