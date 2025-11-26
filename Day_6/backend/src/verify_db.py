"""Verification script for SQLite database setup"""

from database import FraudDatabase
import os

db = FraudDatabase()
print("✅ Database module imported successfully")
print(f"📁 Database file exists: {os.path.exists('fraud_cases.db')}")
print(f"📊 Total cases: {len(db.get_all_fraud_cases())}")

stats = db.get_statistics()
print(f"📈 Statistics:")
print(f"   Pending: {stats.get('pending', 0)}")
print(f"   Confirmed Safe: {stats.get('confirmed_safe', 0)}")
print(f"   Confirmed Fraud: {stats.get('confirmed_fraud', 0)}")
print()
print("✅ SQLite Database Setup Complete!")
print("🚀 Ready to run the fraud alert agent")
