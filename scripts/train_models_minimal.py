#!/usr/bin/env python3
"""
Script d'entraînement minimal et robuste pour CyberGuard AI
"""
import sys
import os
import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_cicids_simple():
    """Charge CICIDS2017 de manière simple et robuste"""
    logger.info("🔄 Chargement simple de CICIDS2017...")
    
    try:
        # Prendre un seul fichier pour commencer
        dataset_path = os.path.join("data", "datasets", "cicids2017")
        csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')]
        
        if not csv_files:
            raise FileNotFoundError("Aucun fichier CSV trouvé")
        
        # Charger le premier fichier
        file_path = os.path.join(dataset_path, csv_files[0])
        logger.info(f"📁 Chargement de {csv_files[0]}...")
        
        df = pd.read_csv(file_path, nrows=10000)  # Limiter à 10K pour test
        logger.info(f"✅ {len(df)} échantillons chargés")
        
        # Nettoyer les colonnes
        df.columns = df.columns.str.strip()
        
        # Trouver la colonne label
        label_col = None
        for col in ['Label', ' Label', 'label']:
            if col in df.columns:
                label_col = col
                break
        
        if label_col:
            df.rename(columns={label_col: 'label'}, inplace=True)
        else:
            raise ValueError("Colonne label non trouvée")
        
        # Garder seulement les colonnes numériques + label
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        df_clean = df[numeric_cols + ['label']].copy()
        
        # Nettoyer les données
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        df_clean = df_clean.fillna(0)
        
        logger.info(f"📊 Dataset nettoyé: {len(df_clean)} échantillons, {len(numeric_cols)} features")
        
        return df_clean
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement: {e}")
        raise

def train_simple_model(df):
    """Entraîne un modèle simple"""
    logger.info("🧠 Entraînement d'un modèle simple...")
    
    try:
        # Préparer les données
        feature_cols = [col for col in df.columns if col != 'label']
        X = df[feature_cols]
        
        # Encoder les labels
        le = LabelEncoder()
        y = le.fit_transform(df['label'])
        
        logger.info(f"📊 Features: {len(feature_cols)}, Classes: {len(le.classes_)}")
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # Entraîner Random Forest
        rf = RandomForestClassifier(n_estimators=10, random_state=42)
        rf.fit(X_train, y_train)
        
        # Évaluer
        score = rf.score(X_test, y_test)
        logger.info(f"📊 Accuracy: {score:.4f}")
        
        # Sauvegarder
        import joblib
        os.makedirs("models/trained", exist_ok=True)
        joblib.dump(rf, "models/trained/simple_rf_model.joblib")
        joblib.dump(le, "models/trained/label_encoder.joblib")
        
        logger.info("✅ Modèle sauvegardé avec succès!")
        
        return rf, le
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'entraînement: {e}")
        raise

def main():
    """Fonction principale"""
    try:
        logger.info("🚀 === ENTRAÎNEMENT MINIMAL CYBERGUARD AI ===")
        
        # Charger les données
        df = load_cicids_simple()
        
        # Entraîner le modèle
        model, encoder = train_simple_model(df)
        
        logger.info("🎉 ✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
        
    except Exception as e:
        logger.error(f"❌ Échec de l'entraînement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
