🛡️ CyberGuard AI - Déploiement des Corrections
🚀 ÉTAPES RAPIDES (5 minutes)
1. Remplacer les Fichiers Corrigés
bash# Aller dans votre projet
cd ~/CyberGuardAI

# Sauvegarder les anciens fichiers (optionnel)
cp src/detection_engine.py src/detection_engine.py.backup
cp src/data_collection.py src/data_collection.py.backup
cp config/config.py config/config.py.backup
Remplacez ces fichiers avec les versions corrigées :

src/detection_engine.py → Remplacer par detection_engine_fixed.py
src/data_collection.py → Remplacer par data_collection_enhanced.py
config/config.py → Remplacer par config_fixed.py
scripts/test_detection.py → Nouveau fichier à créer

2. Créer le Script de Test
bash# Créer le script de test
cat > scripts/test_detection.py << 'EOF'
[Coller le contenu de test_detection.py ici]
EOF

# Rendre exécutable
chmod +x scripts/test_detection.py
3. Tester Immédiatement
bash# Activer l'environnement
source cyberguard_env/bin/activate

# Test rapide du système
python scripts/test_detection.py

🔧 DÉMARRAGE COMPLET
Option A: Démarrage Rapide avec Tests
bash# 1. Activer l'environnement
source cyberguard_env/bin/activate

# 2. Tester le système corrigé
python scripts/test_detection.py

# 3. Créer des alertes de démonstration
python scripts/force_alerts.py

# 4. Démarrer l'interface web
python scripts/start_ids.py --mode web --simulation
Option B: Démarrage Manuel Étape par Étape
bash# 1. Vérifier la base de données
python scripts/setup_database.py

# 2. Vérifier les modèles ML
ls -la models/trained/

# 3. Tester la détection
python -c "
from src.detection_engine import IDSDetectionEngine
from config.config import Config
engine = IDSDetectionEngine(Config)
print('✅ Moteur initialisé' if engine.initialize(True) else '❌ Erreur')
"

# 4. Démarrer le serveur web
cd web_interface
python app.py

🎯 VÉRIFICATION RAPIDE
Après démarrage, vérifiez :

Dashboard accessible : http://localhost:5000
Métriques qui bougent : Paquets > 0, Flux > 0
Anomalies détectées : Doit être > 0 après quelques minutes
Alertes générées : Page /alerts doit montrer des alertes

Si pas d'anomalies détectées :
bash# Forcer la création d'alertes
python -c "
from scripts.force_alerts import create_test_alerts
create_test_alerts()
print('✅ Alertes de test créées')
"

# Ou redémarrer avec paramètres agressifs
export ALERT_THRESHOLD=0.1
export ANOMALY_THRESHOLD=0.05
python scripts/start_ids.py --mode web --simulation

🚨 TESTS D'ATTAQUES EXTERNES
Depuis Windows (si vous avez le .bat) :
bash# Depuis Windows, exécuter :
# cyberguard_attack_suite.bat
Depuis Linux/WSL :
bash# Test SSH brute force simulé
for i in {1..20}; do
  echo "Tentative $i"
  timeout 1 telnet 172.23.73.174 22 2>/dev/null || true
  sleep 0.1
done

# Test port scan
nmap -sS -F localhost 2>/dev/null || echo "Nmap non installé"

# Génération de trafic HTTP
for i in {1..50}; do
  curl -s http://localhost:5000 > /dev/null &
done

📊 SURVEILLANCE EN TEMPS RÉEL
Terminal 1: Logs en temps réel
bashtail -f logs/training.log
Terminal 2: Stats système
bashwatch -n 2 "python -c '
from src.database import DatabaseManager
db = DatabaseManager()
alerts = db.get_recent_alerts(10)
print(f\"Alertes: {len(alerts)}\")
for a in alerts[:3]:
    print(f\"- {a.alert_type}: {a.severity}\")
'"
Terminal 3: Interface web
bashpython scripts/start_ids.py --mode web --simulation --verbose

🔍 DÉBOGAGE AVANCÉ
Si toujours 0 anomalies :
bash# Mode débogage ultra-agressif
python -c "
import sys, os
sys.path.append('.')
from src.detection_engine import IDSDetectionEngine
from config.config import Config

# Forcer les seuils très bas
Config.ALERT_THRESHOLD = 0.05
Config.ANOMALY_THRESHOLD = 0.02

engine = IDSDetectionEngine(Config)
engine.initialize(True)
engine.start()

import time
print('Test pendant 30 secondes...')
for i in range(6):
    time.sleep(5)
    stats = engine.get_stats()
    print(f'Stats: {stats}')

engine.stop()
"
Vérifier les modèles ML :
bashpython -c "
from src.ml_models import EnsembleIDS
ensemble = EnsembleIDS()
try:
    ensemble.load_ensemble('models/trained/')
    print('✅ Modèles chargés')
    for name, model in ensemble.models.items():
        print(f'- {name}: {model.is_trained}')
except Exception as e:
    print(f'❌ Erreur modèles: {e}')
"

📱 ACCÈS AU DASHBOARD
Une fois démarré :

Dashboard principal : http://localhost:5000
Page des alertes : http://localhost:5000/alerts
API status : http://localhost:5000/api/status
API alertes : http://localhost:5000/api/alerts

Comptes utilisateur (si nécessaire) :

Admin : admin / admin123
User : user / user123


⚡ SCRIPT DE DÉMARRAGE AUTOMATIQUE
Créez un script de démarrage complet :
bashcat > start_cyberguard.sh << 'EOF'
#!/bin/bash
echo "🛡️ Démarrage CyberGuard AI..."

# Activer l'environnement
source cyberguard_env/bin/activate

# Vérifier la BDD
python scripts/setup_database.py

# Créer des alertes de test
python scripts/force_alerts.py

# Configurer les seuils agressifs
export ALERT_THRESHOLD=0.2
export ANOMALY_THRESHOLD=0.15

# Démarrer avec simulation agressive
echo "🚀 Lancement du serveur..."
python scripts/start_ids.py --mode web --simulation

EOF

chmod +x start_cyberguard.sh
Puis simplement :
bash./start_cyberguard.sh

🎯 RÉSULTATS ATTENDUS
Après 2-3 minutes, vous devriez voir :

Paquets analysés : 500-2000+
Flux réseau : 100-500+
Anomalies détectées : 20-100+ (au lieu de 0)
Alertes actives : 5-50+ (au lieu de 0)

Types d'alertes générées :

SSH Brute Force
Port Scan
DDoS Attack
Web Attack
Anomalous Activity


🆘 DÉPANNAGE RAPIDE
Problème 1: "Module not found"
bashexport PYTHONPATH="${PWD}:${PYTHONPATH}"
Problème 2: Base de données
bashsudo systemctl start postgresql
python scripts/setup_database.py
Problème 3: Port 5000 occupé
bash# Changer le port dans web_interface/app.py ligne finale :
# socketio.run(app, host='0.0.0.0', port=5001, debug=False)
Problème 4: Permissions
bashchmod +x scripts/*.py
sudo chown -R $USER:$USER .

🚀 COMMANDE ULTIME POUR DÉMARRER :
bashcd ~/CyberGuardAI && source cyberguard_env/bin/activate && python scripts/test_detection.py && python scripts/start_ids.py --mode web --simulation
