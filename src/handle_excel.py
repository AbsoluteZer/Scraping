import pandas as pd
import time
import random
import traceback
import os

from src.handle_scraping import search_duckduckgo
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from datetime import datetime

def search_with_cache(name: str, cache: dict, filter: list) -> bool:
    """Search name with caching."""
    if name in cache:
        return cache[name]

    found = search_duckduckgo(name, filter)
    cache[name] = found
    # Reduced delay for concurrent requests
    time.sleep(random.uniform(0.5, 1))
    return found


def read_excel(input_file: str) -> pd.DataFrame:
    """Read an Excel file into a pandas DataFrame.

    Args:
        input_file: Path to the input Excel file.

    Returns:
        pandas.DataFrame
    """
    print("📖 Reading Excel file...")
    return pd.read_excel(input_file)


def write_excel(results: List[Dict], output_file: str) -> None:
    """Write results (list of dict) to an Excel file.

    Args:
        results: List of row dictionaries.
        output_file: Path to the output Excel file.
    """
    print(f"\n💾 Saving results to {output_file}...")
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_file, index=False)


def process_row(row: dict, search_cache: dict, filter: list) -> Dict:
    """Process a single row (dict) and return a result dict.

    This function is intentionally pure with respect to external counters
    (it does not update shared stats). Caller should aggregate stats.
    """
    result = {"ID": row.get("ID"), "Name": row.get("Name"), "Status": ""}
    name = row.get("Name")

    if pd.notna(name) and str(name).strip():
        name = str(name).strip()
        print(f"Searching: {name}")

        found = search_with_cache(name, search_cache, filter)

        if found:
            result["Status"] = "Adverse"
        else:
            result["Status"] = "No Adverse"
    else:
        result["Status"] = "Empty Name"

    return result


def run(input_file: str, output_dir: str, filter: list, max_workers: int = 5) -> None:
    """High-level runner: read input, process rows (parallel), and write output.

    Args:
        input_file: Path to input Excel file.
        output_dir: Directory where output file will be written.
        filter: List of filter words/patterns to pass to the scraper.
        max_workers: Number of threads for concurrent processing.
    """
    # Build unique output filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{input_name}_{timestamp}.xlsx")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        start_time = datetime.now()

        df = read_excel(input_file)

        # Verify required columns
        required_columns = ["ID", "Name", "Status"]
        if not all(col in df.columns for col in required_columns):
            print(f"❌ Error: Excel file must contain columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            return

        total_rows = len(df)
        print(f"✅ Found {total_rows} rows to process\n")

        # Prepare cache and stats
        search_cache: dict = {}
        stats = {"found": 0, "not_found": 0, "empty": 0}

        # Run processing in parallel
        print("🔍 Starting parallel searches...\n")
        rows = df.to_dict("records")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # submit with needed extra args by mapping tuples
            futures = [executor.submit(process_row, row, search_cache, filter) for row in rows]
            results = [f.result() for f in futures]

        # Aggregate stats
        for r in results:
            status = r.get("Status")
            if status == "Adverse":
                stats["found"] += 1
            elif status == "No Adverse":
                stats["not_found"] += 1
            else:
                stats["empty"] += 1

        # Write results
        write_excel(results, output_file)

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
        print(f"\nResults saved to: {output_file}")
        print(f"Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print("=" * 50)

    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        print("   Make sure the file exists in the same folder as this script.")
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        traceback.print_exc()

