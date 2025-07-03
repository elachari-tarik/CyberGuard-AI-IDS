#!/usr/bin/env python3
"""
Script de test pour vérifier la détection d'anomalies - DÉBOGAGE IMMÉDIAT
"""
import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection_engine import IDSDetectionEngine
from config.config import Config
from src.data_collection import SimulatedCapture
from src.feature_extraction import NetworkFeatureExtractor
import logging

# Configuration du logging détaillé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simulation_only():
    """Test de la simulation seule"""
    print("🧪 === TEST 1: SIMULATION DE TRAFIC ===")
    
    sim = SimulatedCapture()
    sim.start_capture()
    
    print("⏳ Génération de trafic pendant 10 secondes...")
    time.sleep(10)
    
    packets = sim.get_packets()
    print(f"📦 Paquets générés: {len(packets)}")
    
    if packets:
        print("📊 Exemples de paquets générés:")
        for i, packet in enumerate(packets[:5]):
            print(f"  {i+1}. {packet['src_ip']} -> {packet['dst_ip']}:{packet['dst_port']} ({packet['protocol_name']})")
    
    sim.stop_capture()
    return len(packets) > 0

def test_feature_extraction():
    """Test de l'extraction de features"""
    print("\n🧪 === TEST 2: EXTRACTION DE FEATURES ===")
    
    # Créer des paquets de test manuellement
    test_packets = [
        {
            'timestamp': datetime.now(),
            'src_ip': '172.23.64.1',
            'dst_ip': '172.23.73.174',
            'src_port': 12345,
            'dst_port': 22,
            'protocol_name': 'TCP',
            'packet_size': 64,
            'ttl': 64
        },
        {
            'timestamp': datetime.now(),
            'src_ip': '172.23.64.1',
            'dst_ip': '172.23.73.174',
            'src_port': 12345,
            'dst_port': 22,
            'protocol_name': 'TCP',
            'packet_size': 64,
            'ttl': 64
        }
    ]
    
    extractor = NetworkFeatureExtractor()
    features_list = extractor.extract_features_from_packets(test_packets)
    
    print(f"📊 Features extraites: {len(features_list)}")
    
    if features_list:
        features = features_list[0]
        print("🔍 Exemple de features:")
        for key, value in features.items():
            if key not in ['flow_id', 'start_time']:
                print(f"  {key}: {value}")
        
        # Test de création de DataFrame
        df = extractor.create_feature_dataframe(features_list)
        print(f"📈 DataFrame créé: {df.shape}")
        print(f"📋 Colonnes: {list(df.columns)}")
    
    return len(features_list) > 0

def test_detection_engine():
    """Test complet du moteur de détection"""
    print("\n🧪 === TEST 3: MOTEUR DE DÉTECTION COMPLET ===")
    
    # Initialiser le moteur
    ids_engine = IDSDetectionEngine(Config)
    
    print("🔧 Initialisation du moteur...")
    if not ids_engine.initialize(use_simulation=True):
        print("❌ Échec de l'initialisation")
        return False
    
    print("🚀 Démarrage du moteur...")
    ids_engine.start()
    
    print("⏳ Test pendant 30 secondes...")
    start_time = time.time()
    
    while time.time() - start_time < 30:
        stats = ids_engine.get_stats()
        print(f"📊 Stats: Paquets: {stats['packets_processed']}, "
              f"Flux: {stats['flows_analyzed']}, "
              f"Anomalies: {stats['anomalies_detected']}, "
              f"Alertes: {stats['alerts_generated']}")
        time.sleep(5)
    
    # Arrêter le moteur
    ids_engine.stop()
    
    final_stats = ids_engine.get_stats()
    print(f"📈 RÉSULTATS FINAUX:")
    print(f"  Paquets traités: {final_stats['packets_processed']}")
    print(f"  Flux analysés: {final_stats['flows_analyzed']}")
    print(f"  Anomalies détectées: {final_stats['anomalies_detected']}")
    print(f"  Alertes générées: {final_stats['alerts_generated']}")
    
    # Vérifier si des anomalies ont été détectées
    success = final_stats['anomalies_detected'] > 0
    if success:
        print("✅ Test réussi - Anomalies détectées!")
    else:
        print("❌ Test échoué - Aucune anomalie détectée")
    
    return success

