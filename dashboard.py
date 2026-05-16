import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Akola Schools Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Aurora Premium Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Main Background & Text */
    .stApp {
        background: radial-gradient(circle at top left, #120A2A, #060814 60%, #03040A);
        color: #F1F5F9;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Top padding reduction */
    .css-18e3th9 {
        padding-top: 2rem;
    }
    
    /* KPI Cards Glassmorphism */
    .kpi-card {
        background: rgba(20, 25, 45, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .kpi-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 50px rgba(139, 92, 246, 0.2);
        border-color: rgba(139, 92, 246, 0.4);
    }
    .kpi-title {
        font-size: 0.95rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        background: linear-gradient(135deg, #38BDF8, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 12, 24, 0.95);
        border-right: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)


# --- DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "School.xlsx"
    df_main = pd.read_excel(file_path, sheet_name='Cleaned Data')
    df_digital = pd.read_excel(file_path, sheet_name='Digital Presence')
    
    # Data Cleaning for Maps
    df_main['Latitude'] = pd.to_numeric(df_main['Latitude'], errors='coerce')
    df_main['Longitude'] = pd.to_numeric(df_main['Longitude'], errors='coerce')
    df_main['Rating'] = pd.to_numeric(df_main['Rating'], errors='coerce')
    
    return df_main, df_digital

try:
    df_main, df_digital = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure the Excel file is correctly formatted and located at the correct path.")
    st.stop()


# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/330/330058.png", width=60) # Placeholder generic premium icon
st.sidebar.markdown("## ⚙️ Filter Controls")

# Category Filter
categories = sorted(df_main['Category'].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Select Categories", categories, default=None)

# Rating Filter
min_rating = float(df_main['Rating'].min(skipna=True)) if not df_main['Rating'].isna().all() else 0.0
max_rating = float(df_main['Rating'].max(skipna=True)) if not df_main['Rating'].isna().all() else 5.0
if np.isnan(min_rating): min_rating = 0.0
if np.isnan(max_rating): max_rating = 5.0

rating_range = st.sidebar.slider("Rating Range", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating), step=0.1)

# Apply Filters
mask = (df_main['Rating'] >= rating_range[0]) & (df_main['Rating'] <= rating_range[1])
# Include schools without ratings if the full range is selected
if rating_range[0] == min_rating and rating_range[1] == max_rating:
    mask = mask | df_main['Rating'].isna()

if selected_categories:
    mask = mask & df_main['Category'].isin(selected_categories)
    
filtered_main = df_main[mask]
filtered_digital = df_digital[df_digital['Name'].isin(filtered_main['Name'])]


# --- HEADER ---
st.markdown("<h1 style='font-size: 3.5rem; margin-bottom: 0;'>🏫 Akola Schools <span style='background: linear-gradient(135deg, #38BDF8, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Market Intelligence</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8; font-size: 1.1rem; margin-top: 5px; margin-bottom: 40px;'>A state-of-the-art interactive overview of educational institutions in the region.</p>", unsafe_allow_html=True)


# --- KPI METRICS ---
def create_kpi(title, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

with col1:
    st.markdown(create_kpi("Total Schools", len(filtered_main)), unsafe_allow_html=True)
with col2:
    avg_rating = filtered_main['Rating'].mean()
    avg_rating_str = f"{avg_rating:.1f} ★" if pd.notnull(avg_rating) else "N/A"
    st.markdown(create_kpi("Avg Rating", avg_rating_str), unsafe_allow_html=True)
with col3:
    top_category = filtered_main['Category'].mode()[0] if not filtered_main['Category'].empty else "None"
    st.markdown(create_kpi("Top Category", top_category), unsafe_allow_html=True)
with col4:
    website_count = len(filtered_digital[filtered_digital['Website'] == 'Yes'])
    web_perc = f"{(website_count/len(filtered_main))*100:.0f}%" if len(filtered_main) > 0 else "0%"
    st.markdown(create_kpi("Web Presence", web_perc), unsafe_allow_html=True)

with col5:
    phone_count = len(filtered_digital[filtered_digital['Phone'] == 'Yes'])
    phone_perc = f"{(phone_count/len(filtered_main))*100:.0f}%" if len(filtered_main) > 0 else "0%"
    st.markdown(create_kpi("Phone Contact", phone_perc), unsafe_allow_html=True)
with col6:
    email_count = len(filtered_digital[filtered_digital['Email'] == 'Yes'])
    email_perc = f"{(email_count/len(filtered_main))*100:.0f}%" if len(filtered_main) > 0 else "0%"
    st.markdown(create_kpi("Email Setup", email_perc), unsafe_allow_html=True)
with col7:
    fb_count = len(filtered_digital[filtered_digital['Facebook'] == 'Yes'])
    fb_perc = f"{(fb_count/len(filtered_main))*100:.0f}%" if len(filtered_main) > 0 else "0%"
    st.markdown(create_kpi("Facebook", fb_perc), unsafe_allow_html=True)
with col8:
    insta_count = len(filtered_digital[filtered_digital['Instagram'] == 'Yes'])
    insta_perc = f"{(insta_count/len(filtered_main))*100:.0f}%" if len(filtered_main) > 0 else "0%"
    st.markdown(create_kpi("Instagram", insta_perc), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- ROW 1: CHARTS ---
r1c1, r1c2 = st.columns([2, 1])

with r1c1:
    st.markdown("### 🏆 Top Rated Schools")
    # Take top 10 schools by rating
    top_schools = filtered_main.dropna(subset=['Rating']).sort_values('Rating', ascending=False).head(10)
    
    if not top_schools.empty:
        fig_top = px.bar(
            top_schools,
            x='Rating',
            y='Name',
            orientation='h',
            color='Rating',
            color_continuous_scale=['#4C1D95', '#8B5CF6', '#38BDF8'],
            text='Rating'
        )
        fig_top.update_layout(
            xaxis_title="Rating (Out of 5)",
            yaxis_title="",
            yaxis={'categoryorder':'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E6ED', family='Outfit'),
            margin=dict(l=0, r=0, t=30, b=0),
            coloraxis_showscale=False
        )
        fig_top.update_traces(
            texttemplate='<b>%{text:.1f} ★</b>', 
            textposition='inside',
            insidetextanchor='end',
            marker_line_width=0
        )
        fig_top.update_xaxes(range=[0, 5.2], showgrid=False)
        fig_top.update_yaxes(showgrid=False)
        st.plotly_chart(fig_top, width='stretch')
    else:
        st.info("No rating data available for the current filter.")

with r1c2:
    st.markdown("### 📊 Category Mix")
    cat_counts = filtered_main['Category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    
    fig_donut = px.pie(
        cat_counts, 
        values='Count', 
        names='Category', 
        hole=0.6,
        color_discrete_sequence=['#38BDF8', '#818CF8', '#C084FC', '#F472B6', '#2DD4BF']
    )
    fig_donut.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94A3B8', family='Outfit')
    )
    # Add text in center
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, width='stretch')


# --- ROW 2: DIGITAL PRESENCE & DATA TABLE ---
st.markdown("<br><hr style='border-color: #2D3748;'>", unsafe_allow_html=True)
st.markdown("### 🌐 Digital Footprint Analysis")

r2c1, r2c2 = st.columns([1, 1])

with r2c1:
    # Prepare data for digital presence bar chart
    presence_cols = ['Website', 'Phone', 'Email', 'Facebook', 'Instagram', 'Twitter']
    presence_counts = []
    
    for col in presence_cols:
        count = len(filtered_digital[filtered_digital[col] == 'Yes'])
        presence_counts.append({'Channel': col, 'Count': count})
        
    df_presence = pd.DataFrame(presence_counts)
    
    fig_bar = px.bar(
        df_presence, 
        x='Count', 
        y='Channel', 
        orientation='h',
        color='Count',
        color_continuous_scale=['#4C1D95', '#38BDF8']
    )
    fig_bar.update_layout(
        xaxis_title="Number of Schools",
        yaxis_title="",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E6ED', family='Outfit'),
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_showscale=False
    )
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=False)
    st.plotly_chart(fig_bar, width='stretch')

with r2c2:
    st.markdown("##### Detailed Dataset View")
    st.markdown("<span style='color: #A0AEC0; font-size: 0.9rem;'>Explore the raw data for the filtered schools.</span>", unsafe_allow_html=True)
    st.dataframe(
        filtered_main[['Name', 'Category', 'Rating', 'Address', 'Phone']].reset_index(drop=True),
        width='stretch',
        height=300
    )

st.markdown("<div style='text-align: center; color: #4A5568; margin-top: 50px; font-size: 0.8rem;'>Built with precision for Akola Intelligence</div>", unsafe_allow_html=True)
