"""Data Towers - Data storage, analysis, and insights."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class DataTowers:
    """Centralized data storage and analysis for GoodBoy.AI."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "goodboy_data.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT,
                assistant_response TEXT,
                agents_used TEXT,
                confidence REAL,
                response_time_ms INTEGER,
                success INTEGER DEFAULT 1
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metadata TEXT
            )
        """)
        
        # User data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_interaction(
        self,
        user_message: str,
        assistant_response: str,
        agents_used: List[str],
        confidence: float,
        response_time_ms: int,
        success: bool = True
    ):
        """Store an interaction record."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions 
            (timestamp, user_message, assistant_response, agents_used, confidence, response_time_ms, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_message,
            assistant_response,
            json.dumps(agents_used),
            confidence,
            response_time_ms,
            1 if success else 0
        ))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self, days: int = 7) -> Dict:
        """Get analytics for the past N days."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total interactions
        cursor.execute(
            "SELECT COUNT(*) FROM interactions WHERE timestamp > ?", 
            (cutoff,)
        )
        total = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute(
            "SELECT AVG(success) FROM interactions WHERE timestamp > ?",
            (cutoff,)
        )
        success_rate = cursor.fetchone()[0] or 0
        
        # Average confidence
        cursor.execute(
            "SELECT AVG(confidence) FROM interactions WHERE timestamp > ?",
            (cutoff,)
        )
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Average response time
        cursor.execute(
            "SELECT AVG(response_time_ms) FROM interactions WHERE timestamp > ?",
            (cutoff,)
        )
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Agent usage
        cursor.execute(
            "SELECT agents_used FROM interactions WHERE timestamp > ?",
            (cutoff,)
        )
        agent_counts = defaultdict(int)
        for row in cursor.fetchall():
            agents = json.loads(row[0]) if row[0] else []
            for agent in agents:
                agent_counts[agent] += 1
        
        conn.close()
        
        return {
            "period_days": days,
            "total_interactions": total,
            "success_rate": round(success_rate * 100, 1),
            "avg_confidence": round(avg_confidence, 2),
            "avg_response_time_ms": round(avg_response_time, 0),
            "agent_usage": dict(agent_counts),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """Get daily statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count,
                AVG(confidence) as avg_conf,
                AVG(response_time_ms) as avg_time
            FROM interactions 
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (cutoff,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "date": row[0],
                "interactions": row[1],
                "avg_confidence": round(row[2], 2) if row[2] else 0,
                "avg_response_time_ms": round(row[3], 0) if row[3] else 0
            })
        
        conn.close()
        return results
    
    def store_user_data(self, key: str, value: Any):
        """Store user-specific data."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_data (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_data(self, key: str) -> Optional[Any]:
        """Retrieve user-specific data."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def get_insights(self) -> List[Dict]:
        """Generate insights from data."""
        analytics = self.get_analytics(30)
        daily = self.get_daily_stats(7)
        
        insights = []
        
        # Success rate insight
        if analytics["success_rate"] >= 95:
            insights.append({
                "type": "positive",
                "title": "High Success Rate",
                "message": f"GoodBoy.AI has a {analytics['success_rate']}% success rate over the past month."
            })
        elif analytics["success_rate"] < 80:
            insights.append({
                "type": "warning",
                "title": "Success Rate Needs Attention",
                "message": f"Success rate is {analytics['success_rate']}%. Consider reviewing failed interactions."
            })
        
        # Usage trend
        if len(daily) >= 2:
            recent = sum(d["interactions"] for d in daily[:3])
            older = sum(d["interactions"] for d in daily[3:6]) if len(daily) > 3 else recent
            if older > 0:
                change = ((recent - older) / older) * 100
                if change > 20:
                    insights.append({
                        "type": "info",
                        "title": "Usage Increasing",
                        "message": f"Usage has increased by {change:.0f}% compared to last week."
                    })
        
        # Agent performance
        usage = analytics.get("agent_usage", {})
        if usage:
            most_used = max(usage.items(), key=lambda x: x[1])
            insights.append({
                "type": "info",
                "title": "Most Active Agent",
                "message": f"{most_used[0]} handled {most_used[1]} requests this month."
            })
        
        return insights
    
    def export_data(self, export_path: Path) -> bool:
        """Export all data to JSON."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Export interactions
            cursor.execute("SELECT * FROM interactions ORDER BY timestamp DESC LIMIT 10000")
            interactions = cursor.fetchall()
            
            # Export user data
            cursor.execute("SELECT * FROM user_data")
            user_data = cursor.fetchall()
            
            conn.close()
            
            export = {
                "exported_at": datetime.now().isoformat(),
                "interactions": [
                    {
                        "id": r[0],
                        "timestamp": r[1],
                        "user_message": r[2],
                        "assistant_response": r[3],
                        "agents_used": r[4],
                        "confidence": r[5],
                        "response_time_ms": r[6],
                        "success": r[7]
                    }
                    for r in interactions
                ],
                "user_data": [
                    {"key": r[1], "value": r[2], "updated_at": r[3]}
                    for r in user_data
                ]
            }
            
            with open(export_path, 'w') as f:
                json.dump(export, f, indent=2)
            
            return True
            
        except Exception:
            return False
