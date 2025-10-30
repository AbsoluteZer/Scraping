import pandas as pd
from src.scraping.scraping import search_duckduckgo
import time
import random
import traceback
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from datetime import datetime

def search_with_cache(name: str, cache: dict,filter:list) -> bool:
    """Search name with caching"""
    if name in cache:
        return cache[name]
    
    found = search_duckduckgo(name,filter)
    cache[name] = found
    time.sleep(random.uniform(0.5, 1))  # Reduced delay for concurrent requests
    return found

def run(input_file: str, output_dir: str, filter: list, max_workers: int = 5) -> None:
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file
    """
    # Create unique output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join("output_",output_file, f"{input_name}_{timestamp}.xlsx")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        start_time = datetime.now()
        print("📖 Reading Excel file...")
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Verify columns exist
        required_columns = ['ID', 'Name', 'Status']
        if not all(col in df.columns for col in required_columns):
            print(f"❌ Error: Excel file must contain columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            return
        
        total_rows = len(df)
        print(f"✅ Found {total_rows} rows to process\n")
        
        # Initialize counters and cache
        results: List[Dict] = []
        search_cache = {}
        stats = {'found': 0, 'not_found': 0, 'empty': 0}

        def process_row(row) -> Dict:
            result = {'ID': row['ID'], 'Name': row['Name'], 'Status': ''}
            name = row['Name']
            
            if pd.notna(name) and str(name).strip():
                name = str(name).strip()
                print(f"Searching: {name}")
                
                found = search_with_cache(name, search_cache,filter)
                
                if found:
                    result['Status'] = 'Adverse'
                    stats['found'] += 1
                else:
                    result['Status'] = 'No Adverse'
                    stats['not_found'] += 1
            else:
                result['Status'] = 'Empty Name'
                stats['empty'] += 1
            
            return result

        print("🔍 Starting parallel searches...\n")
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(process_row, df.to_dict('records')))
        
        # Save results
        print(f"\n💾 Saving results to {output_file}...")
        results_df = pd.DataFrame(results)
        results_df.to_excel(output_file, index=False)
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        print("\n" + "="*50)
        print("✅ PROCESSING COMPLETE!")
        print("="*50)
        print(f"Total processed: {total_rows}")
        print(f"Adverse: {stats['found']}")
        print(f"Not Adverse: {stats['not_found']}")
        print(f"Empty/Invalid: {stats['empty']}")
        print(f"\nResults saved to: {output_file}")
        print(f"Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print("="*50)
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        print("   Make sure the file exists in the same folder as this script.")
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        traceback.print_exc()

