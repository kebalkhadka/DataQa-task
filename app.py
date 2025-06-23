import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# --- Set Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("Data QA Dashboard")
st.write("Generated on June 22, 2025, 11:06 PM +0545")

# --- Cache processed data ---
@st.cache_data
def load_processed_data():
    df = pd.read_csv('D:/BigData/data assesment/data/Dataset - Junior Data QA Analyst.csv', encoding='utf-8')
    current_date = datetime(2025, 6, 22, 23, 6)
    df['dob'] = df['dob'].astype(str).replace('nan', '')
    df['age'] = df['dob'].apply(lambda x: current_date.year - int(x) if x.isdigit() else float('nan'))

    max_items = 50
    if len(df['post_code'].unique()) > max_items:
        top_postcodes = df['post_code'].value_counts().head(max_items).index
        df = df[df['post_code'].isin(top_postcodes)]

    return df

with st.spinner("Loading and processing data..."):
    df = load_processed_data()

# --- Generate Visualizations ---

# 1. Age Histogram
age_hist = px.histogram(df, x='age', nbins=100, title='Age Distribution',
                        labels={'age': 'Age (Years)'}, height=400)
age_hist.update_layout(bargap=0.1, margin=dict(l=40, r=40, t=60, b=40),
                       hovermode='x unified', hoverlabel=dict(bgcolor="white", font_size=12))

# 2. Postcode Bar
postcode_counts = df['post_code'].value_counts().reset_index()
postcode_counts.columns = ['post_code', 'count']
bar_postcode = px.bar(postcode_counts, x='post_code', y='count', title='Record Counts by Postcode',
                      labels={'post_code': 'Postcode', 'count': 'Number of Records'}, height=400)
bar_postcode.update_traces(hovertemplate='Postcode: %{x}<br>Records: %{y}<extra></extra>')
bar_postcode.update_layout(margin=dict(l=40, r=40, t=60, b=40), hovermode='x unified',
                           hoverlabel=dict(bgcolor="white", font_size=12),
                           xaxis=dict(type='category', tickangle=45))

# 3. Gender Bar
gender_counts = df['gender'].value_counts().reset_index()
gender_counts.columns = ['gender', 'count']
bar_gender = px.bar(gender_counts, x='gender', y='count', title='Gender Distribution',
                    labels={'gender': 'Gender', 'count': 'Number of Records'}, height=400)
bar_gender.update_traces(hovertemplate='Gender: %{x}<br>Records: %{y}<extra></extra>')
bar_gender.update_layout(margin=dict(l=40, r=40, t=60, b=40), hovermode='x unified',
                         hoverlabel=dict(bgcolor="white", font_size=12))

# 4. Missing Data Heatmap
missing_data = df.isnull().astype(int)
heatmap = go.Figure(data=go.Heatmap(z=missing_data.T.values, x=df.index, y=missing_data.columns,
                                    colorscale='Viridis', showscale=True))
heatmap.update_layout(title='Missing Data Heatmap', xaxis_title='Record Index', yaxis_title='Fields',
                      height=600, margin=dict(l=40, r=40, t=60, b=40), hovermode='closest',
                      hoverlabel=dict(bgcolor="white", font_size=12))

# 5. Insurance Completeness Bar
insurance_cols = [
    'Spitalzusatzversicherung', 'Franchise', 'Ambulante Zusatzversicherung',
    'Zahnbehandlungen', 'Unfallzusatz in den Zusatzversicherungen',
    'Zusatzversicherung', 'Zusatzversicherung 1', 'Zusatzversicherung 2'
]
insurance_counts = df[insurance_cols].notnull().sum().reset_index()
insurance_counts.columns = ['Field', 'Non-Null Count']
stacked_bar = px.bar(insurance_counts, x='Field', y='Non-Null Count',
                     title='Non-Null Counts for Insurance Fields',
                     labels={'Field': 'Insurance Field', 'Non-Null Count': 'Number of Non-Null Records'}, height=400)
stacked_bar.update_traces(hovertemplate='Field: %{x}<br>Non-Null: %{y}<extra></extra>')
stacked_bar.update_layout(xaxis_tickangle=45, margin=dict(l=40, r=40, t=60, b=40),
                          hovermode='x unified', hoverlabel=dict(bgcolor="white", font_size=12))

# 6. Box Plot - Age by Postcode
box_plot = px.box(df, x='post_code', y='age', title='Age Distribution by Postcode',
                  labels={'post_code': 'Postcode', 'age': 'Age (Years)'}, height=400)
box_plot.update_traces(hovertemplate='Postcode: %{x}<br>Age: %{y}<extra></extra>')
box_plot.update_layout(margin=dict(l=40, r=40, t=60, b=40), hovermode='x unified',
                       hoverlabel=dict(bgcolor="white", font_size=12),
                       xaxis=dict(type='category', tickangle=45))

# --- Pages Dictionary ---
pages = {
    "Age Distribution": age_hist,
    "Postcode Records": bar_postcode,
    "Gender Distribution": bar_gender,
    "Missing Data": heatmap,
    "Insurance Completeness": stacked_bar,
    "Age by Postcode": box_plot,
}

# --- Page Selection ---
page = st.radio("Select Visualization:", tuple(pages.keys()))

# --- Display Chart ---
st.subheader(page)
with st.spinner("Loading chart..."):
    chart = pages.get(page)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("Chart not found!")

# --- Clean Data Summary Table (Auto After Every Chart) ---
st.markdown("### 📊 Data Summary")
summary_table = []
total_rows = len(df)

for col in df.columns:
    missing = df[col].isnull().sum()
    available = total_rows - missing
    available_pct = round(available / total_rows * 100, 2)
    missing_pct = round(missing / total_rows * 100, 2)

    summary_table.append({
        "Field": col,
        "Available Count": available,
        "Missing Count": missing,
        "Available %": f"{available_pct}%",
        "Missing %": f"{missing_pct}%",
    })

summary_df = pd.DataFrame(summary_table)
st.dataframe(summary_df, use_container_width=True)

# --- Refresh Button ---
if st.button("Refresh Data"):
    st.experimental_rerun()
