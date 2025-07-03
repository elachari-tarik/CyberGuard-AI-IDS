# 🛡️ CyberGuard AI - Système de Détection d'Intrusions Intelligent## 📋 Description

CyberGuard AI est un système de détection d'intrusions réseau (IDS) intelligent basé sur le machine learning. Il utilise des algorithmes d'apprentissage automatique pour détecter en temps réel les activités malveillantes et les tentatives d'intrusion sur le réseau.

## 🎯 Fonctionnalités

- **Détection en temps réel** des intrusions réseau
- **Machine Learning** avec ensemble de modèles (Random Forest, SVM, Isolation Forest)
- **Interface web moderne** avec dashboard interactif
- **Base de données PostgreSQL** pour stockage des logs et alertes
- **Système d'alertes intelligent** avec classification automatique
- **Support de multiples types d'attaques** : DDoS, Port Scan, Brute Force, etc.

## 🏗️ Architecture
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Capture │ │ Preprocessing │ │ ML Models │
│ Réseau │───▶│ & Feature │───▶│ (Ensemble) │
│ (Scapy) │ │ Extraction │ │ Detection │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Interface │ │ Alert System │ │ Database │
│ Web (Flask) │◀───│ & Notification │◀───│ (PostgreSQL) │
│ Dashboard │ │ Management │ │ Storage │
└─────────────────┘ └──────────────────┘ └─────────────────┘
text
## 📊 Performance

- **F1-Score** : 99.93%
- **Accuracy** : 99.84%
- **Dataset** : CICIDS2017 (218K+ échantillons)
- **Features** : 70 caractéristiques réseau
- **Classes détectées** : 6 types d'attaques + trafic normal

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- Git

### Installation Rapide
Cloner le projet
git clone https://github.com/votre-username/CyberGuard-AI-IDS.git
cd CyberGuard-AI-IDS
Créer l'environnement virtuel
python3 -m venv cyberguard_env
source cyberguard_env/bin/activate # Linux/macOS
cyberguard_env\Scripts\activate # Windows
Installer les dépendances
pip install -r requirements.txt
Configuration de la base de données
python scripts/setup_database.py
Entraîner les modèles
python scripts/start_ids.py --mode train
Démarrer l'interface web
python scripts/start_ids.py --mode web --simulation
text
## 🎮 Utilisation

### Dashboard Web
Accédez à l'interface web : http://localhost:5000

- **Dashboard principal** : Métriques temps réel, graphiques interactifs
- **Gestion des alertes** : Filtrage, export, détails des intrusions
- **Contrôles système** : Démarrage/arrêt du moteur IDS

### Modes de Fonctionnement
Mode web avec simulation
python scripts/start_ids.py --mode web --simulation
Mode web avec capture réelle
python scripts/start_ids.py --mode web
Mode console
python scripts/start_ids.py --mode console --simulation
Entraînement des modèles
python scripts/start_ids.py --mode train
text
## 📁 Structure du Projet
CyberGuard-AI-IDS/
├── config/ # Configuration système
├── src/ # Code source principal
│ ├── data_collection.py # Capture réseau
│ ├── feature_extraction.py # Extraction de caractéristiques
│ ├── ml_models.py # Modèles ML
│ ├── detection_engine.py # Moteur de détection
│ ├── alert_system.py # Système d'alertes
│ └── database.py # Gestion base de données
├── web_interface/ # Interface web Flask
├── scripts/ # Scripts d'automatisation
├── data/ # Datasets et données
├── models/ # Modèles ML entraînés
└── logs/ # Fichiers de logs
text
## 🔬 Datasets Utilisés

- **CICIDS2017** : Dataset de référence pour IDS
- **NSL-KDD** : Dataset classique de détection d'intrusions
- **Données synthétiques** : Génération de trafic pour tests

## 🛠️ Technologies

- **Backend** : Python, Flask, SQLAlchemy
- **Machine Learning** : scikit-learn, pandas, numpy
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, CSS3, JavaScript, Chart.js
- **Capture réseau** : Scapy, pyshark
- **Temps réel** : WebSocket, Flask-SocketIO

## 📈 Résultats

### Performance des Modèles
| Modèle | Accuracy | F1-Score | Precision | Recall |
|--------|----------|----------|-----------|--------|
| Random Forest | 99.84% | 99.93% | 99.9% | 99.9% |
| SVM | 97.65% | 98.0% | 97.0% | 98.0% |
| Isolation Forest | - | - | - | 10% anomalies |

### Types d'Attaques Détectées
- ✅ **DDoS** : 100% F1-Score
- ✅ **Port Scan** : 99.9% F1-Score
- ✅ **Brute Force** : 99.9% F1-Score
- ✅ **DoS** : 99.8% F1-Score
- ✅ **FTP-Patator** : 100% F1-Score

## 🎓 Contexte Académique

Ce projet a été développé dans le cadre d'un **Projet de Fin d'Études (PFE)** en cybersécurité, démontrant l'application pratique du machine learning pour la sécurité réseau.

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

EL-ACHARI Tarik - Étudiant en ITLearning - Master ISRS
HAJJI Wissal - Étudiant en ITLearning - Master SAAICC

## 🙏 Remerciements

- Dataset CICIDS2017 par l'Université du Nouveau-Brunswick
- Communauté scikit-learn pour les outils ML
- Flask et PostgreSQL pour l'infrastructure web

---

⭐ **N'hésitez pas à donner une étoile si ce projet vous a été utile !**
