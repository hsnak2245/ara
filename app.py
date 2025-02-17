from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

app = Flask(__name__)

# Custom filter for number formatting
@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(value)

def load_and_filter_data():
    # Load the parquet files
    acc_df = pd.read_parquet('data/acc.parquet')
    liz_df = pd.read_parquet('data/liz.parquet')
    veh_df = pd.read_parquet('data/veh.parquet')
    
    # Filter for 2020-2024
    acc_df = acc_df[acc_df['ACCIDENT_YEAR'].between(2020, 2024)]
    
    return acc_df, liz_df, veh_df

def create_accidents_trend(acc_df):
    yearly_accidents = acc_df['ACCIDENT_YEAR'].value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=yearly_accidents.index.astype(str),
            y=yearly_accidents.values,
            mode='lines+markers',
            line=dict(color='#6366f1', width=2),
            marker=dict(size=8)
        )
    ])
    
    fig.update_layout(
        title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa'),
        showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            title='Year',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#262626',
            title='Number of Accidents',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        )
    )
    
    return fig

def create_nationality_distribution(acc_df):
    nationality_counts = acc_df['NATIONALITY_GROUP_OF_ACCIDENT_'].value_counts().head(5)
    
    fig = go.Figure(data=[
        go.Bar(
            x=nationality_counts.index,
            y=nationality_counts.values,
            marker_color='#6366f1'
        )
    ])
    
    fig.update_layout(
        title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa'),
        showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            title='Nationality Group',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#262626',
            title='Number of Accidents',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        )
    )
    
    return fig

def create_hourly_pattern(acc_df):
    # Convert accident time to hour
    acc_df['Hour'] = acc_df['ACCIDENT_TIME'].str.extract('(\d+)').astype(float)
    hourly_accidents = acc_df['Hour'].value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=hourly_accidents.index,
            y=hourly_accidents.values,
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.2)',
            line=dict(color='#6366f1', width=2)
        )
    ])
    
    fig.update_layout(
        title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa'),
        showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            title='Hour of Day',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#262626',
            title='Number of Accidents',
            titlefont=dict(color='#9ca3af'),
            tickfont=dict(color='#9ca3af')
        )
    )
    
    return fig

@app.route('/')
def index():
    acc_df, liz_df, veh_df = load_and_filter_data()
    
    # Calculate metrics
    metrics = {
        'total_accidents': len(acc_df),
        'total_licenses': len(liz_df),
        'total_vehicles': len(veh_df)
    }
    
    return render_template('dashboard.html',
                         metrics=metrics,
                         accidents_trend=create_accidents_trend(acc_df).to_json(),
                         nationality_dist=create_nationality_distribution(acc_df).to_json(),
                         hourly_pattern=create_hourly_pattern(acc_df).to_json())

if __name__ == '__main__':
    app.run(debug=True)