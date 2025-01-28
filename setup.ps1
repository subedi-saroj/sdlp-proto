# Get the absolute path to the project root
$projectRoot = (Get-Location).Path

# Set PYTHONPATH using the relative path to lux4600
$env:PYTHONPATH="$projectRoot\lux4600;$env:PYTHONPATH"

# Activate the virtual environment (adjust path if necessary)
& "$projectRoot\.venv\Scripts\Activate.ps1"