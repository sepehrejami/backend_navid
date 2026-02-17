# Dot-source this script to apply env vars in your current shell
# Example: . .\simulator\switch_to_mock.ps1
$env:AUTOX_BASE_URL = "http://127.0.0.1:9001"
$env:AUTOX_APP_ID = "mock"
$env:AUTOX_APP_SECRET = "mock"
$env:AUTOX_APP_CODE = "mock"
$env:AUTOX_FORCE_ENV = "1"
$env:ROBOT_IDS = "SIM-ROBOT-1,SIM-ROBOT-2"
Write-Host "Mock AutoXing env set for this shell."
