import re

# Lire le fichier detection_engine.py
with open('src/detection_engine.py', 'r') as f:
    content = f.read()

# Corriger l'initialisation de alert_history
content = re.sub(
    r'self\.alert_history = defaultdict\(list\)',
    'self.alert_history = {}',
    content
)

# Corriger la méthode _add_to_history dans alert_system.py
content = re.sub(
    r'self\.alert_history\[source_ip\]\.append\(history_entry\)',
    '''if source_ip not in self.alert_history:
            self.alert_history[source_ip] = []
        self.alert_history[source_ip].append(history_entry)''',
    content
)

# Écrire le fichier corrigé
with open('src/detection_engine.py', 'w') as f:
    f.write(content)

print("✅ detection_engine.py corrigé pour defaultdict")
