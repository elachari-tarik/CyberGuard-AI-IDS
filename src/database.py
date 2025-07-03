#!/usr/bin/env python3
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
import numpy as np  # ← Ajout de l'import numpy
from config.config import Config

Base = declarative_base()

class NetworkFlow(Base):
    __tablename__ = 'network_flows'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    src_ip = Column(String(45))
    dst_ip = Column(String(45))
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))
    packet_count = Column(Integer)
    byte_count = Column(Integer)
    duration = Column(Float)
    features = Column(Text)
    prediction = Column(String(20))
    confidence = Column(Float)
    is_anomaly = Column(Boolean, default=False)

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(50))
    severity = Column(String(20))
    src_ip = Column(String(45))
    dst_ip = Column(String(45))
    description = Column(Text)
    confidence = Column(Float)
    status = Column(String(20), default='New')

def serialize_datetime(obj):
    """Fonction pour sérialiser les objets datetime en JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def convert_numpy_types(value):
    """Convertit les types NumPy en types Python natifs"""
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    else:
        return value

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.NetworkFlow = NetworkFlow
        self.Alert = Alert
    
    def save_network_flow(self, flow_data):
        """Sauvegarde un flux réseau analysé - VERSION CORRIGÉE NUMPY"""
        try:
            # Nettoyer les features pour éviter les erreurs de sérialisation
            features = flow_data.get('features', {})
            
            # Convertir tous les types NumPy et datetime en types Python natifs
            cleaned_features = {}
            for key, value in features.items():
                cleaned_features[key] = convert_numpy_types(value)
            
            # *** CORRECTION CRITIQUE : Convertir confidence en float Python ***
            confidence_value = flow_data.get('confidence')
            if isinstance(confidence_value, np.floating):
                confidence_value = float(confidence_value)
            elif confidence_value is None:
                confidence_value = 0.0
            
            # *** CORRECTION : Convertir tous les autres champs NumPy ***
            flow = NetworkFlow(
                src_ip=flow_data.get('src_ip'),
                dst_ip=flow_data.get('dst_ip'),
                src_port=convert_numpy_types(flow_data.get('src_port')),
                dst_port=convert_numpy_types(flow_data.get('dst_port')),
                protocol=flow_data.get('protocol'),
                packet_count=convert_numpy_types(flow_data.get('packet_count')),
                byte_count=convert_numpy_types(flow_data.get('byte_count')),
                duration=convert_numpy_types(flow_data.get('duration')),
                features=json.dumps(cleaned_features, default=serialize_datetime),
                prediction=flow_data.get('prediction'),
                confidence=confidence_value,  # ← CORRECTION ICI
                is_anomaly=convert_numpy_types(flow_data.get('is_anomaly', False))
            )
            self.session.add(flow)
            self.session.commit()
            return flow.id
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la sauvegarde du flux: {e}")
            return None
    
    def create_alert(self, alert_data):
        """Crée une nouvelle alerte"""
        try:
            # Convertir les types NumPy en types Python
            confidence_value = alert_data.get('confidence')
            if isinstance(confidence_value, np.floating):
                confidence_value = float(confidence_value)
            
            alert = Alert(
                alert_type=alert_data.get('alert_type'),
                severity=alert_data.get('severity'),
                src_ip=alert_data.get('source_ip'),
                dst_ip=alert_data.get('target_ip'),
                description=alert_data.get('description'),
                confidence=confidence_value
            )
            self.session.add(alert)
            self.session.commit()
            return alert.id
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création de l'alerte: {e}")
            return None
    
    def get_recent_alerts(self, limit=50):
        """Récupère les alertes récentes"""
        try:
            return self.session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des alertes: {e}")
            return []
    
    def get_flows_by_timeframe(self, hours=24):
        """Récupère les flux des dernières heures"""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return self.session.query(NetworkFlow).filter(NetworkFlow.timestamp >= cutoff).all()
        except Exception as e:
            print(f"Erreur lors de la récupération des flux: {e}")
            return []
