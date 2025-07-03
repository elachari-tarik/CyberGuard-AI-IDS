#!/usr/bin/env python3
"""
Application Flask pour l'interface web de CyberGuard AI - VERSION CORRIGÉE
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection_engine import IDSDetectionEngine
from src.database import DatabaseManager
from src.alert_system import AlertManager
from config.config import Config

# Initialisation de l'application Flask
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialisation des composants
db_manager = DatabaseManager()
alert_manager = AlertManager(db_manager)
ids_engine = None

@app.route('/')
def dashboard():
    """Page principale du dashboard"""
    return render_template('dashboard.html')

@app.route('/alerts')
def alerts_page():
    """Page des alertes détaillées"""
    return render_template('alerts.html')

@app.route('/api/status')
def get_system_status():
    """API: Statut du système IDS"""
    try:
        if ids_engine:
            status = {
                'is_running': ids_engine.is_running,
                'buffer_size': len(ids_engine.packet_buffer) if hasattr(ids_engine, 'packet_buffer') else 0,
                'stats': ids_engine.get_stats(),
                'last_analysis': datetime.now().isoformat()
            }
            return jsonify({
                'status': 'success',
                'data': status
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'IDS Engine not initialized'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/alerts')
def get_alerts():
    """API: Récupération des alertes"""
    try:
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        # Récupérer les alertes de la base de données
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = db_manager.session.query(db_manager.Alert).filter(
            db_manager.Alert.timestamp >= cutoff_time
        ).order_by(db_manager.Alert.timestamp.desc()).limit(limit).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'source_ip': alert.src_ip,
                'target_ip': alert.dst_ip,
                'description': alert.description,
                'confidence': alert.confidence,
                'status': alert.status
            })
        
        return jsonify({
            'status': 'success',
            'data': alerts_data,
            'total': len(alerts_data)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/stats')
def get_statistics():
    """API: Statistiques du système"""
    try:
        # Statistiques du moteur IDS
        ids_stats = ids_engine.get_stats() if ids_engine else {}
        
        # Statistiques des alertes
        alert_stats = alert_manager.get_alert_statistics()
        
        # Statistiques réseau des dernières 24h
        flows = db_manager.get_flows_by_timeframe(24)
        
        network_stats = {
            'total_flows': len(flows),
            'unique_src_ips': len(set(flow.src_ip for flow in flows if flow.src_ip)),
            'unique_dst_ips': len(set(flow.dst_ip for flow in flows if flow.dst_ip)),
            'protocols': {},
            'anomaly_rate': 0
        }
        
        if flows:
            protocol_count = {}
            anomaly_count = 0
            
            for flow in flows:
                protocol = flow.protocol or 'Unknown'
                protocol_count[protocol] = protocol_count.get(protocol, 0) + 1
                if flow.is_anomaly:
                    anomaly_count += 1
            
            network_stats['protocols'] = protocol_count
            network_stats['anomaly_rate'] = (anomaly_count / len(flows)) * 100
        
        return jsonify({
            'status': 'success',
            'data': {
                'ids_stats': ids_stats,
                'alert_stats': alert_stats,
                'network_stats': network_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/control/start', methods=['POST'])
def start_ids():
    """API: Démarrer le moteur IDS"""
    global ids_engine
    try:
        if not ids_engine:
            ids_engine = IDSDetectionEngine(Config)
            ids_engine.initialize(use_simulation=True)
        
        ids_engine.start()
        alert_manager.start()
        
        return jsonify({
            'status': 'success',
            'message': 'IDS Engine started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/control/stop', methods=['POST'])
def stop_ids():
    """API: Arrêter le moteur IDS"""
    global ids_engine
    try:
        if ids_engine:
            ids_engine.stop()
        alert_manager.stop()
        
        return jsonify({
            'status': 'success',
            'message': 'IDS Engine stopped successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Gestion des connexions WebSocket"""
    print('Client connecté au WebSocket')
    emit('status', {'message': 'Connecté au système CyberGuard AI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion des déconnexions WebSocket"""
    print('Client déconnecté du WebSocket')

def real_time_updates():
    """Thread pour les mises à jour en temps réel - VERSION CORRIGÉE"""
    while True:
        try:
            if ids_engine and ids_engine.is_running:
                # Récupérer les statistiques de base
                stats = ids_engine.get_stats()
                
                # Préparer les données pour WebSocket (tout en string/int/float)
                update_data = {
                    'ids_stats': {
                        'packets_processed': stats.get('packets_processed', 0),
                        'flows_analyzed': stats.get('flows_analyzed', 0),
                        'anomalies_detected': stats.get('anomalies_detected', 0),
                        'alerts_generated': stats.get('alerts_generated', 0)
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                socketio.emit('stats_update', update_data)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Erreur dans les mises à jour temps réel: {e}")
            time.sleep(10)

# Démarrer le thread des mises à jour en temps réel
update_thread = threading.Thread(target=real_time_updates)
update_thread.daemon = True
update_thread.start()

if __name__ == '__main__':
    # Initialiser le moteur IDS au démarrage
    ids_engine = IDSDetectionEngine(Config)
    if ids_engine.initialize(use_simulation=True):
        ids_engine.start()
        alert_manager.start()
        print("CyberGuard AI IDS démarré avec succès!")
    
    # Démarrer l'application Flask
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
