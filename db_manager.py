#!/usr/bin/env python3
"""
Interactive Database Manager for Smart Journal
"""

import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='instance/smart_journal.db'):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at: {self.db_path}")
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            print("🔌 Database connection closed")
    
    def get_tables(self):
        """Get list of all tables"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in cursor.fetchall()]
    
    def show_table_info(self, table_name):
        """Show detailed information about a table"""
        cursor = self.conn.cursor()
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n🏗️  Table: {table_name}")
        print("=" * 60)
        print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Primary Key':<12} {'Default':<15}")
        print("-" * 80)
        
        for col in columns:
            cid, name, type_, notnull, dflt_value, pk = col
            nullable = "NO" if notnull else "YES"
            primary = "YES" if pk else "NO"
            default = str(dflt_value) if dflt_value else "NULL"
            print(f"{name:<20} {type_:<15} {nullable:<10} {primary:<12} {default:<15}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total rows: {count}")
    
    def show_table_data(self, table_name, limit=10):
        """Show data from a table"""
        cursor = self.conn.cursor()
        
        try:
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            
            if total_count == 0:
                print(f"📭 Table '{table_name}' is empty")
                return
            
            print(f"\n📊 Data from '{table_name}' (showing {min(limit, total_count)} of {total_count} records):")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Print headers
            header = " | ".join(f"{col:<20}" for col in columns)
            print("-" * len(header))
            print(header)
            print("-" * len(header))
            
            # Print data
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL".ljust(20))
                    elif isinstance(value, str) and len(value) > 18:
                        formatted_row.append(f"{value[:17]}...".ljust(20))
                    else:
                        formatted_row.append(str(value).ljust(20))
                print(" | ".join(formatted_row))
                
        except Exception as e:
            print(f"❌ Error reading table data: {e}")
    
    def run_custom_query(self, query):
        """Run a custom SQL query"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                # Fetch and display results
                rows = cursor.fetchall()
                if rows:
                    # Get column names
                    columns = [description[0] for description in cursor.description]
                    
                    # Print headers
                    header = " | ".join(f"{col:<20}" for col in columns)
                    print("-" * len(header))
                    print(header)
                    print("-" * len(header))
                    
                    # Print data
                    for row in rows:
                        formatted_row = []
                        for value in row:
                            if value is None:
                                formatted_row.append("NULL".ljust(20))
                            elif isinstance(value, str) and len(value) > 18:
                                formatted_row.append(f"{value[:17]}...".ljust(20))
                            else:
                                formatted_row.append(str(value).ljust(20))
                        print(" | ".join(formatted_row))
                    
                    print(f"\n📊 Total results: {len(rows)}")
                else:
                    print("📭 No results found")
            else:
                # Non-SELECT query
                self.conn.commit()
                print(f"✅ Query executed successfully. Rows affected: {cursor.rowcount}")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    def show_database_stats(self):
        """Show database statistics"""
        cursor = self.conn.cursor()
        
        print("\n📈 Database Statistics")
        print("=" * 40)
        
        tables = self.get_tables()
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<20}: {count:>5} rows")
        
        # Show some useful metrics
        print("\n💡 Quick Insights:")
        
        # User activity
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM journal_entry")
        active_users = cursor.fetchone()[0]
        print(f"Active users: {active_users}")
        
        # Recent activity
        cursor.execute("SELECT COUNT(*) FROM journal_entry WHERE created_at >= date('now', '-7 days')")
        recent_entries = cursor.fetchone()[0]
        print(f"Entries this week: {recent_entries}")
        
        # Mood trends
        cursor.execute("SELECT mood_before, COUNT(*) FROM mood_entry WHERE mood_before IS NOT NULL GROUP BY mood_before ORDER BY COUNT(*) DESC LIMIT 3")
        mood_counts = cursor.fetchall()
        if mood_counts:
            print("Top moods:", ", ".join([f"{mood}({count})" for mood, count in mood_counts]))

def main():
    """Main interactive function"""
    print("🔧 Smart Journal Database Manager")
    print("=" * 40)
    
    db_manager = DatabaseManager()
    
    if not db_manager.connect():
        return
    
    try:
        while True:
            print("\n" + "="*50)
            print("📋 Available Options:")
            print("1. Show all tables")
            print("2. Show table schema")
            print("3. Show table data")
            print("4. Run custom query")
            print("5. Show database stats")
            print("6. Exit")
            print("="*50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                tables = db_manager.get_tables()
                print(f"\n📋 Tables in database ({len(tables)}):")
                for i, table in enumerate(tables, 1):
                    print(f"  {i}. {table}")
            
            elif choice == '2':
                tables = db_manager.get_tables()
                if tables:
                    print(f"\nAvailable tables: {', '.join(tables)}")
                    table_name = input("Enter table name: ").strip()
                    if table_name in tables:
                        db_manager.show_table_info(table_name)
                    else:
                        print("❌ Invalid table name")
                else:
                    print("❌ No tables found")
            
            elif choice == '3':
                tables = db_manager.get_tables()
                if tables:
                    print(f"\nAvailable tables: {', '.join(tables)}")
                    table_name = input("Enter table name: ").strip()
                    if table_name in tables:
                        limit_input = input("Enter row limit (default 10): ").strip()
                        limit = int(limit_input) if limit_input.isdigit() else 10
                        db_manager.show_table_data(table_name, limit)
                    else:
                        print("❌ Invalid table name")
                else:
                    print("❌ No tables found")
            
            elif choice == '4':
                query = input("Enter SQL query: ").strip()
                if query:
                    db_manager.run_custom_query(query)
                else:
                    print("❌ Query cannot be empty")
            
            elif choice == '5':
                db_manager.show_database_stats()
            
            elif choice == '6':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    main()
