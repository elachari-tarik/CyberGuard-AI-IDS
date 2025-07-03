#!/usr/bin/env python3
"""
Script de démarrage principal pour CyberGuard AI - VERSION CORRIGÉE
"""
import sys
import os
import argparse
import signal
import time
import traceback

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def signal_handler(sig, frame):
    """Gestionnaire pour arrêt propre"""
    print('\n🛑 Arrêt du système CyberGuard AI...')
    sys.exit(0)

def train_models():
    """Entraîne les modèles ML avec gestion d'erreurs robuste"""
    try:
        print("🧠 Démarrage de l'entraînement des modèles...")
        
        # Vérifier que le script d'entraînement existe
        train_script_path = os.path.join(os.path.dirname(__file__), 'train_models.py')
        if not os.path.exists(train_script_path):
            print(f"❌ Script d'entraînement non trouvé: {train_script_path}")
            return False
        
        # Méthode 1: Import direct (recommandé)
        try:
            # Import du module d'entraînement
            import importlib.util
            spec = importlib.util.spec_from_file_location("train_models", train_script_path)
            train_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(train_module)
            
            # Exécuter la fonction d'entraînement
            if hasattr(train_module, 'train_all_models'):
                train_module.train_all_models()
                print("✅ Entraînement terminé avec succès!")
                return True
            else:
                print("❌ Fonction 'train_all_models' non trouvée dans le script")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
            print("🔄 Tentative avec subprocess...")
            
            # Méthode 2: Subprocess en fallback
            import subprocess
            result = subprocess.run([
                sys.executable, train_script_path
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            
            if result.returncode == 0:
                print("✅ Entraînement terminé avec succès!")
                print(result.stdout)
                return True
            else:
                print(f"❌ Erreur lors de l'entraînement:")
                print(result.stderr)
                return False
                
    except Exception as e:
        print(f"❌ Erreur critique lors de l'entraînement: {e}")
        traceback.print_exc()
        return False

def start_web_mode(simulation=False):
    """Démarre en mode web"""
    try:
        print("🌐 Démarrage de l'interface web...")
        
        # Vérifier que les modules web existent
        web_app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface', 'app.py')
        if not os.path.exists(web_app_path):
            print(f"❌ Application web non trouvée: {web_app_path}")
            return False
        
        # Import de l'application web
        from web_interface.app import app, socketio
        
        print("📊 Dashboard accessible sur: http://localhost:5000")
        print("🔄 Initialisation du moteur IDS...")
        
        # Démarrer l'application
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Erreur d'import pour l'interface web: {e}")
        print("💡 Vérifiez que tous les fichiers web_interface sont présents")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du démarrage web: {e}")
        traceback.print_exc()
        return False

def start_console_mode(simulation=False):
    """Démarre en mode console"""
    try:
        print("💻 Mode console activé")
        
        from src.detection_engine import IDSDetectionEngine
        from config.config import Config
        
        ids_engine = IDSDetectionEngine(Config)
        
        if ids_engine.initialize(use_simulation=simulation):
            ids_engine.start()
            print("✅ Moteur IDS démarré - Appuyez sur Ctrl+C pour arrêter")
            
            try:
                while True:
                    stats = ids_engine.get_stats()
                    print(f"📊 Paquets: {stats.get('packets_processed', 0)} | "
                          f"Flux: {stats.get('flows_analyzed', 0)} | "
                          f"Anomalies: {stats.get('anomalies_detected', 0)}")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                ids_engine.stop()
                print("🛑 Moteur IDS arrêté")
                return True
        else:
            print("❌ Erreur lors de l'initialisation du moteur IDS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur en mode console: {e}")
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='CyberGuard AI - Système IDS Intelligent')
    parser.add_argument('--mode', choices=['web', 'console', 'train'], 
                       default='web', help='Mode d\'exécution')
    parser.add_argument('--simulation', action='store_true', 
                       help='Utiliser la simulation de trafic')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mode verbeux pour le débogage')
    
    args = parser.parse_args()
    
    # Configuration du gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🛡️ Démarrage de CyberGuard AI...")
    print(f"📁 Répertoire de travail: {os.getcwd()}")
    
    if args.verbose:
        print(f"🔧 Mode: {args.mode}")
        print(f"🔧 Simulation: {args.simulation}")
        print(f"🔧 Python: {sys.executable}")
        print(f"🔧 Version Python: {sys.version}")
    
    success = False
    
    try:
        if args.mode == 'train':
            success = train_models()
        elif args.mode == 'web':
            success = start_web_mode(args.simulation)
        elif args.mode == 'console':
            success = start_console_mode(args.simulation)
        else:
            print(f"❌ Mode non reconnu: {args.mode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur")
        success = True
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        if args.verbose:
            traceback.print_exc()
        success = False
    
    if success:
        print("✅ Opération terminée avec succès")
        sys.exit(0)
    else:
        print("❌ Opération échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()

