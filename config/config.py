import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'ids_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'secure_password')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'cyberguard_db')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # *** IDS Configuration CORRIGÉE pour plus de sensibilité ***
    CAPTURE_INTERFACE = os.getenv('CAPTURE_INTERFACE', 'eth0')
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/trained/')
    
    # *** CORRECTION CRITIQUE: Seuils beaucoup plus bas ***
    ALERT_THRESHOLD = float(os.getenv('ALERT_THRESHOLD', '0.2'))  # Au lieu de 0.3
    ANOMALY_THRESHOLD = float(os.getenv('ANOMALY_THRESHOLD', '0.15'))  # Nouveau seuil très bas
    
    # *** Real-time Configuration OPTIMISÉE ***
    BUFFER_SIZE = int(os.getenv('BUFFER_SIZE', '30'))  # Plus petit pour analyse plus fréquente
    ANALYSIS_INTERVAL = int(os.getenv('ANALYSIS_INTERVAL', '3'))  # Plus fréquent (3 secondes)
    
    # *** Nouveaux paramètres pour améliorer la détection ***
    # Détection heuristique
    ENABLE_HEURISTIC_DETECTION = True
    HEURISTIC_WEIGHT = 0.6  # Poids de la détection heuristique
    ML_WEIGHT = 0.4  # Poids de la détection ML
    
    # Seuils pour différents types d'attaques
    PORT_SCAN_THRESHOLD = 10  # Nombre de ports scannés pour déclencher une alerte
    BRUTE_FORCE_THRESHOLD = 5  # Nombre de tentatives pour déclencher une alerte
    DDOS_PPS_THRESHOLD = 50  # Paquets par seconde pour détecter DDoS
    
    # Mode debug pour forcer des détections
    DEBUG_MODE = True
    FORCE_DETECTION_RATE = 0.1  # 10% de détections forcées en mode debug
    
    # Configuration de simulation agressive
    SIMULATION_ATTACK_RATE = 0.7  # 70% d'attaques en simulation
    SIMULATION_BURST_MODE = True  # Générer des bursts d'attaques
    
    # Alertes en temps réel
    REAL_TIME_ALERTS = True
    ALERT_AGGREGATION_WINDOW = 30  # secondes pour grouper les alertes similaires
    MAX_ALERTS_PER_MINUTE = 50  # Augmenté pour plus d'alertes
    
    # Configuration de logging améliorée
    LOG_LEVEL = 'INFO'
    LOG_ANOMALIES = True
    LOG_ALL_PREDICTIONS = False  # Mettre True pour debug complet
    
    # Thresholds pour classification des sévérités
    SEVERITY_THRESHOLDS = {
        'critical': 0.8,
        'high': 0.6,
        'medium': 0.4,
        'low': 0.2
    }
    
    # Ports suspects pour la détection heuristique
    SUSPICIOUS_PORTS = [22, 23, 21, 25, 53, 80, 110, 143, 443, 993, 995, 1433, 3306, 3389, 5432, 5900, 1723, 135, 139, 445]
    
    # IPs et réseaux à surveiller particulièrement
    MONITORED_NETWORKS = [
        '172.23.0.0/16',  # Réseau WSL2
        '10.0.0.0/8',     # Réseau privé
        '192.168.0.0/16', # Réseau local
    ]
    
    # Configuration ML améliorée
    ML_ENSEMBLE_WEIGHTS = {
        'random_forest': 0.4,
        'svm': 0.3,
        'isolation_forest': 0.3
    }
    
    # Retrain automatique des modèles
    AUTO_RETRAIN = False  # Désactivé pour la démo
    RETRAIN_INTERVAL_HOURS = 24
    MIN_SAMPLES_FOR_RETRAIN = 1000
