#!/bin/bash

# Inicializo serverin
clear
echo 'Duke ngarkuar checker-in... ju lutemi prisni'
echo 'Duke zbuluar kodin burim...'
sleep 3

# Konfiguro drejtoritë e serverit
DIRECTORIO='Cheker CC Bsz - V0.0.0'
echo "Kodi burim u ngarkua, duke përdorur: $DIRECTORIO"
sleep 3
clear

# Instalo PHP
echo 'Duke instaluar serverin...'
if ! command -v php &> /dev/null
then
    echo "Serveri nuk është i instaluar. Duke instaluar..."
    sudo apt update
    sudo apt install -y php
    echo "Serveri u instalua"
else
    echo "Serveri është tashmë i instaluar."
fi
sleep 3
clear

# Ekzekuto serverin
IP="localhost:8000"
echo "Duke ekzekutuar serverin në $IP"
php -S $IP -t "$DIRECTORIO"
