from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from functools import lru_cache
from sklearn.linear_model import LinearRegression
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

@lru_cache(maxsize=32)
def load_and_filter_data():
    """Load and filter data from parquet files with error handling."""
    try:
        acc_df = pd.read_parquet('data/acc.parquet')
        liz_df = pd.read_parquet('data/liz.parquet', 
                               columns=['LICENSE_TYPE', 'BIRTHYEAR', 'NATIONALITY_GROUP', 'TOTAL'])
        veh_df = pd.read_parquet('data/veh.parquet',
                               columns=['VEHICLE_STATUS', 'BIRTH_YEAR', 'TOTAL'])
        
        # Filter and process with data validation
        current_year = datetime.now().year
        acc_df = acc_df[acc_df['ACCIDENT_YEAR'].between(2020, current_year)].copy()
        acc_df['AGE'] = current_year - acc_df['BIRTH_YEAR_OF_ACCIDENT_PERPETR']
        
        return acc_df, liz_df, veh_df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def analyze_hourly_patterns(acc_df):
    """Analyze accident patterns by hour with day/night segmentation."""
    try:
        # Check if hour information is available
        if 'Hour' not in acc_df.columns and 'ACCIDENT_HOUR' not in acc_df.columns:
            # Provide default data if hour information is not available
            hours = list(range(24))
            counts = [0] * 24  # Empty data for all hours
            return {
                'hours': hours,
                'counts': counts,
                'is_daylight': [6 <= h <= 18 for h in hours],
                'day_accidents': 0,
                'night_accidents': 0,
                'data_available': False
            }
        
        # Get the correct hour column
        hour_col = 'Hour' if 'Hour' in acc_df.columns else 'ACCIDENT_HOUR'
        
        # Ensure hours are in correct range
        acc_df[hour_col] = pd.to_numeric(acc_df[hour_col], errors='coerce')
        valid_hours = acc_df[hour_col].between(0, 23)
        hourly_data = acc_df.loc[valid_hours, hour_col].value_counts().sort_index()
        
        # Fill in missing hours with zeros
        all_hours = pd.Series(0, index=range(24))
        hourly_data = hourly_data.add(all_hours, fill_value=0)
        
        is_daylight = lambda hour: 6 <= hour <= 18
        day_accidents = hourly_data[hourly_data.index.map(is_daylight)].sum()
        night_accidents = hourly_data[~hourly_data.index.map(is_daylight)].sum()
        
        return {
            'hours': hourly_data.index.tolist(),
            'counts': hourly_data.values.tolist(),
            'is_daylight': [is_daylight(h) for h in hourly_data.index],
            'day_accidents': int(day_accidents),
            'night_accidents': int(night_accidents),
            'data_available': True
        }
    except Exception as e:
        logger.error(f"Error in hourly analysis: {str(e)}")
        # Return safe default data
        hours = list(range(24))
        return {
            'hours': hours,
            'counts': [0] * 24,
            'is_daylight': [6 <= h <= 18 for h in hours],
            'day_accidents': 0,
            'night_accidents': 0,
            'data_available': False
        }

