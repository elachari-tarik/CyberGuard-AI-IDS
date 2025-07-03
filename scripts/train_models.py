#!/usr/bin/env python3
"""
Script d'entraînement optimisé pour CyberGuard AI
Utilise CICIDS2017 uniquement avec validation croisée robuste
"""

import sys
import os
import glob
import argparse
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import joblib
import warnings
warnings.filterwarnings('ignore')

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml_models import EnsembleIDS, IDSMLModel
from config.config import Config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_and_optimize_cicids(path, max_samples_per_class=100000):
    """
    Version corrigée avec gestion appropriée des colonnes string
    """
    logger.info("🔄 Chargement optimisé de CICIDS2017...")
    
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {path}")
    
    logger.info(f"📁 {len(csv_files)} fichiers CSV détectés")
    
    all_data = []
    total_samples = 0
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        logger.info(f"📊 Traitement de {filename}...")
        
        try:
            chunks = []
            chunk_size = 50000
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
            samples = len(df)
            
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip()
            
            # Identifier la colonne label
            label_col = None
            for col in ['Label', ' Label', 'label']:
                if col in df.columns:
                    label_col = col
                    break
            
            if label_col:
                df.rename(columns={label_col: 'label'}, inplace=True)
            
            all_data.append(df)
            total_samples += samples
            logger.info(f"   ✅ {samples:,} échantillons chargés")
            
        except Exception as e:
            logger.warning(f"   ❌ Erreur avec {filename}: {e}")
    
    if not all_data:
        raise ValueError("Aucune donnée CICIDS2017 chargée")
    
    # Combiner toutes les données
    logger.info("🔗 Fusion des données...")
    df_combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"🎯 Total brut: {total_samples:,} échantillons")
    
    # Analyse des labels
    logger.info("📊 Analyse des types d'attaques...")
    if 'label' in df_combined.columns:
        label_counts = df_combined['label'].value_counts()
        logger.info(f"   Types détectés: {len(label_counts)}")
        for label, count in label_counts.head(10).items():
            logger.info(f"   - {label}: {count:,}")
    else:
        raise ValueError("Colonne 'label' non trouvée")
    
    # Sélection intelligente des classes
    logger.info("🎯 Sélection et équilibrage des classes...")
    
    # Identifier le trafic normal
    normal_labels = ['BENIGN', 'Benign', 'benign']
    normal_data = pd.DataFrame()
    
    for normal_label in normal_labels:
        if normal_label in label_counts.index:
            normal_data = df_combined[df_combined['label'] == normal_label]
            logger.info(f"   ✅ Trafic normal trouvé: {normal_label} ({len(normal_data):,} échantillons)")
            break
    
    # Sélectionner les top attaques
    attack_data = df_combined[~df_combined['label'].isin(normal_labels)]
    attack_types = attack_data['label'].value_counts()
    
    # Prendre les 5 types d'attaques les plus fréquents
    top_attacks = attack_types.head(5).index.tolist()
    logger.info(f"   🎯 Top 5 attaques sélectionnées: {top_attacks}")
    
    # Créer un dataset équilibré
    balanced_samples = []
    
    # Ajouter le trafic normal (échantillonné)
    if not normal_data.empty:
        normal_sample = normal_data.sample(min(max_samples_per_class, len(normal_data)), random_state=42)
        balanced_samples.append(normal_sample)
        logger.info(f"   ✅ Normal: {len(normal_sample):,} échantillons")
    
    # Ajouter chaque type d'attaque
    for attack_type in top_attacks:
        attack_subset = attack_data[attack_data['label'] == attack_type]
        attack_sample = attack_subset.sample(min(max_samples_per_class//2, len(attack_subset)), random_state=42)
        balanced_samples.append(attack_sample)
        logger.info(f"   ✅ {attack_type}: {len(attack_sample):,} échantillons")
    
    # Combiner le dataset final
    df_final = pd.concat(balanced_samples, ignore_index=True)
    
    # *** CORRECTION CRITIQUE : Preprocessing avancé avec gestion des colonnes string ***
    logger.info("🔧 Preprocessing avancé...")
    
    # 1. SAUVEGARDER LA COLONNE LABEL AVANT NETTOYAGE
    original_labels = df_final['label'].copy()
    
    # 2. IDENTIFIER ET SUPPRIMER TOUTES LES COLONNES NON NUMÉRIQUES (sauf label temporairement)
    # Sélectionner UNIQUEMENT les colonnes numériques
    numeric_cols = df_final.select_dtypes(include=[np.number]).columns.tolist()
    logger.info(f"   📊 Colonnes numériques détectées: {len(numeric_cols)}")
    
    # 3. CRÉER LE DATASET AVEC UNIQUEMENT LES FEATURES NUMÉRIQUES
    df_clean = df_final[numeric_cols].copy()
    
    # 4. NETTOYER LES DONNÉES NUMÉRIQUES
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean = df_clean.fillna(0)
    
    # 5. SUPPRIMER LES COLONNES AVEC VARIANCE NULLE
    variance_filter = df_clean.var() > 0
    df_clean = df_clean.loc[:, variance_filter]
    logger.info(f"   📊 Features après nettoyage: {len(df_clean.columns)}")
    
    # 6. RÉAJOUTER LA COLONNE LABEL ORIGINALE (STRING)
    df_clean['label'] = original_labels.values
    
    # 7. ENCODER LES LABELS EN VALEURS NUMÉRIQUES
    le = LabelEncoder()
    df_clean['encoded_label'] = le.fit_transform(df_clean['label'])
    
    # Statistiques finales
    final_label_counts = df_clean['encoded_label'].value_counts()
    logger.info(f"🎯 Dataset final optimisé: {len(df_clean):,} échantillons")
    logger.info(f"📊 Features numériques: {len(df_clean.columns)-2}")  # -2 pour label et encoded_label
    logger.info(f"📊 Distribution des classes: {dict(final_label_counts)}")
    
    # Afficher le mapping des labels
    label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    logger.info(f"📊 Mapping des labels: {label_mapping}")
    
    return df_clean, le

def advanced_model_training(df, label_encoder):
    """
    Version corrigée de l'entraînement avec gestion appropriée des colonnes
    """
    logger.info("🧠 === ENTRAÎNEMENT AVANCÉ DES MODÈLES ===")
    
    # *** CORRECTION : Sélectionner UNIQUEMENT les features numériques ***
    # Exclure les colonnes label (string) et encoded_label (target)
    feature_cols = [col for col in df.columns 
                   if col not in ['label', 'encoded_label'] 
                   and df[col].dtype in ['int64', 'float64', 'int32', 'float32']]
    
    X = df[feature_cols].copy()
    y = df['encoded_label'].copy()
    
    logger.info(f"📊 Features d'entraînement: {len(feature_cols)}")
    logger.info(f"📊 Échantillons: {len(X):,}")
    logger.info(f"📊 Types de données X: {X.dtypes.value_counts().to_dict()}")
    
    # Vérification finale : s'assurer que X ne contient que des valeurs numériques
    non_numeric_in_X = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric_in_X:
        logger.error(f"❌ Colonnes non numériques détectées dans X: {non_numeric_in_X}")
        raise ValueError(f"Features non numériques trouvées: {non_numeric_in_X}")
    
    # Normalisation des features
    logger.info("⚖️ Normalisation des features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # Division train/test stratifiée
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"📊 Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # Validation croisée pour sélectionner le meilleur modèle
    logger.info("🔍 Validation croisée pour sélection de modèle...")
    
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        'SVM_RBF': SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
    }
    
    # Validation croisée
    cv_results = {}
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)  # Réduit à 3 pour plus de rapidité
    
    for name, model in models.items():
        logger.info(f"   🔄 Test de {name}...")
        
        cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='f1_macro', n_jobs=-1)
        
        cv_results[name] = {
            'mean_f1': cv_scores.mean(),
            'std_f1': cv_scores.std(),
            'model': model
        }
        
        logger.info(f"      F1-Score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    # Sélectionner le meilleur modèle
    best_model_name = max(cv_results.keys(), key=lambda k: cv_results[k]['mean_f1'])
    best_model = cv_results[best_model_name]['model']
    
    logger.info(f"🏆 Meilleur modèle: {best_model_name}")
    logger.info(f"   F1-Score CV: {cv_results[best_model_name]['mean_f1']:.4f}")
    
    # Entraînement final du meilleur modèle
    logger.info("🎯 Entraînement final du meilleur modèle...")
    best_model.fit(X_train, y_train)
    
    # Évaluation sur le test set
    y_pred = best_model.predict(X_test)
    test_f1 = f1_score(y_test, y_pred, average='macro')
    
    logger.info(f"📊 Performance sur test set:")
    logger.info(f"   F1-Score: {test_f1:.4f}")
    
    # Rapport détaillé
    class_names = label_encoder.classes_
    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
    
    logger.info("📊 Rapport de classification par classe:")
    for class_name in class_names:
        if class_name in report:
            metrics = report[class_name]
            logger.info(f"   {class_name}:")
            logger.info(f"      Precision: {metrics['precision']:.3f}")
            logger.info(f"      Recall: {metrics['recall']:.3f}")
            logger.info(f"      F1-Score: {metrics['f1-score']:.3f}")
    
    # *** CORRECTION : Préparer le dataset pour l'ensemble IDS avec UNIQUEMENT encoded_label ***
    df_for_ensemble = X_scaled.copy()
    df_for_ensemble['label'] = y  # Utiliser encoded_label (numérique)
    
    return df_for_ensemble, best_model, scaler, label_encoder, cv_results

def train_all_models():
    """
    Fonction principale d'entraînement optimisée
    """
    logger.info("🚀 === ENTRAÎNEMENT CICIDS2017 OPTIMISÉ ===")
    
    try:
        # Charger et optimiser CICIDS2017
        df_optimized, label_encoder = load_and_optimize_cicids(
            os.path.join("data", "datasets", "cicids2017"),
            max_samples_per_class=80000
        )
        
        # Entraînement avancé
        df_final, best_model, scaler, le, cv_results = advanced_model_training(df_optimized, label_encoder)
        
        # Entraîner l'ensemble IDS avec les données optimisées
        logger.info("🔧 Entraînement de l'ensemble IDS...")
        ensemble = EnsembleIDS()
        ensemble.train_ensemble(df_final, target_column='label')
        
        # Sauvegarder tous les modèles
        logger.info("💾 Sauvegarde des modèles...")
        os.makedirs(Config.MODEL_PATH, exist_ok=True)
        
        # Sauvegarder l'ensemble
        ensemble.save_ensemble(Config.MODEL_PATH)
        
        # Sauvegarder les métadonnées
        metadata = {
            'label_encoder': label_encoder,
            'scaler': scaler,
            'best_model': best_model,
            'cv_results': cv_results,
            'feature_columns': df_final.columns.tolist(),
            'training_stats': {
                'total_samples': len(df_final),
                'num_features': len(df_final.columns) - 1,
                'num_classes': len(label_encoder.classes_),
                'class_names': label_encoder.classes_.tolist()
            }
        }
        
        joblib.dump(metadata, os.path.join(Config.MODEL_PATH, 'training_metadata.joblib'))
        
        logger.info("✅ === ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS ===")
        logger.info(f"📊 Résumé:")
        logger.info(f"   🎯 Échantillons utilisés: {len(df_final):,}")
        logger.info(f"   🎯 Features: {len(df_final.columns)-1}")
        logger.info(f"   🎯 Classes: {len(label_encoder.classes_)}")
        logger.info(f"   🎯 Meilleur modèle: {type(best_model).__name__}")
        logger.info(f"   🎯 Modèles sauvegardés dans: {Config.MODEL_PATH}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'entraînement: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement optimisé CyberGuard AI avec CICIDS2017")
    parser.add_argument('--max-samples', type=int, default=80000,
                       help='Nombre maximum d\'échantillons par classe')
    
    args = parser.parse_args()
    
    try:
        train_all_models()
        logger.info("🎉 ✅ ENTRAÎNEMENT TERMINÉ!")
        logger.info("🚀 Lancez maintenant: python scripts/start_ids.py --mode web --simulation")
        
    except Exception as e:
        logger.error(f"❌ Échec de l'entraînement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

