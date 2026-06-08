import subprocess
from pathlib import Path

projektordner = Path(__file__).resolve().parent
bat_datei = projektordner / "start_vo_tool.bat"

subprocess.call(str(bat_datei))
