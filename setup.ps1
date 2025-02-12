# Get the absolute path to the project root
$projectRoot = (Get-Location).Path

# Activate the virtual environment (adjust path if necessary)
& "$projectRoot\.venv\Scripts\Activate.ps1"

# Set PYTHONPATH using the relative path to lux4600
$env:PYTHONPATH="$projectRoot\lux4600;$env:PYTHONPATH"
