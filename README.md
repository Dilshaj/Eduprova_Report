# Company Live Work Monitoring System

A production-ready Streamlit dashboard for real-time tracking of company workloads. This project connects dynamically to a live Google Sheet and provides dual distinct views: a robust **Technical Monitoring UI** and an elegant **Executive Summary Dashboard**.

## 🚀 Features
- **Live Google Sheet Sync**: Auto-refreshes data utilizing TTL caching.
- **Dual Visual Themes**: 
  - Dynamic Custom Red Theme for Technical Details
  - Clean Navy Blue Theme for Executive Summaries
- **Session Auth**: Secure lock-down logic preventing unauthorized access.
- **Global Data Filters**: Deep filtering logic chaining immediately across responsive Plotly charts & dynamic data tables.
- **Downloadable Reports**: Simple export of live filtered state directly to CSV.

---

## 🛠 Prerequisites & Installation

1. **Environment Setup**: Ensure Python 3.9+ is installed.
2. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
*(Dependencies: `streamlit`, `pandas`, `plotly`)*

3. **Run the Dashboard (Local)**:
   ```bash
   streamlit run dashboard.py
   ```

---

## ☁️ AWS EC2 Production Deployment Setup

This dashboard is designed to run efficiently on an AWS EC2 instance (e.g., Ubuntu/Amazon Linux). 
Follow these steps to deploy:

### Step 1: Launch & Configure EC2 Instance
1. Launch an EC2 instance directly inside your AWS console (a `t2.micro` or `t3.micro` works fine).
2. Configure your **Security Groups** to ensure you open TCP port `8501`. Include `SSH` (port `22`) to access the server.
3. Connect strictly to your server via SSH.

### Step 2: Install Python & Pull Code
Once inside the EC2 terminal:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

# Clone your repository or securely copy files (via scp) to the EC2 server
git clone <your-repo-link>
cd task_monitoring
```

### Step 3: Setup Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install software-properties-common
pip install wheel
pip install -r requirements.txt
```

### Step 4: Port Configuration
The Streamlit specific `.streamlit/config.toml` file is already generated and configured to aggressively enforce port `8501`, disable general XSRF protection (allowing IP-specific usage without errors initially), and initialize headless mode securely.

### Step 5: Run Dashboard Persistently in Background
To keep Streamlit running securely after you close your SSH terminal, use `tmux` or `nohup`:

**Using nohup:**
```bash
nohup streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 &
```

The system will now be live strictly at: `http://<EC2-PUBLIC-IP>:8501`

*(To explicitly stop it later, use `lsof -i:8501` to find the PID and `kill <PID>`)*

---

## ⚡ Performance Optimization Tips

1. **Extended Caching (`@st.cache_data`)**: The system currently caches the Google Sheet response using `ttl=10`. In production with heavy network lag or heavy row limits, securely extend this TTL up to `60` seconds to aggressively limit network payload consumption. 
2. **Nginx Reverse Proxy**: For heavy usage, safely place Streamlit behind an **Nginx** server block natively bound to port `80` (HTTP) or `443` (HTTPS). This allows you to handle extreme traffic correctly before it routes to Streamlit's `8501` port.
3. **Data Pre-Aggregation**: If the Google sheet balloons to 50k+ records, offload heavy pandas dataframe calculations (means, grouped metrics, etc.) directly inside `@st.cache_data` instead of recalculating during massive re-renders.
4. **Remove Unused Visuals**: If using complex multi-trace visuals, consider actively caching Plotly figure objects themselves.
