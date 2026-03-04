import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests

# Set up page configurations for the Executive Summary
st.set_page_config(
    page_title="Executive Summary",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_URL = "https://docs.google.com/spreadsheets/d/1i3Knwzh3I9rklo_8xDxeDVzH8y0aAzG2OayosfPt3mY/export?format=csv"

def get_custom_css():
    return """
    <style>
        /* Modern Gradient background */
        .stApp { 
            background: linear-gradient(135deg, #C8EADD 0%, #f0faf7 100%); 
            background-attachment: fixed;
            color: #0f172a; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Main Container */
        .block-container { 
            padding-top: 3rem !important; 
            max-width: 1400px;
        }
        
        /* Module buttons */
        div.stButton > button {
            background-color: #2b1b54;
            color: #a0a5ce;
            border: 1px solid #452b80;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover, div.stButton > button:focus, div.stButton > button:active {
            background-color: #3f2a7a;
            border-color: #5c6bc0;
            color: white;
            box-shadow: 0 4px 10px rgba(63, 81, 181, 0.4);
        }
        
        /* Dark KPI Cards for Purple Theme */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e1a3b, #2c2456);
            border: none;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            height: 100%;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: transform 0.2s;
            overflow: hidden;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
        }
        
        /* Metric Label */
        div[data-testid="stMetricLabel"] {
            justify-content: center;
            width: 100%;
        }
        div[data-testid="stMetricLabel"] > div > p {
            color: #d1d5db !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            text-align: center;
        }
        
        /* Metric Value (Big Numbers, White) */
        div[data-testid="stMetricValue"] {
            display: flex;
            justify-content: center;
            width: 100%;
            word-wrap: break-word;
            overflow-wrap: break-word;
            text-align: center;
        }
        div[data-testid="stMetricValue"] > div {
            color: #ffffff !important; 
            font-size: clamp(24px, 2.5vw, 36px) !important;
            font-weight: 800 !important;
            line-height: 1.2 !important;
            white-space: normal !important;
            text-align: center !important;
        }
        
        /* Sidebar Professional Styling */
        section[data-testid="stSidebar"], [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e1a3b, #2c2456) !important;
            height: 100vh !important;
            border-right: none !important;
        }
        
        section[data-testid="stSidebar"] *, [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* Active Sidebar page highlight */
        [data-testid="stSidebarNavItems"] > li > div > a[aria-current="page"] {
            background-color: rgba(96, 196, 138, 0.15) !important;
            border-radius: 8px !important;
            margin: 0 8px !important;
        }
        [data-testid="stSidebarNavItems"] > li > div > a[aria-current="page"] span {
            color: #60C48A !important;
            font-weight: 700 !important;
        }
    </style>
    """

def inject_active_button_style(active_module):
    # Depending on which module is selected, target that specific button index natively
    index_map = {'All': 1, 'Backend': 2, 'Flutter': 3, 'Frontend': 4}
    active_index = index_map.get(active_module, 1)
    
    css = f"""
    <style>
        /* Inject active state to the specific button */
        div[data-testid="column"]:nth-child({active_index}) div.stButton > button {{
            background-color: #3f51b5 !important;
            border-color: #5c6bc0 !important;
            color: white !important;
            box-shadow: 0 4px 10px rgba(63, 81, 181, 0.6) !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def load_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        col_mapping = {
            '%_complete': 'percent_complete',
            '%_completed_today': 'percent_complete',
            'column_6': 'status',
            'emp_name': 'employee',
            'task_name': 'task_title'
        }
        df.rename(columns=col_mapping, inplace=True)
        
        required_cols = ['task_title', 'status', 'percent_complete']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return None, None, f"Missing required columns in dataset: {', '.join(missing_cols)}"
            
        if 'percent_complete' in df.columns:
            df['percent_complete'] = df['percent_complete'].astype(str).str.replace('%', '', regex=False)
            df['percent_complete'] = pd.to_numeric(df['percent_complete'], errors='coerce').fillna(0)
            
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.strip().str.title()
            
        if 'task_title' in df.columns:
            df.dropna(subset=['task_title'], inplace=True)
            
        if 'effort_value' in df.columns:
            df['effort_value'] = pd.to_numeric(df['effort_value'], errors='coerce').fillna(0)
            
        if 'module' not in df.columns and 'task_title' in df.columns:
            def infer_module(title):
                title = str(title).lower()
                if 'flutter' in title or 'mobile' in title:
                    return 'Flutter'
                elif 'backend' in title or 'api' in title:
                    return 'Backend'
                elif 'frontend' in title or 'ui' in title or 'website' in title or 'react' in title:
                    return 'Frontend'
                else:
                    return 'General'
            df['module'] = df['task_title'].apply(infer_module)
            
        last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df, last_refresh, None
    except requests.exceptions.RequestException as e:
        return None, None, f"Network error: Could not securely connect to Google Sheets."
    except Exception as e:
        return None, None, f"An unexpected error occurred during data processing: {e}"

def main():
    st.markdown(get_custom_css(), unsafe_allow_html=True)
        
    df, last_refresh, error_msg = load_data(DATA_URL)
    
    # Initialization for selected module state
    if 'selected_module' not in st.session_state:
        st.session_state['selected_module'] = 'All'
    
    # Header area (Refresh Info on Left, Buttons on Right)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"<span style='color: #a0a5ce; font-size: 0.9rem;'><b>Last Updated: {last_refresh if last_refresh else 'Unknown'}</b></span>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()

    with col2:
        mod_c1, mod_c2, mod_c3, mod_c4 = st.columns(4)
        with mod_c1: 
            if st.button("All", use_container_width=True): 
                st.session_state['selected_module'] = 'All'
                st.rerun()
        with mod_c2: 
            if st.button("Backend", use_container_width=True): 
                st.session_state['selected_module'] = 'Backend'
                st.rerun()
        with mod_c3: 
            if st.button("Flutter", use_container_width=True): 
                st.session_state['selected_module'] = 'Flutter'
                st.rerun()
        with mod_c4:
            if st.button("Frontend", use_container_width=True): 
                st.session_state['selected_module'] = 'Frontend'
                st.rerun()
                
    inject_active_button_style(st.session_state['selected_module'])

    if error_msg:
        st.error(f"⚠️ **Data Unavailable**: {error_msg}")
        if st.button("🔄 Retry Connection", key="retry_err_btn", type="primary"):
            st.cache_data.clear()
            st.rerun()
        st.stop()

    if df is not None and not df.empty:
        # Filter Data deeply
        filtered_df = df.copy()
        if st.session_state['selected_module'] != 'All':
            if 'module' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['module'] == st.session_state['selected_module']]
                
        # Main Metrics Calculation (Always scoped to filtered_df now!)
        overall_completion = filtered_df['percent_complete'].mean() if 'percent_complete' in filtered_df.columns and not filtered_df.empty else 0
             
        web_app_progress = 0
        mobile_app_progress = 0
        
        # Recalculate App metrics based on strictly the filtered subset
        if 'module' in filtered_df.columns and 'percent_complete' in filtered_df.columns:
            web_modules = filtered_df[filtered_df['module'].isin(['Frontend', 'Backend'])]
            if not web_modules.empty: web_app_progress = web_modules['percent_complete'].mean()
            
            mobile_modules = filtered_df[filtered_df['module'] == 'Flutter']
            if not mobile_modules.empty: mobile_app_progress = mobile_modules['percent_complete'].mean()
            
        # Timelines Fixed Setup
        project_start = datetime(2025, 1, 1) # January 1, 2025
        project_deadline = datetime(2026, 4, 15) # April 15, 2026
        today = datetime.now()
        
        total_project_days = max(1, (project_deadline - project_start).days)
        days_elapsed = max(0, (today - project_start).days)
        days_remaining = max(0, (project_deadline - today).days)
        
        expected_progress = min(100, max(0, (days_elapsed / total_project_days) * 100))
        remaining_pct = max(0, 100 - overall_completion)
        
        req_progress_per_day = 0
        if days_remaining > 0 and remaining_pct > 0:
            req_progress_per_day = remaining_pct / days_remaining
        
        project_status = "IN PROGRESS" if overall_completion < 100 else "COMPLETED"
        schedule_status = "On Track" if overall_completion >= expected_progress else "Behind Schedule"
        
        # Grid layout (3x3 metric layout)
        
        # ROW 1
        st.markdown("<br>", unsafe_allow_html=True)
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: st.metric("Overall Project Progress", f"{overall_completion:.1f}%")
        with r1c2: st.metric("Web Application Progress", f"{web_app_progress:.1f}%")
        with r1c3: st.metric("Mobile App Progress", f"{mobile_app_progress:.1f}%")

        # ROW 2
        st.markdown("<br>", unsafe_allow_html=True)
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: st.metric("Expected Overall Progress", f"{expected_progress:.1f}%")
        with r2c2: st.metric("Remaining Project Progress", f"{remaining_pct:.1f}%")
        with r2c3: st.metric("Required Progress Per Day", f"{req_progress_per_day:.2f}%")

        # ROW 3
        st.markdown("<br>", unsafe_allow_html=True)
        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1: st.metric("Project Status", project_status)
        with r3c2: st.metric("Schedule Status", schedule_status)
        with r3c3: st.metric("Days Remaining", str(days_remaining))

    else:
        st.warning("Data is currently empty or unavailable.")

if __name__ == "__main__":
    main()
