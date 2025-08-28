#!/usr/bin/env python3
"""
Simple SQLite Database Viewer for Smart Journal
"""

import sqlite3
import os
from datetime import datetime

def connect_db():
    """Connect to the SQLite database"""
    db_path = 'instance/smart_journal.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def show_tables(conn):
    """Show all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📋 Tables in database ({len(tables)}):")
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table[0]}")
    
    return [table[0] for table in tables]

def show_table_schema(conn, table_name):
    """Show the schema of a specific table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"\n🏗️  Schema for table '{table_name}':")
    print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Primary Key':<12}")
    print("-" * 60)
    
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        nullable = "NO" if notnull else "YES"
        primary = "YES" if pk else "NO"
        print(f"{name:<20} {type_:<15} {nullable:<10} {primary:<12}")

def show_table_data(conn, table_name, limit=5):
    """Show sample data from a table"""
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 Data in table '{table_name}' (showing {min(limit, total_count)} of {total_count} records):")
        
        if total_count == 0:
            print("  (No data)")
            return
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Print headers
        header = " | ".join(f"{col:<15}" for col in columns)
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        
        # Print data
        for row in rows:
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append("NULL".ljust(15))
                elif isinstance(value, datetime):
                    formatted_row.append(str(value).ljust(15))
                else:
                    formatted_row.append(str(value)[:14].ljust(15))
            print(" | ".join(formatted_row))
            
    except Exception as e:
        print(f"❌ Error reading table data: {e}")

def main():
    """Main function"""
    print("🔍 Smart Journal Database Viewer")
    print("=" * 40)
    
    # Connect to database
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Show tables
        tables = show_tables(conn)
        
        if not tables:
            print("❌ No tables found in database")
            return
        
        # Show schema and sample data for each table
        for table in tables:
            show_table_schema(conn, table)
            show_table_data(conn, table)
            print("\n" + "="*60 + "\n")
        
        # Show some useful queries
        print("💡 Useful Database Queries:")
        print("1. Total users:", end=" ")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user")
        print(cursor.fetchone()[0])
        
        print("2. Total journal entries:", end=" ")
        cursor.execute("SELECT COUNT(*) FROM journal_entry")
        print(cursor.fetchone()[0])
        
        print("3. Total mood entries:", end=" ")
        cursor.execute("SELECT COUNT(*) FROM mood_entry")
        print(cursor.fetchone()[0])
        
        print("4. Latest journal entry:", end=" ")
        cursor.execute("SELECT entry_date FROM journal_entry ORDER BY entry_date DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(result[0])
        else:
            print("None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        conn.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
