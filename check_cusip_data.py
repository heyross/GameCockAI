#!/usr/bin/env python3
"""Check CUSIP data availability in database"""

import sqlite3

def check_cusip_data():
    conn = sqlite3.connect('gamecock.db')
    cursor = conn.cursor()
    
    # Check Form 13F CUSIP data
    print("Checking Form 13F CUSIP data...")
    cursor.execute("SELECT COUNT(*) FROM form13f_info_tables WHERE cusip IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"Form 13F records with CUSIP: {count}")
    
    if count > 0:
        # Show sample CUSIPs
        cursor.execute("SELECT DISTINCT cusip, nameofissuer FROM form13f_info_tables WHERE cusip IS NOT NULL LIMIT 5")
        samples = cursor.fetchall()
        print("\nSample Form 13F CUSIPs:")
        for sample in samples:
            print(f"  CUSIP: {sample[0]}, Issuer: {sample[1]}")
    
    # Check N-MFP CUSIP data
    print("\nChecking N-MFP CUSIP data...")
    cursor.execute("SELECT COUNT(*) FROM nmfp_sch_portfolio_securities WHERE cusip_number IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"N-MFP records with CUSIP: {count}")
    
    if count > 0:
        # Show sample CUSIPs
        cursor.execute("SELECT DISTINCT cusip_number, name_of_issuer FROM nmfp_sch_portfolio_securities WHERE cusip_number IS NOT NULL LIMIT 5")
        samples = cursor.fetchall()
        print("\nSample N-MFP CUSIPs:")
        for sample in samples:
            print(f"  CUSIP: {sample[0]}, Issuer: {sample[1]}")
    
    conn.close()

if __name__ == "__main__":
    check_cusip_data()
