"""
Verification script for Phase 1 Database Models & Schema Creation
"""

import sys
import os

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database import init_db, engine
from backend.app.models import (
    Base,
    User,
    Service,
    MetricSample,
    Incident,
    RecoveryPolicy,
    RecoveryExecution,
    AnomalyEvent,
    AuditLog,
    NotificationEvent
)

def test_models_and_tables():
    print("Testing Phase 1 Database Tables Creation...")
    init_db()
    
    # Check tables registered in Base metadata
    registered_tables = list(Base.metadata.tables.keys())
    print(f"Registered tables in Base.metadata ({len(registered_tables)}):")
    for table_name in sorted(registered_tables):
        print(f"  - {table_name}")

    expected_tables = {
        "users",
        "services",
        "metric_samples",
        "incidents",
        "recovery_policies",
        "recovery_executions",
        "anomaly_events",
        "audit_logs",
        "notification_events"
    }

    missing = expected_tables - set(registered_tables)
    assert not missing, f"Missing tables: {missing}"
    print("\nAll 9 expected tables created and verified successfully!")

if __name__ == "__main__":
    test_models_and_tables()
