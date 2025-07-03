import re

# Lire le fichier app.py
with open('web_interface/app.py', 'r') as f:
    content = f.read()

# Corriger la fonction real_time_updates
new_function = '''
def real_time_updates():
    """Thread pour les mises à jour en temps réel"""
    while True:
        try:
            if ids_engine and ids_engine.is_running:
                # Récupérer les nouvelles notifications
                notifications = alert_manager.get_recent_notifications(10)
                
                if notifications:
                    socketio.emit('new_alerts', notifications)
                
                # Mettre à jour les statistiques - CORRECTION ICI
                stats = {
                    'ids_stats': ids_engine.get_stats(),
                    'timestamp': datetime.now().isoformat()  # Déjà en string
                }
                socketio.emit('stats_update', stats)
            
            time.sleep(5)  # Mise à jour toutes les 5 secondes
            
        except Exception as e:
            print(f"Erreur dans les mises à jour temps réel: {e}")
            time.sleep(10)
'''

# Remplacer la fonction
content = re.sub(
    r'def real_time_updates\(\):.*?time\.sleep\(10\)',
    new_function.strip(),
    content,
    flags=re.DOTALL
)

# Écrire le fichier corrigé
with open('web_interface/app.py', 'w') as f:
    f.write(content)

print("✅ app.py corrigé pour isoformat")
