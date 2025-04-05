import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Load the Excel file
@st.cache_data
def load_data():
    xls = pd.ExcelFile("Region Charts Master.xlsx")
    df = xls.parse('Radar Sa3 Houses')
    return df

df = load_data()

# Select score-based filter columns
score_columns = [
    '10Y Price Change', '1M Price Change', 'Inventory Now', 'Inventory trend',
    'Inventory Forecast', 'DOM', 'Dom Forecast'
]

st.title("PropwealthNext: SA3 Investment Radar Dashboard")

# Sidebar filters
st.sidebar.header("Filter Regions by Score")
selected_scores = {}
for col in score_columns:
    selected_scores[col] = st.sidebar.slider(f"{col}", 1, 5, (1, 5))

# Filter DataFrame based on selected score ranges
filtered_df = df.copy()
for col in score_columns:
    min_val, max_val = selected_scores[col]
    filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]

selected_sa3s = st.multiselect("Select SA3 Regions to Compare:", filtered_df['SA3'].unique())

# Plot radar chart
if selected_sa3s:
    fig = go.Figure()
    for sa3 in selected_sa3s:
        row = filtered_df[filtered_df['SA3'] == sa3][score_columns].iloc[0]
        fig.add_trace(go.Scatterpolar(
            r=row.values,
            theta=score_columns,
            fill='toself',
            name=sa3
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
        showlegend=True,
        title="Radar Chart: SA3 Comparison"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Download CSV
    csv_data = filtered_df[filtered_df['SA3'].isin(selected_sa3s)][['SA3'] + score_columns]
    csv = csv_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Selected Data as CSV",
        data=csv,
        file_name='selected_sa3s.csv',
        mime='text/csv'
    )

    # Download Radar Chart as PDF
    pdf_bytes = pio.to_image(fig, format='pdf')
    st.download_button(
        label="📄 Download Radar Chart as PDF",
        data=pdf_bytes,
        file_name='radar_chart.pdf',
        mime='application/pdf'
    )
else:
    st.info("Please select SA3 regions from the list above.")