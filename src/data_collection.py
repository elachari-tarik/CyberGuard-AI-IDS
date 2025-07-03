from scapy.all import sniff, IP, TCP, UDP, ICMP
import threading
import queue
import time
from datetime import datetime
import logging
import random

class NetworkCapture:
    def __init__(self, interface='any', filter_str='ip'):
        self.interface = interface
        self.filter_str = filter_str
        self.packet_queue = queue.Queue(maxsize=10000)
        self.is_capturing = False
        self.capture_thread = None
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def packet_handler(self, packet):
        """Traite chaque paquet capturé"""
        try:
            if IP in packet:
                packet_info = self.extract_packet_info(packet)
                if packet_info:
                    self.packet_queue.put(packet_info, block=False)
        except queue.Full:
            self.logger.warning("Queue pleine, paquet ignoré")
        except Exception as e:
            self.logger.error(f"Erreur traitement paquet: {e}")
    
    def extract_packet_info(self, packet):
        """Extrait les informations importantes du paquet"""
        try:
            packet_info = {
                'timestamp': datetime.now(),
                'src_ip': packet[IP].src,
                'dst_ip': packet[IP].dst,
                'protocol': packet[IP].proto,
                'packet_size': len(packet),
                'ttl': packet[IP].ttl,
                'flags': packet[IP].flags
            }
            
            # Informations spécifiques TCP
            if TCP in packet:
                packet_info.update({
                    'src_port': packet[TCP].sport,
                    'dst_port': packet[TCP].dport,
                    'tcp_flags': packet[TCP].flags,
                    'window_size': packet[TCP].window,
                    'protocol_name': 'TCP'
                })
            
            # Informations spécifiques UDP
            elif UDP in packet:
                packet_info.update({
                    'src_port': packet[UDP].sport,
                    'dst_port': packet[UDP].dport,
                    'protocol_name': 'UDP'
                })
            
            # Informations spécifiques ICMP
            elif ICMP in packet:
                packet_info.update({
                    'icmp_type': packet[ICMP].type,
                    'icmp_code': packet[ICMP].code,
                    'protocol_name': 'ICMP'
                })
            
            return packet_info
            
        except Exception as e:
            self.logger.error(f"Erreur extraction packet info: {e}")
            return None
    
    def start_capture(self):
        """Démarre la capture réseau"""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        self.logger.info(f"Capture démarrée sur interface {self.interface}")
    
    def _capture_loop(self):
        """Boucle principale de capture"""
        try:
            sniff(
                iface=self.interface,
                filter=self.filter_str,
                prn=self.packet_handler,
                stop_filter=lambda x: not self.is_capturing
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la capture: {e}")
    
    def stop_capture(self):
        """Arrête la capture réseau"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        self.logger.info("Capture arrêtée")
    
    def get_packets(self, max_packets=None):
        """Récupère les paquets de la queue"""
        packets = []
        count = 0
        
        while not self.packet_queue.empty():
            if max_packets and count >= max_packets:
                break
            try:
                packet = self.packet_queue.get_nowait()
                packets.append(packet)
                count += 1
            except queue.Empty:
                break
        
        return packets

class SimulatedCapture:
    """Capture simulée AGRESSIVE pour tests et développement - VERSION CORRIGÉE"""
    def __init__(self):
        self.packet_queue = queue.Queue()
        self.is_simulating = False
        self.logger = logging.getLogger(__name__)
        
    def generate_simulated_traffic(self):
        """Génère du trafic réseau simulé AGRESSIF avec beaucoup d'attaques"""
        
        # *** PATTERNS D'ATTAQUES PLUS AGRESSIFS ***
        attack_patterns = [
            # Brute Force SSH
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 22, 'protocol_name': 'TCP', 'attack_type': 'ssh_brute'},
            {'src_ip': '10.0.0.100', 'dst_ip': '172.23.73.174', 'dst_port': 22, 'protocol_name': 'TCP', 'attack_type': 'ssh_brute'},
            
            # Port Scanning
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 80, 'protocol_name': 'TCP', 'attack_type': 'port_scan'},
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 443, 'protocol_name': 'TCP', 'attack_type': 'port_scan'},
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 21, 'protocol_name': 'TCP', 'attack_type': 'port_scan'},
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 3389, 'protocol_name': 'TCP', 'attack_type': 'port_scan'},
            
            # DDoS Simulation
            {'src_ip': '203.0.113.1', 'dst_ip': '172.23.73.174', 'dst_port': 80, 'protocol_name': 'TCP', 'attack_type': 'ddos'},
            {'src_ip': '198.51.100.1', 'dst_ip': '172.23.73.174', 'dst_port': 443, 'protocol_name': 'TCP', 'attack_type': 'ddos'},
            
            # SMB Attacks
            {'src_ip': '172.16.0.1', 'dst_ip': '172.23.73.174', 'dst_port': 445, 'protocol_name': 'TCP', 'attack_type': 'smb'},
            {'src_ip': '172.16.0.1', 'dst_ip': '172.23.73.174', 'dst_port': 139, 'protocol_name': 'TCP', 'attack_type': 'smb'},
            
            # Web Attacks
            {'src_ip': '185.220.101.1', 'dst_ip': '172.23.73.174', 'dst_port': 80, 'protocol_name': 'TCP', 'attack_type': 'web_attack'},
            {'src_ip': '185.220.101.2', 'dst_ip': '172.23.73.174', 'dst_port': 8080, 'protocol_name': 'TCP', 'attack_type': 'web_attack'},
            
            # DNS Tunneling
            {'src_ip': '8.8.8.8', 'dst_ip': '172.23.73.174', 'dst_port': 53, 'protocol_name': 'TCP', 'attack_type': 'dns_tunnel'},
            
            # RDP Brute Force
            {'src_ip': '94.102.49.1', 'dst_ip': '172.23.73.174', 'dst_port': 3389, 'protocol_name': 'TCP', 'attack_type': 'rdp_brute'},
            
            # ICMP Flood
            {'src_ip': '172.23.64.1', 'dst_ip': '172.23.73.174', 'dst_port': 0, 'protocol_name': 'ICMP', 'attack_type': 'icmp_flood'},
        ]
        
        # *** PATTERNS NORMAUX (MOINS FRÉQUENTS) ***
        normal_patterns = [
            {'src_ip': '172.23.73.174', 'dst_ip': '8.8.8.8', 'dst_port': 53, 'protocol_name': 'UDP'},
            {'src_ip': '172.23.73.174', 'dst_ip': '172.217.16.46', 'dst_port': 443, 'protocol_name': 'TCP'},
            {'src_ip': '172.23.73.174', 'dst_ip': '151.101.65.140', 'dst_port': 80, 'protocol_name': 'TCP'},
        ]
        
        packet_counter = 0
        attack_burst_counter = 0
        
        while self.is_simulating:
            packet_counter += 1
            
            # *** CORRECTION CRITIQUE: 70% d'attaques au lieu de 10% ***
            if random.random() < 0.7:  # 70% d'attaques pour forcer la détection
                pattern = random.choice(attack_patterns)
                attack_burst_counter += 1
                
                # Générer des bursts d'attaques pour simuler des vraies attaques
                if pattern['attack_type'] in ['ssh_brute', 'rdp_brute']:
                    burst_size = random.randint(5, 15)  # Burst de 5-15 paquets
                elif pattern['attack_type'] in ['port_scan', 'ddos']:
                    burst_size = random.randint(10, 50)  # Burst plus important
                elif pattern['attack_type'] == 'icmp_flood':
                    burst_size = random.randint(20, 100)  # ICMP flood intense
                else:
                    burst_size = random.randint(3, 10)
                
                # Générer le burst
                for _ in range(burst_size):
                    packet_info = self._create_attack_packet(pattern, packet_counter)
                    try:
                        self.packet_queue.put(packet_info, block=False)
                    except queue.Full:
                        pass
                
                # Log des attaques générées
                if attack_burst_counter % 10 == 0:
                    self.logger.info(f"🚨 Génération d'attaque #{attack_burst_counter}: {pattern['attack_type']} "
                                   f"({pattern['src_ip']} -> {pattern['dst_ip']}:{pattern['dst_port']})")
                
                # Délai plus court pour les attaques
                time.sleep(random.uniform(0.01, 0.1))
                
            else:
                # Trafic normal (30%)
                pattern = random.choice(normal_patterns)
                packet_info = self._create_normal_packet(pattern, packet_counter)
                
                try:
                    self.packet_queue.put(packet_info, block=False)
                except queue.Full:
                    pass
                
                # Délai plus long pour le trafic normal
                time.sleep(random.uniform(0.1, 0.5))
    
    def _create_attack_packet(self, pattern, counter):
        """Crée un paquet d'attaque avec caractéristiques suspectes"""
        packet_info = {
            'timestamp': datetime.now(),
            'src_ip': pattern['src_ip'],
            'dst_ip': pattern['dst_ip'],
            'src_port': random.randint(1024, 65535),
            'dst_port': pattern['dst_port'],
            'protocol_name': pattern['protocol_name'],
            'packet_size': self._get_attack_packet_size(pattern['attack_type']),
            'ttl': random.randint(32, 128),
            'flags': self._get_attack_flags(pattern['attack_type'])
        }
        
        # Ajouter des caractéristiques spécifiques aux attaques
        if pattern['attack_type'] in ['ssh_brute', 'rdp_brute']:
            packet_info['tcp_flags'] = 0x02  # SYN flag pour tentatives de connexion
            packet_info['window_size'] = random.randint(1024, 8192)
        
        elif pattern['attack_type'] == 'port_scan':
            packet_info['tcp_flags'] = 0x02  # SYN scan
            packet_info['window_size'] = 1024  # Petite window typique des scans
            
        elif pattern['attack_type'] == 'ddos':
            packet_info['packet_size'] = random.randint(1200, 1500)  # Gros paquets
            packet_info['tcp_flags'] = random.choice([0x02, 0x10, 0x04])  # Mélange de flags
            
        elif pattern['attack_type'] == 'icmp_flood':
            packet_info['icmp_type'] = 8  # ICMP Echo Request
            packet_info['icmp_code'] = 0
            packet_info['packet_size'] = random.randint(1000, 1500)  # Gros pings
        
        return packet_info
    
    def _create_normal_packet(self, pattern, counter):
        """Crée un paquet normal"""
        return {
            'timestamp': datetime.now(),
            'src_ip': pattern['src_ip'],
            'dst_ip': pattern['dst_ip'],
            'src_port': random.randint(1024, 65535),
            'dst_port': pattern['dst_port'],
            'protocol_name': pattern['protocol_name'],
            'packet_size': random.randint(64, 1200),
            'ttl': random.randint(64, 255),
            'flags': random.randint(0, 31)
        }
    
    def _get_attack_packet_size(self, attack_type):
        """Retourne une taille de paquet typique pour chaque type d'attaque"""
        sizes = {
            'ssh_brute': random.randint(40, 100),       # Petits paquets de connexion
            'rdp_brute': random.randint(100, 300),      # Paquets RDP moyens
            'port_scan': random.randint(40, 80),        # Très petits paquets SYN
            'ddos': random.randint(1200, 1500),         # Gros paquets pour saturer
            'smb': random.randint(200, 800),            # Paquets SMB variables
            'web_attack': random.randint(300, 1200),    # Requêtes HTTP variables
            'dns_tunnel': random.randint(200, 500),     # DNS queries avec données
            'icmp_flood': random.randint(1000, 1500),   # Gros pings
        }
        return sizes.get(attack_type, random.randint(64, 1500))
    
    def _get_attack_flags(self, attack_type):
        """Retourne des flags IP typiques pour chaque type d'attaque"""
        # Flags IP: bit 1 = Don't Fragment, bit 2 = More Fragments
        flags = {
            'ssh_brute': 2,        # Don't Fragment
            'rdp_brute': 2,        # Don't Fragment  
            'port_scan': 2,        # Don't Fragment
            'ddos': random.choice([0, 2, 3]),  # Mélange de flags
            'smb': 2,              # Don't Fragment
            'web_attack': 2,       # Don't Fragment
            'dns_tunnel': 0,       # Pas de flags spéciaux
            'icmp_flood': 0,       # Pas de flags spéciaux
        }
        return flags.get(attack_type, random.randint(0, 3))
    
    def start_capture(self):
        """Démarre la simulation AGRESSIVE"""
        self.is_simulating = True
        self.sim_thread = threading.Thread(target=self.generate_simulated_traffic)
        self.sim_thread.daemon = True
        self.sim_thread.start()
        self.logger.info("🚨 Simulation AGRESSIVE démarrée - 70% d'attaques")
    
    def stop_capture(self):
        """Arrête la simulation"""
        self.is_simulating = False
        self.logger.info("Simulation arrêtée")
    
    def get_packets(self, max_packets=None):
        """Récupère les paquets simulés"""
        packets = []
        count = 0
        
        while not self.packet_queue.empty():
            if max_packets and count >= max_packets:
                break
            try:
                packet = self.packet_queue.get_nowait()
                packets.append(packet)
                count += 1
            except queue.Empty:
                break
        
        return packets
