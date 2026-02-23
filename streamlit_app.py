# Entry point for Streamlit Cloud — delegates to the dashboard
import runpy, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
runpy.run_path("dashboard/app.py", run_name="__main__")
