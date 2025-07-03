#!/usr/bin/env python3
"""
Script de test minimal pour l'entraînement
"""
import sys
import os

print("🧪 Test du script d'entraînement...")

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("📦 Test des imports...")
    import pandas as pd
    print("✅ pandas OK")
    
    import numpy as np
    print("✅ numpy OK")
    
    from sklearn.ensemble import RandomForestClassifier
    print("✅ sklearn OK")
    
    from config.config import Config
    print("✅ config OK")
    
    from src.ml_models import EnsembleIDS
    print("✅ ml_models OK")
    
    print("📁 Test des datasets...")
    dataset_path = os.path.join("data", "datasets", "cicids2017")
    if os.path.exists(dataset_path):
        import glob
        csv_files = glob.glob(os.path.join(dataset_path, "*.csv"))
        print(f"✅ {len(csv_files)} fichiers CSV trouvés")
    else:
        print("❌ Répertoire CICIDS2017 non trouvé")
    
    print("✅ Tous les tests passés!")
    
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    print("🎯 Script de test terminé avec succès!")
