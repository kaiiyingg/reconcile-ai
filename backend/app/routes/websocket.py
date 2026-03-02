"""
WebSocket routes: real-time updates for dashboard
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
import json
import asyncio

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "transactions": [],
            "anomalies": [],
            "predictions": []
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)
    
    async def broadcast(self, message: dict, channel: str):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/transactions")
async def websocket_transactions(websocket: WebSocket):
    """WebSocket endpoint for real-time transaction updates"""
    await manager.connect(websocket, "transactions")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            await websocket.send_json({
                "type": "transaction_update",
                "message": "Connected to transaction stream",
                "timestamp": str(asyncio.get_event_loop().time())
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "transactions")


@router.websocket("/ws/anomalies")
async def websocket_anomalies(websocket: WebSocket):
    """WebSocket endpoint for real-time anomaly updates"""
    await manager.connect(websocket, "anomalies")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            await websocket.send_json({
                "type": "anomaly_update",
                "message": "Connected to anomaly stream",
                "timestamp": str(asyncio.get_event_loop().time())
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "anomalies")


@router.websocket("/ws/predictions")
async def websocket_predictions(websocket: WebSocket):
    """WebSocket endpoint for real-time prediction updates"""
    await manager.connect(websocket, "predictions")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            await websocket.send_json({
                "type": "prediction_update",
                "message": "Connected to prediction stream",
                "timestamp": str(asyncio.get_event_loop().time())
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "predictions")


async def notify_new_transaction(transaction_data: dict):
    """Helper function to broadcast new transaction"""
    await manager.broadcast({
        "type": "new_transaction",
        "data": transaction_data
    }, "transactions")


async def notify_new_anomaly(anomaly_data: dict):
    """Helper function to broadcast new anomaly"""
    await manager.broadcast({
        "type": "new_anomaly",
        "data": anomaly_data
    }, "anomalies")


async def notify_new_prediction(prediction_data: dict):
    """Helper function to broadcast new prediction"""
    await manager.broadcast({
        "type": "new_prediction",
        "data": prediction_data
    }, "predictions")
