#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager

def create_test_alerts():
    """Crée des alertes de test pour vérifier l'interface"""
    db = DatabaseManager()
    
    test_alerts = [
        {
            'alert_type': 'Port Scan',
            'severity': 'High',
            'source_ip': '172.23.64.1',  # Votre IP Windows
            'target_ip': '172.23.73.174',  # Votre IP WSL2
            'description': 'Port scan détecté depuis Windows host',
            'confidence': 0.95
        },
        {
            'alert_type': 'Nmap Scan',
            'severity': 'Medium',
            'source_ip': '172.23.64.1',
            'target_ip': '172.23.73.174',
            'description': 'Scan Nmap intensif détecté',
            'confidence': 0.87
        },
        {
            'alert_type': 'Reconnaissance',
            'severity': 'Medium',
            'source_ip': '172.23.64.1',
            'target_ip': '172.23.73.174',
            'description': 'Activité de reconnaissance réseau',
            'confidence': 0.78
        }
    ]
    
    for alert_data in test_alerts:
        alert_id = db.create_alert(alert_data)
        if alert_id:
            print(f"✅ Alerte créée: {alert_data['alert_type']} (ID: {alert_id})")
        else:
            print(f"❌ Erreur création alerte: {alert_data['alert_type']}")

if __name__ == "__main__":
    create_test_alerts()
    print("🎯 Alertes de test créées! Actualisez votre dashboard.")
