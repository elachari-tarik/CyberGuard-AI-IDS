import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import ipaddress

class NetworkFeatureExtractor:
    def __init__(self, window_size=30):
        self.window_size = window_size  # secondes
        self.flow_cache = defaultdict(list)
        self.connection_stats = {}
        
    def extract_features_from_packets(self, packets):
        """Extrait les features à partir des paquets capturés"""
        if not packets:
            return []
        
        # Grouper les paquets par connexion
        flows = self._group_packets_to_flows(packets)
        
        # Extraire les features pour chaque flux
        features_list = []
        for flow_key, flow_packets in flows.items():
            features = self._extract_flow_features(flow_key, flow_packets)
            features_list.append(features)
        
        return features_list
    
    def _group_packets_to_flows(self, packets):
        """Groupe les paquets en flux de connexion"""
        flows = defaultdict(list)
        
        for packet in packets:
            # Créer une clé unique pour chaque flux bidirectionnel
            src_ip = packet.get('src_ip', '')
            dst_ip = packet.get('dst_ip', '')
            src_port = packet.get('src_port', 0)
            dst_port = packet.get('dst_port', 0)
            protocol = packet.get('protocol_name', 'Unknown')
            
            # Normaliser la direction du flux
            if src_ip < dst_ip or (src_ip == dst_ip and src_port < dst_port):
                flow_key = (src_ip, dst_ip, src_port, dst_port, protocol)
            else:
                flow_key = (dst_ip, src_ip, dst_port, src_port, protocol)
            
            flows[flow_key].append(packet)
        
        return flows
    
    def _extract_flow_features(self, flow_key, packets):
        """Extrait les features pour un flux donné"""
        src_ip, dst_ip, src_port, dst_port, protocol = flow_key
        
        # Features de base du flux
        features = {
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': protocol,
            'flow_id': f"{src_ip}:{src_port}-{dst_ip}:{dst_port}",
        }
        
        # Statistiques temporelles
        timestamps = [p['timestamp'] for p in packets]
        if timestamps:
            duration = (max(timestamps) - min(timestamps)).total_seconds()
            features['duration'] = max(duration, 0.001)  # Éviter division par zéro
            features['start_time'] = min(timestamps)
        else:
            features['duration'] = 0.001
            features['start_time'] = datetime.now()
        
        # Statistiques de paquets et octets
        packet_sizes = [p.get('packet_size', 0) for p in packets]
        features.update({
            'packet_count': len(packets),
            'total_bytes': sum(packet_sizes),
            'avg_packet_size': np.mean(packet_sizes) if packet_sizes else 0,
            'min_packet_size': min(packet_sizes) if packet_sizes else 0,
            'max_packet_size': max(packet_sizes) if packet_sizes else 0,
            'std_packet_size': np.std(packet_sizes) if len(packet_sizes) > 1 else 0,
            'bytes_per_second': sum(packet_sizes) / features['duration'],
            'packets_per_second': len(packets) / features['duration']
        })
        
        # Features TCP spécifiques
        if protocol == 'TCP':
            tcp_flags = [p.get('tcp_flags', 0) for p in packets if 'tcp_flags' in p]
            window_sizes = [p.get('window_size', 0) for p in packets if 'window_size' in p]
            
            features.update({
                'syn_count': sum(1 for flag in tcp_flags if flag & 0x02),
                'ack_count': sum(1 for flag in tcp_flags if flag & 0x10),
                'fin_count': sum(1 for flag in tcp_flags if flag & 0x01),
                'rst_count': sum(1 for flag in tcp_flags if flag & 0x04),
                'psh_count': sum(1 for flag in tcp_flags if flag & 0x08),
                'urg_count': sum(1 for flag in tcp_flags if flag & 0x20),
                'avg_window_size': np.mean(window_sizes) if window_sizes else 0
            })
        else:
            # Valeurs par défaut pour non-TCP
            for flag_type in ['syn', 'ack', 'fin', 'rst', 'psh', 'urg']:
                features[f'{flag_type}_count'] = 0
            features['avg_window_size'] = 0
        
        # Features contextuelles et statistiques d'hôte
        features.update(self._extract_contextual_features(src_ip, dst_ip, src_port, dst_port))
        
        # Features de détection d'anomalies
        features.update(self._extract_anomaly_features(features))
        
        return features
    
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
    
    def _extract_anomaly_features(self, base_features):
        """Extrait des features spécifiques à la détection d'anomalies"""
        features = {}
        
        # Ratios et métriques dérivées
        packet_count = base_features.get('packet_count', 1)
        duration = base_features.get('duration', 0.001)
        
        features.update({
            'bytes_per_packet': base_features.get('total_bytes', 0) / packet_count,
            'connection_rate': packet_count / duration,
            'protocol_anomaly_score': self._calculate_protocol_anomaly_score(base_features),
            'size_anomaly_score': self._calculate_size_anomaly_score(base_features),
            'temporal_anomaly_score': self._calculate_temporal_anomaly_score(base_features)
        })
        
        return features
    
    def _is_internal_ip(self, ip_str):
        """Vérifie si l'IP est dans un réseau privé"""
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private
        except:
            return False
    
    def _is_common_port(self, port):
        """Vérifie si le port est couramment utilisé"""
        common_ports = {80, 443, 53, 22, 21, 25, 110, 993, 995, 143, 993, 587}
        return port in common_ports
    
    def _categorize_port(self, port):
        """Catégorise le port selon son usage"""
        if port < 1024:
            return 'system'
        elif port < 49152:
            return 'registered'
        else:
            return 'dynamic'
    
    def _calculate_protocol_anomaly_score(self, features):
        """Calculate protocol-based anomaly score"""
        score = 0
        
        # Vérification des combinaisons anormales protocol/port
        protocol = features.get('protocol', '')
        dst_port = features.get('dst_port', 0)
        
        # Protocole inhabituel pour le port
        if protocol == 'UDP' and dst_port in [80, 443, 22]:
            score += 0.3
        elif protocol == 'TCP' and dst_port == 53:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_size_anomaly_score(self, features):
        """Calculate size-based anomaly score"""
        avg_size = features.get('avg_packet_size', 0)
        std_size = features.get('std_packet_size', 0)
        
        # Tailles de paquets inhabituelles
        if avg_size > 1400:  # Paquets très grands
            return 0.4
        elif avg_size < 50:  # Paquets très petits
            return 0.3
        elif std_size > 500:  # Variation importante
            return 0.2
        
        return 0.0
    
    def _calculate_temporal_anomaly_score(self, features):
        """Calculate temporal-based anomaly score"""
        duration = features.get('duration', 0)
        packet_count = features.get('packet_count', 1)
        
        # Connexions très rapides avec beaucoup de paquets (possible scan)
        if duration < 1 and packet_count > 10:
            return 0.5
        
        # Connexions très longues avec peu de données
        elif duration > 300 and features.get('total_bytes', 0) < 1000:
            return 0.3
        
        return 0.0
    
    def create_feature_dataframe(self, features_list):
        """Convertit la liste de features en DataFrame pour ML"""
        if not features_list:
            return pd.DataFrame()
        
        # Sélectionner uniquement les features numériques pour ML
        numeric_features = [
            'duration', 'packet_count', 'total_bytes', 'avg_packet_size',
            'min_packet_size', 'max_packet_size', 'std_packet_size',
            'bytes_per_second', 'packets_per_second', 'syn_count', 'ack_count',
            'fin_count', 'rst_count', 'psh_count', 'urg_count', 'avg_window_size',
            'src_ip_connections', 'dst_ip_connections', 'bytes_per_packet',
            'connection_rate', 'protocol_anomaly_score', 'size_anomaly_score',
            'temporal_anomaly_score'
        ]
        
        # Ajouter des features catégorielles encodées
        categorical_features = ['protocol', 'port_category']
        
        df_data = []
        for features in features_list:
            row = {}
            
            # Features numériques
            for feature in numeric_features:
                row[feature] = features.get(feature, 0)
            
            # Encodage des features catégorielles
            protocol = features.get('protocol', 'Unknown')
            row['protocol_tcp'] = 1 if protocol == 'TCP' else 0
            row['protocol_udp'] = 1 if protocol == 'UDP' else 0
            row['protocol_icmp'] = 1 if protocol == 'ICMP' else 0
            
            port_category = features.get('port_category', 'dynamic')
            row['port_system'] = 1 if port_category == 'system' else 0
            row['port_registered'] = 1 if port_category == 'registered' else 0
            
            # Features booléennes
            row['is_internal_src'] = 1 if features.get('is_internal_src', False) else 0
            row['is_internal_dst'] = 1 if features.get('is_internal_dst', False) else 0
            row['is_common_port'] = 1 if features.get('is_common_port', False) else 0
            
            # Métadonnées (non utilisées pour ML mais utiles pour le contexte)
            row['flow_id'] = features.get('flow_id', '')
            row['src_ip'] = features.get('src_ip', '')
            row['dst_ip'] = features.get('dst_ip', '')
            row['src_port'] = features.get('src_port', 0)
            row['dst_port'] = features.get('dst_port', 0)
            
            df_data.append(row)
        
        return pd.DataFrame(df_data)

