import pandas as pd
import time
import random
import traceback
import os

from src.handle_scraping import search_duckduckgo
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from datetime import datetime

def choose_default_workers(io_bound=True):
    cores = os.cpu_count() or 1
    if not io_bound:
        return cores  # CPU bound: ~ cores
    # I/O bound: start with cores * 10, capped
    return min(200, max(5, cores-1))

def search_with_cache(name: str, cache: dict, filter: list) -> tuple:
    """
    Search name with caching.
    
    Returns:
        tuple: (bool, bool, list, int) - (if match found, if search was blocked, list of matched keywords, number of results)
    """
    if name in cache:
        return cache[name]

    found, blocked, matches, result_count = search_duckduckgo(name, filter)
    if not blocked:  # Only cache results if we weren't blocked
        cache[name] = (found, blocked, matches, result_count)
    # Reduced delay for concurrent requests
    time.sleep(random.uniform(0.5, 1))
    return found, blocked, matches, result_count


def read_excel(input_file: str) -> pd.DataFrame:
    """Read an Excel file into a pandas DataFrame.

    Args:
        input_file: Path to the input Excel file.

    Returns:
        pandas.DataFrame
    """
    print("📖 Reading Excel file...")
    return pd.read_excel(input_file)


def write_excel(results: list, output_dir: str) -> str:
    """Write results to Excel file"""
    try:
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Adverse_Events_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\n📝 Saving results...")
        print(f"   Output directory: {output_dir}")
        print(f"   Directory exists: {os.path.exists(output_dir)}")
        print(f"   Full path: {filepath}")
        print(f"   Number of results: {len(results)}")
        
        df.to_excel(filepath, index=False)
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ File saved successfully!")
            print(f"   File: {filename}")
            print(f"   Size: {file_size} bytes")
        else:
            print(f"❌ ERROR: File was not created at {filepath}")
        
        return filepath
    except Exception as e:
        print(f"❌ Error writing Excel file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def process_row(row: dict, search_cache: dict, filter: list) -> Dict:
    """Process a single row (dict) and return a result dict.

    This function is intentionally pure with respect to external counters
    (it does not update shared stats). Caller should aggregate stats.
    """
    result = {"ID": row.get("ID"), "Name": row.get("Name"), "Status": "", "Keyword": "", "Results": 0}
    name = row.get("Name")

    if pd.notna(name) and str(name).strip():
        name = str(name).strip()
        print(f"Searching: {name}")

        found, blocked, matches, result_count = search_with_cache(name, search_cache, filter)
        result["Results"] = result_count  # Always store the result count

        if blocked:
            result["Status"] = "Empty"  # Set status to Empty when search is blocked
            print(f"  ⚠️ Search for '{name}' was blocked - marking as Empty")
        elif found:
            result["Status"] = "Adverse"
            # join multiple matched keywords with comma
            result["Keyword"] = ", ".join(matches) if matches else ""
        else:
            result["Status"] = "No Adverse"
    else:
        result["Status"] = "Empty Name"

    return result


def run(input_file: str, output_dir: str, filter: list, job_id: str = None, processing_jobs: dict = None) -> None:
    """High-level runner: read input, process rows (parallel), and write output.

    Args:
        input_file: Path to input Excel file.
        output_dir: Directory where output file will be written.
        filter: List of filter words/patterns to pass to the scraper.
        job_id: Optional job ID for progress tracking.
        processing_jobs: Optional dict to update progress.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        start_time = datetime.now()

        df = read_excel(input_file)

        # Verify required columns
        required_columns = ["CIF", "Name", "Status"]
        if not all(col in df.columns for col in required_columns):
            print(f"❌ Error: Excel file must contain columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            raise Exception(f"Missing required {required_columns} columns in input Excel file.")

        total_rows = len(df)
        print(f"✅ Found {total_rows} rows to process\n")

        # Prepare cache and stats
        search_cache: dict = {}
        stats = {"found": 0, "not_found": 0, "empty": 0, "blocked": 0}

        # Run processing in parallel
        print("🔍 Starting parallel searches...\n")
        rows = df.to_dict("records")
        
        # Update progress tracking if job_id provided
        if job_id and processing_jobs:
            processing_jobs[job_id]['total_rows'] = total_rows
        
        with ThreadPoolExecutor(max_workers=choose_default_workers()) as executor:
            # submit with needed extra args by mapping tuples
            futures = [executor.submit(process_row, row, search_cache, filter) for row in rows]
            results = []
            # simple processed counter printed as each job completes
            for f in as_completed(futures):
                r = f.result()
                results.append(r)
                processed_count = len(results)
                print(f"Count: {processed_count}/{total_rows}")
                
                # Update progress percentage if tracking enabled
                if job_id and processing_jobs:
                    progress_pct = int((processed_count / total_rows) * 100)
                    processing_jobs[job_id]['processed_rows'] = processed_count
                    processing_jobs[job_id]['progress'] = progress_pct

        # Aggregate stats
        for r in results:
            status = r.get("Status")
            if status == "Adverse":
                stats["found"] += 1
            elif status == "No Adverse":
                stats["not_found"] += 1
            elif status == "Empty":  # Separate count for blocked searches
                stats["blocked"] = stats.get("blocked", 0) + 1
            else:
                stats["empty"] += 1

        # Write results
        write_excel(results, output_dir)

        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print summary
        print("\n" + "=" * 50)
        print("✅ PROCESSING COMPLETE!")
        print("=" * 50)
        print(f"Total processed: {total_rows}")
        print(f"Adverse: {stats['found']}")
        print(f"Not Adverse: {stats['not_found']}")
        print(f"Empty/Invalid: {stats['empty']}")
        print(f"Blocked searches: {stats['blocked']}")
        print(f"\nResults saved to: {output_dir}")
        print(f"Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print("=" * 50)

    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        print("   Make sure the file exists in the same folder as this script.")
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        traceback.print_exc()

