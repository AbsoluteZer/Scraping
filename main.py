from src.handle_excel import run
import os

# File and directory configuration (using os.path for readability)
BASE_DIR = os.path.abspath(os.getcwd())  # Current working directory
INPUT_FILE = "Test_Data.xlsx"  # Input Excel file name
OUTPUT_DIR = os.path.join(BASE_DIR, "tests", "output")  # Output directory for processed files

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

filter =[
    "corruption", "bribery", "embezzlement", "fraud", "money laundering", "laundering funds",
    "kickback", "graft", "misappropriation", "extortion", "embezzled funds", "embezzlement conviction",
    "abuse of office", "abuse of power", "nepotism", "favoritism", "public procurement scandal",
    "procurement fraud", "conflict of interest", "illicit enrichment", "unexplained wealth",
    "asset seizure", "asset forfeiture", "offshore account", "shell company", "nominee director",
    "nominee shareholder", "bearer shares", "trust structure", "secret bank account",
    "suspicious transaction", "structuring", "smurfing", "large cash deposit", "sudden transfer",
    "unexplained transfer", "transaction with Panama", "transaction with Cayman Islands",
    "sanctions evasion", "sanctioned", "OFAC", "EU sanctions", "UN sanctions", "blacklist",
    "terrorism financing", "sanctions breach", "tax evasion", "tax fraud", "tax shelter",
    "tax haven", "offshore leak", "Panama Papers", "Paradise Papers", "Pandora Papers",
    "beneficial owner concealment", "indictment", "arrested", "charged with", "convicted",
    "trial", "investigation", "probe", "probe launched", "plea bargain", "plea deal", "sentence",
    "imprisonment", "scandal", "controversy", "resignation amid", "accused of", "implicated in",
    "alleged bribery", "alleged corruption", "linked to criminal network", "family member charged",
    "spouse charged", "close associate arrested", "cronyism", "relative implicated",
    "business partner arrested", "money mule", "hawala", "trade-based money laundering",
    "false invoicing", "shell bank", "nominee account", "front company", "crypto mixer",
    "crypto tumbler", "leak", "whistleblower", "internal memo", "forensic audit", "investigative report",
    "offshore jurisdiction", "tax haven", "secrecy jurisdiction", "Panama", "British Virgin Islands",
    "Cayman Islands", "Jersey", "Guernsey", "Luxembourg", "Switzerland"
] # Add your filter word here

if __name__ == "__main__":
    # Process the Excel file
    input_file = os.path.join(BASE_DIR, "tests", INPUT_FILE)
    output_dir = OUTPUT_DIR
    run(input_file, output_dir, filter)