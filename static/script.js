 // Utility functions
 const formatNumber = (num) => new Intl.NumberFormat().format(num);
 const formatDecimal = (num) => Number(num).toFixed(1);

 // Initialize dashboard
 document.addEventListener('DOMContentLoaded', async () => {
     try {
         const response = await fetch('/api/data');
         if (!response.ok) throw new Error('Failed to fetch data');
         
         const data = await response.json();
         if (data.error) throw new Error(data.error);

         // Update metrics
         document.getElementById('total-accidents').textContent = formatNumber(data.metrics.total_accidents);
         document.getElementById('avg-age').textContent = formatDecimal(data.metrics.avg_age);
         document.getElementById('peak-hour').textContent = `${data.metrics.peak_hour}:00`;
         document.getElementById('vehicle-active').textContent = formatNumber(data.metrics.vehicle_active);

         // Initialize charts
         const accidentsTrend = JSON.parse(data.accidents_trend);
         Plotly.newPlot('accidents-trend', accidentsTrend.data, {
             ...accidentsTrend.layout,
             font: {family: 'Space Grotesk'},
             hoverlabel: {font: {family: 'Space Grotesk'}}
         }, {
             responsive: true,
             displayModeBar: false
         });

         // Hourly patterns chart
         const hourlyData = data.analytics.hourly_patterns;
         const hourlyLayout = {
             template: 'plotly_dark',
             plot_bgcolor: 'rgba(0,0,0,0)',
             paper_bgcolor: 'rgba(0,0,0,0)',
             font: {family: 'Space Grotesk', color: 'white'},
             xaxis: {
                 title: 'Hour of Day',
                 gridcolor: '#334155',
                 tickmode: 'array',
                 ticktext: hourlyData.hours.map(h => `${h}:00`),
                 tickvals: hourlyData.hours
             },
             yaxis: {
                 title: 'Number of Accidents',
                 gridcolor: '#334155'
             },
             annotations: hourlyData.data_available ? [] : [{
                 text: 'Hourly data not available',
                 xref: 'paper',
                 yref: 'paper',
                 x: 0.5,
                 y: 0.5,
                 showarrow: false,
                 font: {
                     size: 16,
                     color: '#94a3b8'
                 }
             }]
         };

         Plotly.newPlot('hourly-patterns', [{
             x: hourlyData.hours,
             y: hourlyData.counts,
             type: 'bar',
             marker: {
                 color: hourlyData.is_daylight.map(isDaylight => 
                     isDaylight ? '#22d3ee' : '#ec4899'
                 )
             },
             name: 'Accidents'
         }], hourlyLayout, {
             responsive: true,
             displayModeBar: false
         });

         // Update day/night statistics
         document.getElementById('day-accidents').textContent = formatNumber(hourlyData.day_accidents);
         document.getElementById('night-accidents').textContent = formatNumber(hourlyData.night_accidents);

         // License demographics
         const licenseData = data.analytics.license_demographics;
         
         // Create two-column bar chart for nationality and license types
         const nationalityData = Object.entries(licenseData.nationality);
         const licenseTypesData = Object.entries(licenseData.license_types);
         
         Plotly.newPlot('license-demographics', [
             {
                 type: 'bar',
                 x: nationalityData.map(([group]) => group),
                 y: nationalityData.map(([_, count]) => count),
                 name: 'By Nationality',
                 marker: { color: '#22d3ee' }
             },
             {
                 type: 'bar',
                 x: licenseTypesData.map(([type]) => type),
                 y: licenseTypesData.map(([_, count]) => count),
                 name: 'By License Type',
                 marker: { color: '#ec4899' },
                 visible: false
             }
         ], {
             template: 'plotly_dark',
             plot_bgcolor: 'rgba(0,0,0,0)',
             paper_bgcolor: 'rgba(0,0,0,0)',
             font: {family: 'Space Grotesk', color: 'white'},
             margin: {t: 30, r: 20, b: 40, l: 60},
             xaxis: {
                 title: '',
                 gridcolor: '#334155',
                 tickangle: 45
             },
             yaxis: {
                 title: 'Number of License Holders',
                 gridcolor: '#334155'
             },
             updatemenus: [{
                 type: 'buttons',
                 direction: 'right',
                 x: 0.5,
                 y: 1.1,
                 xanchor: 'center',
                 yanchor: 'top',
                 buttons: [
                     {
                         args: [{'visible': [true, false]}],
                         label: 'Nationality',
                         method: 'restyle'
                     },
                     {
                         args: [{'visible': [false, true]}],
                         label: 'License Types',
                         method: 'restyle'
                     }
                 ],
                 font: {family: 'Space Grotesk'},
                 bgcolor: '#1e293b',
                 bordercolor: '#475569'
             }]
         }, {
             responsive: true,
             displayModeBar: false
         });

         // Vehicle status overview
         const vehicleStatusData = Object.entries(data.analytics.vehicle_trends.status_breakdown);
         Plotly.newPlot('vehicle-status', [{
             type: 'bar',
             x: vehicleStatusData.map(([status]) => status),
             y: vehicleStatusData.map(([_, count]) => count),
             marker: {
                 color: vehicleStatusData.map((_, index) => 
                     `rgba(34, 211, 238, ${1 - index * 0.2})`
                 )
             }
         }], {
             template: 'plotly_dark',
             plot_bgcolor: 'rgba(0,0,0,0)',
             paper_bgcolor: 'rgba(0,0,0,0)',
             font: {family: 'Space Grotesk', color: 'white'},
             margin: {t: 10, r: 10, b: 60, l: 60},
             xaxis: {
                 title: 'Vehicle Status',
                 gridcolor: '#334155',
                 tickangle: 45
             },
             yaxis: {
                 title: 'Number of Vehicles',
                 gridcolor: '#334155'
             }
         }, {
             responsive: true,
             displayModeBar: false
         });

         // Vehicle age analysis
         const vehicleAge = Object.entries(data.analytics.vehicle_trends.age_distribution);
         Plotly.newPlot('vehicle-age', [{
             type: 'pie',
             labels: vehicleAge.map(([age]) => age),
             values: vehicleAge.map(([_, count]) => count),
             hole: 0.4,
             marker: {
                 colors: ['#22d3ee', '#38bdf8', '#60a5fa', '#818cf8', '#ec4899']
             }
         }], {
             template: 'plotly_dark',
             plot_bgcolor: 'rgba(0,0,0,0)',
             paper_bgcolor: 'rgba(0,0,0,0)',
             font: {family: 'Space Grotesk', color: 'white'},
             showlegend: true,
             legend: {orientation: 'h', y: -0.2}
         }, {
             responsive: true,
             displayModeBar: false
         });

         // Hide loading, show content
         document.getElementById('loading').style.display = 'none';
         document.getElementById('content').style.display = 'block';
     } catch (error) {
         console.error('Dashboard initialization error:', error);
         const errorContainer = document.getElementById('error-container');
         errorContainer.classList.remove('hidden');
         errorContainer.classList.add('error-message');
         errorContainer.textContent = 'Error loading dashboard data. Please try refreshing the page.';
         document.getElementById('loading').style.display = 'none';
     }
 });

 // Responsive charts
 let resizeTimer;
 window.addEventListener('resize', () => {
     clearTimeout(resizeTimer);
     resizeTimer = setTimeout(() => {
         try {
             const charts = ['accidents-trend', 'age-distribution', 'vehicle-status'];
             charts.forEach(chartId => {
                 const chart = document.getElementById(chartId);
                 if (chart && chart.data) {
                     Plotly.Plots.resize(chart);
                 }
             });
         } catch (error) {
             console.error('Error resizing charts:', error);
         }
     }, 250);
 });

 // Error handling for Plotly
 window.addEventListener('error', (event) => {
     if (event.error.message.includes('Plotly')) {
         console.error('Plotly error:', event.error);
         const errorContainer = document.getElementById('error-container');
         errorContainer.classList.remove('hidden');
         errorContainer.classList.add('error-message');
         errorContainer.textContent = 'Error displaying charts. Please try refreshing the page.';
     }
 });