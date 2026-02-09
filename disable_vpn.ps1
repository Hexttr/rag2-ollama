# Script to disable VPN adapters

Write-Host "Searching for VPN adapters..." -ForegroundColor Yellow

# Find all TAP adapters
$tapAdapters = Get-NetAdapter | Where-Object {
    $_.InterfaceDescription -like "*TAP*" -or 
    $_.InterfaceDescription -like "*VPN*" -or
    $_.InterfaceDescription -like "*OpenVPN*"
}

if ($tapAdapters) {
    Write-Host "Found VPN adapters:" -ForegroundColor Green
    foreach ($adapter in $tapAdapters) {
        Write-Host "  - $($adapter.Name): $($adapter.InterfaceDescription) (Status: $($adapter.Status))" -ForegroundColor Cyan
    }
    
    Write-Host "`nDisabling VPN adapters..." -ForegroundColor Yellow
    foreach ($adapter in $tapAdapters) {
        if ($adapter.Status -eq "Up") {
            Disable-NetAdapter -Name $adapter.Name -Confirm:$false
            Write-Host "  Disabled: $($adapter.Name)" -ForegroundColor Green
        }
    }
} else {
    Write-Host "No VPN adapters found" -ForegroundColor Yellow
}

Write-Host "`nChecking internet..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName google.com -Count 2 -Quiet
if ($ping) {
    Write-Host "  Internet is working!" -ForegroundColor Green
} else {
    Write-Host "  Internet is not working. Check DNS settings." -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Green
