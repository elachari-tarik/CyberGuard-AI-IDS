#!/usr/bin/env python3
import os
import re

def fix_file(filepath, fixes):
    with open(filepath, 'r') as f:
        content = f.read()
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"✅ {filepath} corrigé")

# Corrections pour database.py
db_fixes = [
    (r'class DatabaseManager:', 'class DatabaseManager:\n    def __init__(self):\n        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)\n        Base.metadata.create_all(self.engine)\n        Session = sessionmaker(bind=self.engine)\n        self.session = Session()\n        self.NetworkFlow = NetworkFlow\n        self.Alert = Alert')
]

# Corrections pour detection_engine.py  
de_fixes = [
    (r'import sys', 'import sys\nimport os'),
    (r'self\.alert_history\.append', 'self.alert_history[source_ip].append')
]

# Appliquer les corrections
if os.path.exists('src/database.py'):
    fix_file('src/database.py', db_fixes)

if os.path.exists('src/detection_engine.py'):
    fix_file('src/detection_engine.py', de_fixes)

print("🎉 Corrections appliquées!")
