# Inicializo serverin
Clear-Host
Write-Output 'Duke ngarkuar checker-in... ju lutemi prisni'
Write-Output 'Duke zbuluar kodin burim...'
Start-Sleep -Seconds 3

# Konfiguro drejtoritë e serverit
\$DIRECTORIO = 'Cheker CC Bsz - V0.0.0'
Write-Output "Kodi burim u ngarkua, duke përdorur: \$DIRECTORIO"
Start-Sleep -Seconds 3
Clear-Host

# Verifiko nëse PHP është i instaluar
if (-not (Get-Command php -ErrorAction SilentlyContinue)) {
    Write-Output 'Serveri nuk është i instaluar. Duke instaluar...'
    winget install --id PHP.PHP.8.4
    Clear-Host
    Write-Output "Serveri u instalua. Ekzekutoni skriptin përsëri."
    Start-Sleep -Seconds 3
    Exit
} else {
    Write-Output 'Serveri është tashmë i instaluar.'
    Start-Sleep -Seconds 3
}

# Ekzekuto serverin
\$IP = 'localhost:8000'
Write-Output "Duke ekzekutuar serverin në \$IP, për ta mbyllur, shtypni Ctrl + C ose mbyllni këtë dritare."
php -S "$IP" -t "$DIRECTORIO"
