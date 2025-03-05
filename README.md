## Active virtual env
# In cmd.exe
venv\Scripts\activate.bat
# In PowerShell
venv\Scripts\Activate.ps1


Run the backend "uvicorn backend:app --host 0.0.0.0 --port 8000 --reload"

Run streamlit "streamlit run frontend.py"