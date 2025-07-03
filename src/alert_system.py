#!/usr/bin/env python3
"""
Système de gestion des alertes pour CyberGuard AI
"""
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import threading
import time

class AlertManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.alert_rules = self._load_alert_rules()
        self.alert_buffer = []
        self.notification_queue = []
        
        # Configuration
        self.max_alerts_per_minute = 10
        self.alert_correlation_window = 300  # 5 minutes
        
        # Historique pour éviter le spam
        self.alert_history = defaultdict(list)
        
        # Thread de traitement des notifications
        self.notification_thread = None
        self.is_running = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_alert_rules(self):
        """Charge les règles d'alertes"""
        return {
            'Brute Force Attack': {
                'min_confidence': 0.7,
                'correlation_time': 600,
                'max_occurrences': 3,
                'notify_email': True,
                'auto_block': False
            },
            'Port Scan': {
                'min_confidence': 0.6,
                'correlation_time': 300,
                'max_occurrences': 5,
                'notify_email': True,
                'auto_block': False
            },
            'DDoS Attack': {
                'min_confidence': 0.8,
                'correlation_time': 60,
                'max_occurrences': 1,
                'notify_email': True,
                'auto_block': True
            }
        }
    
    def start(self):
        """Démarre le gestionnaire d'alertes"""
        if self.is_running:
            return
        
        self.is_running = True
        self.notification_thread = threading.Thread(target=self._notification_loop)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        
        self.logger.info("Gestionnaire d'alertes démarré")
    
    def stop(self):
        """Arrête le gestionnaire d'alertes"""
        self.is_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=5)
        
        self.logger.info("Gestionnaire d'alertes arrêté")
    
    def process_alert(self, alert_data):
        """Traite une nouvelle alerte"""
        try:
            alert_type = alert_data.get('alert_type', 'Unknown')
            source_ip = alert_data.get('source_ip', 'Unknown')
            
            # Notifier le dashboard
            self._notify_dashboard(alert_data)
            
            # Ajouter à l'historique
            self._add_to_history(alert_data)
            
            self.logger.info(f"Alerte traitée: {alert_type} de {source_ip}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de l'alerte: {e}")
            return False
    
    def _notify_dashboard(self, alert_data):
        """Notifie le dashboard web en temps réel"""
        notification = {
            'type': 'new_alert',
            'timestamp': datetime.now().isoformat(),
            'data': alert_data
        }
        
        self.notification_queue.append(notification)
        
        if len(self.notification_queue) > 100:
            self.notification_queue.pop(0)
    
    def _add_to_history(self, alert_data):
        """Ajoute l'alerte à l'historique"""
        source_ip = alert_data.get('source_ip', 'Unknown')
        
        history_entry = {
            'timestamp': datetime.now(),
            'alert_type': alert_data.get('alert_type'),
            'severity': alert_data.get('severity'),
            'confidence': alert_data.get('confidence')
        }
        
        if source_ip not in self.alert_history:
            self.alert_history[source_ip] = []
        
        self.alert_history[source_ip].append(history_entry)
        
        # Nettoyer l'historique ancien
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alert_history[source_ip] = [
            entry for entry in self.alert_history[source_ip]
            if entry['timestamp'] > cutoff_time
        ]
    
    def _notification_loop(self):
        """Boucle de traitement des notifications"""
        while self.is_running:
            try:
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de notification: {e}")
                time.sleep(5)
    
    def get_recent_notifications(self, limit=50):
        """Récupère les notifications récentes pour le dashboard"""
        dashboard_notifications = [
            notif for notif in self.notification_queue
            if notif.get('type') in ['new_alert', 'ip_blocked', 'escalation']
        ]
        
        return dashboard_notifications[-limit:]
    
    def get_alert_statistics(self, hours=24):
        """Récupère les statistiques d'alertes"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            alerts = self.db_manager.session.query(
                self.db_manager.Alert
            ).filter(
                self.db_manager.Alert.timestamp >= cutoff_time
            ).all()
            
            stats = {
                'total_alerts': len(alerts),
                'by_severity': {},
                'by_type': {},
                'by_hour': {},
                'top_source_ips': {}
            }
            
            severity_count = defaultdict(int)
            type_count = defaultdict(int)
            hour_count = defaultdict(int)
            ip_count = defaultdict(int)
            
            for alert in alerts:
                severity_count[alert.severity] += 1
                type_count[alert.alert_type] += 1
                hour_count[alert.timestamp.hour] += 1
                if alert.src_ip:  # ← CORRECTION: src_ip au lieu de source_ip
                    ip_count[alert.src_ip] += 1
            
            # Convertir en dict normaux pour JSON
            stats['by_severity'] = dict(severity_count)
            stats['by_type'] = dict(type_count)
            stats['by_hour'] = dict(hour_count)
            stats['top_source_ips'] = dict(ip_count)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_type': {},
                'by_hour': {},
                'top_source_ips': {}
            }
