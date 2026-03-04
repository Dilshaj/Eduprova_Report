import time
import requests
import io
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dilshaj Live Work Monitoring System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def get_dark_red_theme_css():
    return """
    <style>
        /* Professional Dark Red Executive Theme (SaaS Feel) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .stApp { 
            background: linear-gradient(135deg, #C8EADD 0%, #f0faf7 100%); 
            background-attachment: fixed;
            color: #0f172a; 
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Typography */
        h1, h2, h3, p, span, div { font-family: 'Inter', sans-serif !important; }
        h1, h2, h3 { color: #0f172a !important; letter-spacing: -0.02em; }
        h1 { margin-bottom: 0.5rem !important; text-align: center; font-weight: 800; }
        h3 { margin-top: 1.5rem !important; margin-bottom: 1rem !important; font-weight: 700; }
        
        /* Main Container Padding */
        .block-container { 
            padding-top: 2.5rem !important; 
            padding-bottom: 4rem !important; 
            padding-left: 3rem !important; 
            padding-right: 3rem !important; 
            max-width: 1400px; 
            border-top: 4px solid #ef4444; 
        }
        
        /* Metrics & Cards */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e1a3b, #2c2456);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: none;
            transition: all 0.3s ease;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            text-align: center;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        }
        div[data-testid="stMetric"] label { 
            color: #d1d5db !important; 
            font-size: 1.1rem !important; 
            font-weight: 600 !important; 
            margin-bottom: 0.5rem !important;
            opacity: 0.9;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
            color: #ffffff !important; 
            font-weight: 800 !important; 
            font-size: 3.2rem !important; 
            line-height: 1.1 !important;
            margin-top: 0 !important;
        }
        
        /* Buttons */
        div.stButton > button {
            background-color: #2b0b0b;
            color: #ffffff;
            border: 1px solid #451a1a;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            background-color: #ef4444;
            color: #ffffff;
            border-color: #ef4444;
            box-shadow: 0 6px 15px rgba(239, 68, 68, 0.4);
            transform: translateY(-2px);
        }
        div.stDownloadButton > button {
            background-color: #ef4444;
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 0.7rem 1.5rem;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 6px 15px rgba(239, 68, 68, 0.3);
        }
        div.stDownloadButton > button:hover {
            background-color: #dc2626;
            color: #ffffff;
            box-shadow: 0 8px 20px rgba(239, 68, 68, 0.5);
            transform: translateY(-2px);
        }
        
        /* Spinners */
        .stSpinner > div > div { border-top-color: #ef4444 !important; }
        
        /* Spacing */
        div[data-testid="column"] { padding: 0 1rem; }
        
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

# --- CONSTANTS ---
SHEET_ID = "1i3Knwzh3I9rklo_8xDxeDVzH8y0aAzG2OayosfPt3mY"
TAB_GIDS = {
    "Daily Task": "1170202777",
    "Employee ID & Name": "2007217359",
    "Task Logs": "0",
    "Module Progress": "675411717"
}

# --- DATA FETCHING (CACHED WITH TTL) ---
@st.cache_data(ttl=10)
def load_sheet(gid):
    """
    Fetches live data from a specific Google Sheet tab via GID.
    Cache automatically expires every 10 seconds (ttl=10).
    """
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        # Normalize columns: strip spaces, lowercase, replace spaces with underscores
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        return df
    except Exception as e:
        if "PLEASE_ADD_GID_HERE" not in str(gid): # Don't log error for placeholder GIDs
            st.error(f"⚠️ Error fetching data for GID '{gid}': {e}")
        return pd.DataFrame()

def load_all_data():
    df_daily = load_sheet(TAB_GIDS["Daily Task"])
    df_emp = load_sheet(TAB_GIDS["Employee ID & Name"])
    df_task = load_sheet(TAB_GIDS["Task Logs"])
    df_module = load_sheet(TAB_GIDS["Module Progress"])
    
    from datetime import datetime
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df_daily, df_emp, df_task, df_module, last_refresh

# --- UNIFIED PROCESSING LOGIC ---
def process_unified_dataset(df_task, df_emp):
    """
    Process the Google Sheets data into a unified project monitoring dataset.
    Returns: (metrics_dict, cleaned_dataframe)
    """
    if df_task.empty:
        return {}, df_task
        
    # 1. Merge employee details with task logs using employee_id
    if 'employee_id' in df_task.columns and 'employee_id' in df_emp.columns:
        df_merged = pd.merge(df_task, df_emp, on='employee_id', how='left')
    else:
        df_merged = df_task.copy()
        
    # Standardize percent complete column name if necessary
    if '%_complete' in df_merged.columns and 'percent_complete' not in df_merged.columns:
        df_merged.rename(columns={'%_complete': 'percent_complete'}, inplace=True)
        
    # 2. Clean the percent_complete column (remove %, convert to float)
    if 'percent_complete' in df_merged.columns:
        df_merged['percent_complete'] = df_merged['percent_complete'].astype(str).str.replace('%', '', regex=False)
        df_merged['percent_complete'] = pd.to_numeric(df_merged['percent_complete'], errors='coerce').fillna(0).astype(float)
    else:
        df_merged['percent_complete'] = 0.0

    # 3. Categorize tasks by module (Backend, Frontend, Flutter)
    if 'module' not in df_merged.columns:
        title_col = 'task_name' if 'task_name' in df_merged.columns else 'task_title' if 'task_title' in df_merged.columns else None
        
        if title_col:
            def infer_module(title):
                title = str(title).lower()
                if 'flutter' in title or 'mobile' in title: return 'Flutter'
                elif 'backend' in title or 'api' in title: return 'Backend'
                elif 'frontend' in title or 'ui' in title or 'react' in title: return 'Frontend'
                else: return 'General'
            df_merged['module'] = df_merged[title_col].apply(infer_module)
        else:
            df_merged['module'] = 'General'
            
    # 4 & 5. Calculate metrics
    metrics = {}
    
    # Calculate module progress variants
    frontend_pct = df_merged[df_merged['module'] == 'Frontend']['percent_complete'].mean() if not df_merged[df_merged['module'] == 'Frontend'].empty else 0.0
    backend_pct = df_merged[df_merged['module'] == 'Backend']['percent_complete'].mean() if not df_merged[df_merged['module'] == 'Backend'].empty else 0.0
    flutter_pct = df_merged[df_merged['module'] == 'Flutter']['percent_complete'].mean() if not df_merged[df_merged['module'] == 'Flutter'].empty else 0.0
    
    metrics['Frontend %'] = frontend_pct
    metrics['Backend %'] = backend_pct
    metrics['Flutter %'] = flutter_pct

    # Web Application Progress (average completion of Backend + Frontend tasks)
    web_tasks = df_merged[df_merged['module'].isin(['Backend', 'Frontend'])]
    metrics['Web Application Progress'] = web_tasks['percent_complete'].mean() if not web_tasks.empty else 0.0
    
    # Mobile App Progress (average completion of Flutter tasks)
    metrics['Mobile App Progress'] = flutter_pct
    
    # Overall Project Progress (average completion of all tasks)
    metrics['Overall Project Progress'] = df_merged['percent_complete'].mean() if not df_merged.empty else 0.0
    
    return metrics, df_merged

# --- MAIN DASHBOARD LAYOUT ---
def main():
    # --- FETCH DATA ---
    # Loading Spinner wraps the data fetch operation
    with st.spinner("Fetching latest live data from Google Sheets..."):
        df_daily, df_emp, df_task, df_module, last_refresh = load_all_data()
        
        # Process the raw task logs into the unified structure
        metrics, df_merged = process_unified_dataset(df_task, df_emp)
        
        # Initialize session state for module filtering
        if 'selected_module' not in st.session_state:
            st.session_state['selected_module'] = 'All'
            
        # Apply filter to the dataset based on session_state
        if st.session_state['selected_module'] != 'All':
            df_merged = df_merged[df_merged['module'] == st.session_state['selected_module']]
        
        # Temporarily assigning df to df_merged so the rest of the file stays functional 
        df = df_merged if not df_merged.empty else pd.DataFrame()
        
    # --- RENDER DASHBOARD HEADER ---
    st.markdown(get_dark_red_theme_css(), unsafe_allow_html=True)
    st.title("EDUPROVA PROGRESS DASHBOARD")
    
    header_col1, header_col2 = st.columns([1, 5])
    with header_col1:
        if st.button("🔄 Refresh Data", key="manual_refresh_main"):
            st.cache_data.clear()
            st.rerun()
    with header_col2:
        # Display the Last Updated label right below the title
        st.caption(f"**Last Updated: {last_refresh if last_refresh else 'Unknown'}**")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df is not None:
        if df.empty:
            st.warning("Data fetched successfully, but the sheet appears to be empty.")
        else:
            # --- TOP SECTION: 3 KPI CARDS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Web Application Progress", f"{metrics.get('Web Application Progress', 0):.0f}%")
            c2.metric("Mobile App Progress", f"{metrics.get('Mobile App Progress', 0):.0f}%")
            c3.metric("Overall Project Progress", f"{metrics.get('Overall Project Progress', 0):.0f}%")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # --- CHARTS SECTION ---
            st.markdown("### Progress Breakdown & Analytics")
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # 1. Horizontal Bar Chart
                module_data = pd.DataFrame({
                    "Module": ["Frontend", "Backend", "Flutter"],
                    "Progress": [
                        metrics.get('Frontend %', 0),
                        metrics.get('Backend %', 0),
                        metrics.get('Flutter %', 0)
                    ]
                })
                fig_bar = px.bar(
                    module_data, 
                    x='Progress', 
                    y='Module', 
                    orientation='h', 
                    text_auto='.0f',
                    color='Module',
                    color_discrete_sequence=['#ef4444', '#f87171', '#fca5a5']
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1e1e1e'), showlegend=False,
                    xaxis=dict(title="% Complete", range=[0, 100], gridcolor='rgba(0,0,0,0.1)', tickfont=dict(color='#1e1e1e', size=14)),
                    yaxis=dict(title="", tickfont=dict(color='#1e1e1e', size=14)),
                    height=400, margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with chart_col2:
                # 2. Donut Chart
                overall_prog = metrics.get('Overall Project Progress', 0)
                remaining_prog = max(0, 100 - overall_prog)
                
                fig_donut = go.Figure(data=[go.Pie(
                    labels=['<b>Completed %</b>', '<b>Remaining %</b>'], 
                    values=[overall_prog, remaining_prog], 
                    hole=.6, 
                    marker=dict(colors=['#ef4444', '#1e1a3b'])
                )])
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1e1e1e', size=16), height=400, margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#1e1e1e', size=16))
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # --- TASK DETAILS TABLE SECTION ---
            st.markdown("### TASK DETAILS")
            
            # Table specific styling
            st.markdown("""
                <style>
                .custom-table-container {
                    max-height: 400px;
                    overflow-y: auto;
                    border: 1px solid #e6e8f0;
                    border-radius: 12px;
                    background-color: #ffffff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }
                .custom-table {
                    width: 100%;
                    border-collapse: collapse;
                    text-align: left;
                    font-family: 'Inter', sans-serif;
                }
                .custom-table th {
                    background-color: #f4f6fb;
                    color: #4a4f63;
                    padding: 14px 16px;
                    position: sticky;
                    top: 0;
                    z-index: 2;
                    text-transform: uppercase;
                    font-size: 0.85rem;
                    letter-spacing: 0.05em;
                }
                .custom-table td {
                    padding: 14px 16px;
                    color: #2e2e2e;
                    border-bottom: 1px solid #e6e8f0;
                }
                .custom-table tr:hover { background-color: #f9fafc; }
                .custom-table tr:last-child td { border-bottom: none; }
                
                /* Scrollbar styling */
                .custom-table-container::-webkit-scrollbar { width: 8px; }
                .custom-table-container::-webkit-scrollbar-track { background: #ffffff; }
                .custom-table-container::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
                .custom-table-container::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
                </style>
            """, unsafe_allow_html=True)
            
            # Identify columns handling name variants
            title_col = 'task_name' if 'task_name' in df_merged.columns else 'task_title' if 'task_title' in df_merged.columns else None
            
            if not title_col or df_merged.empty:
                 st.info("No task data available.")
            else:
                display_cols = ['module', title_col, 'status', 'percent_complete']
                existing_cols = [c for c in display_cols if c in df_merged.columns]
                
                if existing_cols:
                    display_df = df_merged[existing_cols].copy()
                    rename_dict = {
                        'module': 'Module', 
                        title_col: 'Task_Title', 
                        'status': 'Status', 
                        'percent_complete': 'Percent_Completed'
                    }
                    display_df.rename(columns=rename_dict, inplace=True)
                    
                    if 'Percent_Completed' in display_df.columns:
                        display_df['Percent_Completed'] = display_df['Percent_Completed'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "0%")
                        
                    def format_status_badge(val):
                        if pd.isna(val): return ''
                        val_str = str(val).strip().title()
                        
                        if val_str == 'Completed':
                            return '<span style="background-color: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 5px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">Completed</span>'
                        elif val_str == 'In Progress':
                            return '<span style="background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 5px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">In Progress</span>'
                        elif val_str == 'Pending':
                            return '<span style="background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 5px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">Pending</span>'
                        return f'<span style="background-color: rgba(156, 163, 175, 0.15); color: #64748b; padding: 5px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">{val}</span>'

                    if 'Status' in display_df.columns:
                        display_df['Status'] = display_df['Status'].apply(format_status_badge)
                        
                    # Generate HTML
                    html_table_inner = display_df.to_html(escape=False, index=False, classes="custom-table")
                    
                    # Wrap in scrolling container
                    final_html = f"""
                    <div class="custom-table-container">
                        {html_table_inner}
                    </div>
                    """
                    st.markdown(final_html, unsafe_allow_html=True)
                    
            # --- MODULE FILTER BUTTONS ---
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### Filter Tasks by Module")
            
            # Show the currently active filter
            st.caption(f"Current Filter: **{st.session_state['selected_module']}**")
            
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            with btn_col1:
                if st.button("All", use_container_width=True):
                    st.session_state['selected_module'] = 'All'
                    st.rerun()
            with btn_col2:
                if st.button("Backend", use_container_width=True):
                    st.session_state['selected_module'] = 'Backend'
                    st.rerun()
            with btn_col3:
                if st.button("Flutter", use_container_width=True):
                    st.session_state['selected_module'] = 'Flutter'
                    st.rerun()
            with btn_col4:
                if st.button("Frontend", use_container_width=True):
                    st.session_state['selected_module'] = 'Frontend'
                    st.rerun()
                    
            # --- EXPORT BUTTON ---
            st.markdown("<br>", unsafe_allow_html=True)
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            csv_data = df_merged.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv_data,
                file_name=f"project_tasks_{current_date}.csv",
                mime="text/csv",
                use_container_width=True
            )

    else:
        st.error("Could not load the dashboard data. Retrying shortly...")

    # --- FOOTER ---
    st.markdown("""
        <div style="border-top: 1px solid #1E293B; margin-top: 3rem; padding-top: 1.5rem; text-align: center; color: #9CA3AF; font-size: 0.85rem;">
            Powered by <b>dilshaj Monitoring System</b>
        </div>
    """, unsafe_allow_html=True)




if __name__ == "__main__":
    main()
