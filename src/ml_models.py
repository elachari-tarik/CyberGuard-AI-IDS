import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class IDSMLModel:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = None
        self.is_trained = False
        
        # Seuils de détection
        self.anomaly_threshold = 0.8
        self.confidence_threshold = 0.7
        
    def _get_model(self):
        """Initialise le modèle selon le type spécifié"""
        if self.model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'svm':
            return SVC(
                kernel='rbf',
                probability=True,
                random_state=42,
                gamma='scale'
            )
        elif self.model_type == 'isolation_forest':
            return IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Type de modèle non supporté: {self.model_type}")
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement/prédiction"""
        if df.empty:
            return np.array([]), []
        
        # Sélectionner les colonnes numériques pour ML
        feature_cols = [col for col in df.columns if col not in [
            'flow_id', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'label'
        ] and df[col].dtype in ['int64', 'float64', 'int32', 'float32']]
        
        if self.feature_columns is None:
            self.feature_columns = feature_cols
        
        # S'assurer que toutes les colonnes nécessaires sont présentes
        missing_cols = set(self.feature_columns) - set(df.columns)
        for col in missing_cols:
            df[col] = 0
        
        # Sélectionner et ordonner les features
        X = df[self.feature_columns].copy()
        
        # Gerer les valeurs manquantes
        X = X.fillna(0)
        
        # Gérer les valeurs infinies
        X = X.replace([np.inf, -np.inf], 0)
        
        return X.values, feature_cols
    
    def train_supervised(self, df, target_column='label'):
        """Entraîne le modèle en mode supervisé"""
        print(f"Entraînement du modèle {self.model_type} en mode supervisé...")
        
        if target_column not in df.columns:
            raise ValueError(f"Colonne cible '{target_column}' non trouvée")
        
        # Préparer les features et labels
        X, feature_cols = self.prepare_features(df)
        y = df[target_column].values
        
        if len(X) == 0:
            raise ValueError("Aucune feature numérique trouvée")
        
        # Encoder les labels si nécessaire
        if y.dtype == 'object':
            y = self.label_encoder.fit_transform(y)
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Normalisation des features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement du modèle
        self.model = self._get_model()
        
        if self.model_type in ['random_forest', 'svm']:
            self.model.fit(X_train_scaled, y_train)
            
            # Prédictions et évaluation
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            
            # Métriques d'évaluation
            print("=== Résultats de l'entraînement ===")
            print(f"Accuracy: {self.model.score(X_test_scaled, y_test):.4f}")
            print("\nRapport de classification:")
            print(classification_report(y_test, y_pred))
            
            if len(np.unique(y)) == 2:  # Classification binaire
                auc = roc_auc_score(y_test, y_pred_proba[:, 1])
                print(f"AUC-ROC: {auc:.4f}")
        
        self.is_trained = True
        return self.model
    
    def train_unsupervised(self, df):
        """Entraîne le modèle en mode non-supervisé (détection d'anomalies)"""
        print(f"Entraînement du modèle {self.model_type} en mode non-supervisé...")
        
        X, feature_cols = self.prepare_features(df)
        
        if len(X) == 0:
            raise ValueError("Aucune feature numérique trouvée")
        
        # Normalisation des features
        X_scaled = self.scaler.fit_transform(X)
        
        # Entraînement du modèle
        if self.model_type == 'isolation_forest':
            self.model = self._get_model()
            self.model.fit(X_scaled)
            
            # Évaluation sur les données d'entraînement
            anomaly_scores = self.model.decision_function(X_scaled)
            predictions = self.model.predict(X_scaled)
            
            anomaly_rate = (predictions == -1).mean()
            print(f"Taux d'anomalies détectées: {anomaly_rate:.4f}")
            print(f"Score d'anomalie moyen: {anomaly_scores.mean():.4f}")
        
        self.is_trained = True
        return self.model
    
    def predict(self, df):
        """Effectue des prédictions sur de nouvelles données"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas encore entraîné")
        
        X, _ = self.prepare_features(df)
        
        if len(X) == 0:
            return []
        
        X_scaled = self.scaler.transform(X)
        
        results = []
        
        if self.model_type == 'isolation_forest':
            # Détection d'anomalies non-supervisée
            predictions = self.model.predict(X_scaled)
            scores = self.model.decision_function(X_scaled)
            
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                result = {
                    'prediction': 'Anomaly' if pred == -1 else 'Normal',
                    'confidence': min(abs(score), 1.0),
                    'anomaly_score': score,
                    'is_anomaly': pred == -1
                }
                results.append(result)
        
        else:
            # Classification supervisée
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            # Décoder les labels si nécessaire
            if hasattr(self.label_encoder, 'classes_'):
                class_names = self.label_encoder.classes_
            else:
                class_names = ['Normal', 'Attack']
            
            for i, (pred, proba) in enumerate(zip(predictions, probabilities)):
                max_proba = max(proba)
                predicted_class = class_names[pred] if hasattr(self.label_encoder, 'classes_') else ('Attack' if pred == 1 else 'Normal')
                
                result = {
                    'prediction': predicted_class,
                    'confidence': max_proba,
                    'probabilities': dict(zip(class_names, proba)),
                    'is_anomaly': pred == 1 or max_proba < self.confidence_threshold
                }
                results.append(result)
        
        return results
    
    def save_model(self, filepath):
        """Sauvegarde le modèle entraîné"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas encore entraîné")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'timestamp': datetime.now()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)
        print(f"Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath):
        """Charge un modèle pré-entraîné"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fichier modèle non trouvé: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data['model_type']
        self.is_trained = model_data['is_trained']
        
        print(f"Modèle chargé: {filepath}")
        return self.model

class EnsembleIDS:
    """Système ensemble combinant plusieurs modèles"""
    
    def __init__(self):
        self.models = {
            'random_forest': IDSMLModel('random_forest'),
            'svm': IDSMLModel('svm'),
            'isolation_forest': IDSMLModel('isolation_forest')
        }
        self.weights = {'random_forest': 0.4, 'svm': 0.3, 'isolation_forest': 0.3}
    
    def train_ensemble(self, df, target_column='label'):
        """Entraîne tous les modèles de l'ensemble"""
        print("=== Entraînement de l'ensemble de modèles ===")
        
        # Entraînement supervisé pour RF et SVM
        if target_column in df.columns:
            self.models['random_forest'].train_supervised(df, target_column)
            self.models['svm'].train_supervised(df, target_column)
        
        # Entraînement non-supervisé pour Isolation Forest
        self.models['isolation_forest'].train_unsupervised(df)
        
        print("Ensemble entraîné avec succès!")
    
    def predict_ensemble(self, df):
        """Prédictions combinées de l'ensemble"""
        all_predictions = {}
        
        # Obtenir les prédictions de chaque modèle
        for name, model in self.models.items():
            if model.is_trained:
                try:
                    predictions = model.predict(df)
                    all_predictions[name] = predictions
                except Exception as e:
                    print(f"Erreur prédiction {name}: {e}")
        
        if not all_predictions:
            return []
        
        # Combiner les prédictions
        combined_results = []
        n_samples = len(list(all_predictions.values())[0])
        
        for i in range(n_samples):
            anomaly_scores = []
            confidence_scores = []
            predictions = []
            
            for name, preds in all_predictions.items():
                if i < len(preds):
                    pred = preds[i]
                    
                    # Normaliser les scores
                    if 'anomaly_score' in pred:
                        anomaly_scores.append(abs(pred['anomaly_score']) * self.weights[name])
                    
                    confidence_scores.append(pred['confidence'] * self.weights[name])
                    predictions.append(1 if pred['is_anomaly'] else 0)
            
            # Vote majoritaire pondéré
            weighted_vote = sum(p * list(self.weights.values())[j] for j, p in enumerate(predictions))
            final_prediction = 'Anomaly' if weighted_vote > 0.5 else 'Normal'
            
            combined_result = {
                'prediction': final_prediction,
                'confidence': sum(confidence_scores),
                'ensemble_score': weighted_vote,
                'is_anomaly': weighted_vote > 0.5,
                'individual_predictions': {name: all_predictions[name][i] for name in all_predictions if i < len(all_predictions[name])}
            }
            
            combined_results.append(combined_result)
        
        return combined_results
    
    def save_ensemble(self, base_path):
        """Sauvegarde tous les modèles de l'ensemble"""
        for name, model in self.models.items():
            filepath = os.path.join(base_path, f"{name}_model.joblib")
            model.save_model(filepath)
    
    def load_ensemble(self, base_path):
        """Charge tous les modèles de l'ensemble"""
        for name, model in self.models.items():
            filepath = os.path.join(base_path, f"{name}_model.joblib")
            if os.path.exists(filepath):
                model.load_model(filepath)

