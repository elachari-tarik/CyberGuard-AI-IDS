#!/usr/bin/env python3
"""
Script de configuration de la base de données PostgreSQL
"""
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

def create_database():
    """Crée la base de données et l'utilisateur si nécessaire"""
    try:
        # Connexion avec l'utilisateur postgres par défaut
        conn = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            user='postgres',  # Utilisateur admin par défaut
            password='postgres'  # Changez si nécessaire
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Créer l'utilisateur s'il n'existe pas
        try:
            cursor.execute(f"CREATE USER {Config.POSTGRES_USER} WITH PASSWORD '{Config.POSTGRES_PASSWORD}';")
            print(f"✓ Utilisateur {Config.POSTGRES_USER} créé")
        except psycopg2.errors.DuplicateObject:
            print(f"✓ Utilisateur {Config.POSTGRES_USER} existe déjà")
        
        # Créer la base de données si elle n'existe pas
        try:
            cursor.execute(f"CREATE DATABASE {Config.POSTGRES_DB} OWNER {Config.POSTGRES_USER};")
            print(f"✓ Base de données {Config.POSTGRES_DB} créée")
        except psycopg2.errors.DuplicateDatabase:
            print(f"✓ Base de données {Config.POSTGRES_DB} existe déjà")
        
        # Donner tous les privilèges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {Config.POSTGRES_DB} TO {Config.POSTGRES_USER};")
        print(f"✓ Privilèges accordés à {Config.POSTGRES_USER}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de la base: {e}")
        print("Assurez-vous que PostgreSQL est installé et démarré")
        return False

def initialize_tables():
    """Initialise les tables de la base de données"""
    try:
        from src.database import DatabaseManager
        
        print("🔧 Initialisation des tables...")
        db_manager = DatabaseManager()
        print("✅ Tables initialisées avec succès!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des tables: {e}")
        return False

def main():
    """Fonction principale"""
    print("🗄️ Configuration de la base de données CyberGuard AI...")
    
    if create_database():
        if initialize_tables():
            print("✅ Base de données configurée avec succès!")
        else:
            print("❌ Erreur lors de l'initialisation des tables")
    else:
        print("❌ Erreur lors de la création de la base")

if __name__ == "__main__":
    main()