def test_database_connection():
    """Test de connexion à la base de données"""
    print("\n🧪 === TEST 4: CONNEXION BASE DE DONNÉES ===")
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        
        # Test de création d'alerte
        test_alert = {
            'alert_type': 'Test Alert',
            'severity': 'Medium',
            'source_ip': '172.23.64.1',
            'target_ip': '172.23.73.174',
            'description': 'Test de fonctionnement du système',
            'confidence': 0.8
        }
        
        alert_id = db.create_alert(test_alert)
        
        if alert_id:
            print(f"✅ Alerte de test créée avec ID: {alert_id}")
            
            # Récupérer les alertes récentes
            recent_alerts = db.get_recent_alerts(limit=5)
            print(f"📋 Alertes récentes trouvées: {len(recent_alerts)}")
            
            return True
        else:
            print("❌ Échec de création d'alerte")
            return False
    
    except Exception as e:
        print(f"❌ Erreur de base de données: {e}")
        return False

def force_create_alerts():
    """Force la création d'alertes pour test"""
    print("\n🧪 === TEST 5: CRÉATION FORCÉE D'ALERTES ===")
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        
        test_alerts = [
            {
                'alert_type': 'SSH Brute Force',
                'severity': 'High',
                'source_ip': '172.23.64.1',
                'target_ip': '172.23.73.174',
                'description': 'Tentatives de brute force SSH détectées',
                'confidence': 0.9
            },
            {
                'alert_type': 'Port Scan',
                'severity': 'Medium',
                'source_ip': '10.0.0.100',
                'target_ip': '172.23.73.174',
                'description': 'Scan de ports détecté',
                'confidence': 0.75
            },
            {
                'alert_type': 'DDoS Attack',
                'severity': 'Critical',
                'source_ip': '203.0.113.1',
                'target_ip': '172.23.73.174',
                'description': 'Attaque DDoS détectée',
                'confidence': 0.95
            }
        ]
        
        created_alerts = 0
        for alert_data in test_alerts:
            alert_id = db.create_alert(alert_data)
            if alert_id:
                created_alerts += 1
                print(f"✅ Alerte créée: {alert_data['alert_type']} (ID: {alert_id})")
        
        print(f"📊 Total d'alertes créées: {created_alerts}/3")
        return created_alerts > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🛡️ === CYBERGUARD AI - TESTS DE DÉBOGAGE ===")
    print(f"⏰ Début des tests: {datetime.now()}")
    
    tests_results = []
    
    # Test 1: Simulation
    try:
        result1 = test_simulation_only()
        tests_results.append(("Simulation de trafic", result1))
    except Exception as e:
        print(f"❌ Erreur Test 1: {e}")
        tests_results.append(("Simulation de trafic", False))
    
    # Test 2: Feature extraction
    try:
        result2 = test_feature_extraction()
        tests_results.append(("Extraction de features", result2))
    except Exception as e:
        print(f"❌ Erreur Test 2: {e}")
        tests_results.append(("Extraction de features", False))
    
    # Test 3: Base de données
    try:
        result3 = test_database_connection()
        tests_results.append(("Connexion BDD", result3))
    except Exception as e:
        print(f"❌ Erreur Test 3: {e}")
        tests_results.append(("Connexion BDD", False))
    
    # Test 4: Création forcée d'alertes
    try:
        result4 = force_create_alerts()
        tests_results.append(("Création d'alertes", result4))
    except Exception as e:
        print(f"❌ Erreur Test 4: {e}")
        tests_results.append(("Création d'alertes", False))
    
    # Test 5: Moteur complet (le plus important)
    try:
        result5 = test_detection_engine()
        tests_results.append(("Détection complète", result5))
    except Exception as e:
        print(f"❌ Erreur Test 5: {e}")
        tests_results.append(("Détection complète", False))
    
    # Résumé des tests
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = 0
    for test_name, result in tests_results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:<25} : {status}")
        if result:
            passed += 1
    
    print(f"\nTests réussis: {passed}/{len(tests_results)}")
    
    if passed >= 3:  # Si au moins 3 tests passent
        print("🎉 SYSTÈME FONCTIONNEL - Vérifiez le dashboard!")
        print("🌐 Dashboard: http://localhost:5000")
    else:
        print("⚠️  PROBLÈMES DÉTECTÉS - Vérifiez les logs")
    
    print(f"⏰ Tests terminés: {datetime.now()}")

if __name__ == "__main__":
    main()
