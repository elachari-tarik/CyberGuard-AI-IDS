#!/usr/bin/env python3
"""
Script de configuration initiale du projet CyberGuard AI
"""
import os
import sys
from pathlib import Path

def setup_project():
    """Configure le projet pour la première utilisation"""
    print("🛡️ Configuration initiale de CyberGuard AI...")
    
    # Vérifier l'environnement virtuel
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Attention: Vous n'êtes pas dans un environnement virtuel!")
        print("Exécutez : source cyberguard_env/bin/activate")
        return False
    
    # Créer les répertoires manquants
    directories = [
        'logs', 'models/trained', 'data/captured', 'data/processed'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire créé: {directory}")
    
    # Vérifier les dépendances critiques
    try:
        import pandas, numpy, sklearn, flask, sqlalchemy
        print("✓ Dépendances principales installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Exécutez : pip install -r requirements.txt")
        return False
    
    # Vérifier la configuration
    if not Path('.env').exists():
        print("❌ Fichier .env manquant")
        print("Créez le fichier .env avec la configuration de la base de données")
        return False
    
    print("✅ Configuration terminée avec succès!")
    return True

if __name__ == "__main__":
    setup_project()

