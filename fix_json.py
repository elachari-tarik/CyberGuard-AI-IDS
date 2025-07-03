import re

# Lire le fichier app.py
with open('web_interface/app.py', 'r') as f:
    content = f.read()

# Ajouter la fonction de sérialisation JSON après les imports
json_function = '''
# Fonction utilitaire pour sérialiser les dates JSON
def json_serial(obj):
    """Sérialiseur JSON pour les objets datetime"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

'''

# Insérer après les imports
content = re.sub(r'(from config\.config import Config\n)', r'\1\n' + json_function, content)

# Corriger les routes pour utiliser isoformat()
content = re.sub(r"'timestamp': alert\.timestamp,", "'timestamp': alert.timestamp.isoformat(),", content)
content = re.sub(r"'timestamp': flow\.timestamp,", "'timestamp': flow.timestamp.isoformat(),", content)

# Corriger les mises à jour temps réel
content = re.sub(
    r"'timestamp': datetime\.now\(\)",
    "'timestamp': datetime.now().isoformat()",
    content
)

# Écrire le fichier corrigé
with open('web_interface/app.py', 'w') as f:
    f.write(content)

print("✅ app.py corrigé pour JSON")