def analyze_license_demographics(liz_df):
    """Analyze license holder demographics."""
    try:
        # Create age groups with explicit observed=True
        age_groups = pd.cut(liz_df['BIRTHYEAR'].map(lambda x: datetime.now().year - x),
                           bins=[0, 25, 35, 45, 55, 65, 100],
                           labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
        
        demographics = {
            'age_groups': liz_df.groupby(age_groups, observed=True)['TOTAL'].sum().to_dict(),
            'nationality': liz_df.groupby('NATIONALITY_GROUP')['TOTAL'].sum().nlargest(5).to_dict(),
            'license_types': liz_df.groupby('LICENSE_TYPE')['TOTAL'].sum().nlargest(5).to_dict()
        }
        return demographics
    except Exception as e:
        logger.error(f"Error in license demographics: {str(e)}")
        return {
            'age_groups': {},
            'nationality': {},
            'license_types': {}
        }

def analyze_vehicle_trends(veh_df):
    """Analyze vehicle registration trends and status."""
    try:
        current_year = datetime.now().year
        vehicle_age = current_year - veh_df['BIRTH_YEAR']
        age_groups = pd.cut(vehicle_age,
                           bins=[-float('inf'), 5, 10, 15, 20, float('inf')],
                           labels=['0-5 years', '6-10 years', '11-15 years', '16-20 years', '20+ years'])
        
        vehicle_analysis = {
            'age_distribution': veh_df.groupby(age_groups, observed=True)['TOTAL'].sum().to_dict(),
            'status_breakdown': veh_df.groupby('VEHICLE_STATUS')['TOTAL'].sum().to_dict()
        }
        return vehicle_analysis
    except Exception as e:
        logger.error(f"Error in vehicle trends: {str(e)}")
        return {
            'age_distribution': {},
            'status_breakdown': {}
        }

def create_advanced_visualizations(acc_df, liz_df, veh_df):
    """Create advanced visualizations with error handling and input validation."""
    try:
        # Time Series Forecasting
        yearly = acc_df['ACCIDENT_YEAR'].value_counts().sort_index()
        if len(yearly) < 2:
            raise ValueError("Insufficient data for forecasting")
            
        X = np.array(yearly.index).reshape(-1, 1)
        y = yearly.values
        model = LinearRegression().fit(X, y)
        
        # Only forecast through 2024
        future_years = np.array([2024]).reshape(-1, 1)
        forecast = model.predict(future_years)
        
        # Age Distribution Analysis with validation
        acc_df['AGE'] = pd.to_numeric(acc_df['AGE'], errors='coerce').clip(18, 80)
        veh_df['OWNER_AGE'] = pd.to_numeric(
            datetime.now().year - veh_df['BIRTH_YEAR'], 
            errors='coerce'
        ).clip(18, 100)
        
        # Vehicle Status Distribution with cleaning
        vehicle_status = veh_df['VEHICLE_STATUS'].fillna('UNKNOWN').value_counts()
        
        # Get additional analytics
        hourly_patterns = analyze_hourly_patterns(acc_df)
        license_demographics = analyze_license_demographics(liz_df)
        vehicle_trends = analyze_vehicle_trends(veh_df)
        
        return {
            'forecast_data': {
                'years': yearly.index.tolist(),
                'values': yearly.values.tolist(),
                'future_years': future_years.flatten().tolist(),
                'forecast': forecast.tolist()
            },
            'age_distribution': acc_df['AGE'].value_counts().sort_index().to_dict(),
            'owner_age_distribution': veh_df['OWNER_AGE'].value_counts().sort_index().to_dict(),
            'vehicle_status': vehicle_status.to_dict(),
            'hourly_patterns': hourly_patterns,
            'license_demographics': license_demographics,
            'vehicle_trends': vehicle_trends
        }
    except Exception as e:
        logger.error(f"Error creating visualizations: {str(e)}")
        raise

def create_accidents_trend(forecast_data):
    """Create accident trend visualization with proper error handling."""
    try:
        fig = go.Figure()
        
        # Actual data
        fig.add_trace(go.Scatter(
            x=forecast_data['years'],
            y=forecast_data['values'],
            name='Actual',
            line=dict(color='#22d3ee', width=3, shape='spline'),
            mode='lines+markers',
            marker=dict(size=8, color='#22d3ee')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_data['future_years'],
            y=forecast_data['forecast'],
            name='Forecast',
            line=dict(color='#ec4899', width=3, dash='dot', shape='spline'),
            mode='lines+markers',
            marker=dict(size=8, symbol='x', color='#ec4899')
        ))
        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Space Grotesk', color='white'),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=40, b=40, l=50, r=50),
            xaxis=dict(
                title='Year',
                gridcolor='#334155',
                showgrid=True,
                tickformat='d'
            ),
            yaxis=dict(
                title='Accidents',
                gridcolor='#334155',
                showgrid=True
            ),
            height=400
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating accident trend: {str(e)}")
        raise

@app.route('/api/data')
def get_data():
    """API endpoint for fetching dashboard data."""
    try:
        acc_df, liz_df, veh_df = load_and_filter_data()
        analytics = create_advanced_visualizations(acc_df, liz_df, veh_df)
        
        metrics = {
            'total_accidents': int(len(acc_df)),
            'avg_age': float(acc_df['AGE'].mean()),
            'peak_hour': int(acc_df.get('Hour', pd.Series([0])).mode().iloc[0]),
            'vehicle_active': int(veh_df[veh_df['VEHICLE_STATUS'] == 'ACTIVE'].shape[0])
        }
        
        return jsonify({
            'metrics': metrics,
            'accidents_trend': create_accidents_trend(analytics['forecast_data']).to_json(),
            'analytics': analytics
        })
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def index():
    """Render the dashboard template."""
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=False)  # Set to False in production