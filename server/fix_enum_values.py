#!/usr/bin/env python3
"""Fix enum values in database"""

from app.core.database import SessionLocal
from sqlalchemy import text

def main():
    db = SessionLocal()
    try:
        # Update all lowercase enum values to uppercase
        result1 = db.execute(text('UPDATE agent_decisions SET decision_type = "REORDER" WHERE decision_type = "reorder"'))
        result2 = db.execute(text('UPDATE agent_decisions SET decision_type = "ALERT" WHERE decision_type = "alert"'))
        result3 = db.execute(text('UPDATE agent_decisions SET decision_type = "VENDOR_RISK" WHERE decision_type = "vendor_risk"'))
        result4 = db.execute(text('UPDATE agent_decisions SET decision_type = "ANOMALY" WHERE decision_type = "anomaly"'))
        
        db.commit()
        
        total_updated = result1.rowcount + result2.rowcount + result3.rowcount + result4.rowcount
        print(f'Successfully updated {total_updated} enum values in database')
        
        # Verify the update
        result = db.execute(text('SELECT DISTINCT decision_type FROM agent_decisions'))
        print(f'Current decision types in database: {[row[0] for row in result]}')
        
    except Exception as e:
        print(f'Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()