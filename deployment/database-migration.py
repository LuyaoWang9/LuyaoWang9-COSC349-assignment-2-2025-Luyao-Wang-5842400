#!/usr/bin/env python3
import mysql.connector
import os

def migrate_to_rds():
    # Local MySQL (from your Vagrant setup)
    local_db = mysql.connector.connect(
        host="localhost",
        user="expense_user",
        password="password",
        database="expenses"
    )
    
    # RDS MySQL
    rds_db = mysql.connector.connect(
        host=os.getenv('RDS_ENDPOINT'),
        user=os.getenv('RDS_USER'),
        password=os.getenv('RDS_PASSWORD'),
        database="expenses"
    )
    
    local_cursor = local_db.cursor()
    rds_cursor = rds_db.cursor()
    
    # Export data from local
    local_cursor.execute("SELECT name, amount, description FROM bills")
    bills = local_cursor.fetchall()
    
    # Import to RDS
    for bill in bills:
        rds_cursor.execute(
            "INSERT INTO bills (name, amount, description) VALUES (%s, %s, %s)",
            bill
        )
    
    rds_db.commit()
    print(f"Migrated {len(bills)} bills to RDS")
    
    local_cursor.close()
    rds_cursor.close()
    local_db.close()
    rds_db.close()

if __name__ == "__main__":
    migrate_to_rds()