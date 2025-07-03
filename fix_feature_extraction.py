import re

# Lire le fichier feature_extraction.py
with open('src/feature_extraction.py', 'r') as f:
    content = f.read()

# Corriger l'initialisation de connection_stats
content = re.sub(
    r'self\.connection_stats = defaultdict\(lambda: defaultdict\(int\)\)',
    'self.connection_stats = {}',
    content
)

# Corriger l'utilisation dans _extract_contextual_features
fix_contextual = '''
    def _extract_contextual_features(self, src_ip, dst_ip, src_port, dst_port):
        """Extrait les features contextuelles basées sur l'historique"""
        features = {}
        
        # Analyser les patterns de connexion
        current_time = datetime.now()
        time_window = current_time - timedelta(seconds=self.window_size)
        
        # Compter les connexions récentes de la même source
        src_connections = 0
        dst_connections = 0
        
        for (s_ip, d_ip, s_port, d_port, proto), conn_list in self.connection_stats.items():
            if isinstance(conn_list, list):
                if s_ip == src_ip:
                    src_connections += len([c for c in conn_list if c > time_window])
                if d_ip == dst_ip:
                    dst_connections += len([c for c in conn_list if c > time_window])
        
        features.update({
            'src_ip_connections': src_connections,
            'dst_ip_connections': dst_connections,
            'is_internal_src': self._is_internal_ip(src_ip),
            'is_internal_dst': self._is_internal_ip(dst_ip),
            'is_common_port': self._is_common_port(dst_port),
            'port_category': self._categorize_port(dst_port)
        })
        
        # Mettre à jour le cache des connexions - CORRECTION
        connection_key = (src_ip, dst_ip, src_port, dst_port, 'current')
        if connection_key not in self.connection_stats:
            self.connection_stats[connection_key] = []
        self.connection_stats[connection_key].append(current_time)
        
        return features
'''

# Remplacer la méthode
content = re.sub(
    r'def _extract_contextual_features\(self, src_ip, dst_ip, src_port, dst_port\):.*?return features',
    fix_contextual.strip(),
    content,
    flags=re.DOTALL
)

# Écrire le fichier corrigé
with open('src/feature_extraction.py', 'w') as f:
    f.write(content)

print("✅ feature_extraction.py corrigé")
