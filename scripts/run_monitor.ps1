param(
    [string]$ConfigPath = "config.yaml",
    [int]$Cycles = 1
)

$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt
python -m pytest -v
python monitor.py --config $ConfigPath run --cycles $Cycles --report
