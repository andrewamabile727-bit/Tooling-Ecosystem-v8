import streamlit as st
import pandas as pd
import hashlib

# --- 1. TOOLING ENGINE (THE BRAIN) - DYNAMIC SHA-256 ---
def sha256_hash_dynamic(string_in, digits=4):
    """Generates a unique numerical code of specified length using SHA-256 for superior entropy"""
    # Removes dashes and spaces, making it uppercase for a perfect match
    clean_str = str(string_in).upper().replace("-", "").replace(" ", "")
    
    # Process through Cryptographic SHA-256 hash
    hash_hex = hashlib.sha256(clean_str.encode('utf-8')).hexdigest()
    
    # Convert hex to integer
    hash_int = int(hash_hex, 16)
    
    # Dynamically set modulo and format leading zeros based on requested digits
    modulo = 10 ** digits
    return f"{hash_int % modulo:0{digits}d}"

# --- 2. APP CONFIGURATION & CATEGORY DATA ---
st.set_page_config(page_title="Molds & Fixtures Ecosystem", layout="wide")

# Each category now explicitly defines its required digit output length
category_data = {
    "Mold Component P/N": {
        "prefix": "Dynamic", # Prefix is extracted dynamically in logic below
        "title": "Mold Component P/N Generator",
        "example": "X-N-04-00-A1-01",
        "digits": 5
    },
    "Molds-Cladding-Master-Assy": {
        "prefix": "Z0",
        "title": "Molds-Cladding-Master-Assy P/N Code Generator",
        "example": "Z0-Z10000-Z15996-Z14924-Z17707",
        "digits": 4
    },
    "Molds-Cladding": {
        "prefix": "Z1", 
        "title": "Molds-Cladding P/N Code Generator",
        "example": "Z1-01.20D-1B2-C1B-01",
        "digits": 4
    },
    "Molds-Countertop": {
        "prefix": "Z2", 
        "title": "Molds-Countertop P/N Code Generator",
        "example": "Z2-01.20D1-A0A0A0-B-01",
        "digits": 4
    },
    "Mfg. Fixtures & Jigs": {
        "prefix": "Y1", 
        "title": "Mfg. Fixtures & Jigs P/N Code Generator",
        "example": "Y1-00.00A1-A0A0A0-D-01",
        "digits": 4
    }
}

# Sidebar Navigation
category = st.sidebar.selectbox("Select Tooling Category", list(category_data.keys()))
prefix = category_data[category]["prefix"]
app_title = category_data[category]["title"]
example_code = category_data[category]["example"]
digit_length = category_data[category]["digits"]

# Dynamic Title based on selection
st.title(f"🗜️ {app_title}")
st.markdown("### Production Tooling & Fixture Master Control")

# Show the team the expected format for safety
st.info(f"**Format Guide:** The expected MasterCode input format for this category looks like: `{example_code}`")

# --- 3. DATA PROCESSING ---
uploaded_file = st.file_uploader(f"Upload CSV for {category}", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Safety Check: Ensure the MasterCode column exists
    if "MasterCode" not in df.columns:
        st.error("❌ Error: Your CSV file is missing the 'MasterCode' column!")
        st.info("Please ensure the first row of your column is exactly 'MasterCode'.")
    else:
        # Dynamic button label based on category
        btn_label = "🚀 Generate Mold Component Codes" if category == "Mold Component P/N" else f"🚀 Generate {prefix} Codes"
        
        if st.button(btn_label):
            # Apply different prefix logic based on category selection
            if category == "Mold Component P/N":
                # Extracts the first 2 characters (ignoring dashes) for the prefix + 5 digit hash
                df['Generated P/N'] = df['MasterCode'].apply(
                    lambda x: f"{str(x).upper().replace('-', '').replace(' ', '')[:2]}-{sha256_hash_dynamic(x, digit_length)}"
                )
            else:
                # Standard fixed prefix + 4 digit hash
                df['Generated P/N'] = df['MasterCode'].apply(
                    lambda x: f"{prefix}-{sha256_hash_dynamic(x, digit_length)}"
                )
            
            # Twin Check (Duplication monitor)
            duplicates = df.duplicated(subset=['Generated P/N']).sum()
            
            st.success(f"✅ Part Numbers Generated Successfully!")
            
            if duplicates > 0:
                st.warning(f"⚠️ Warning: Found {duplicates} duplicate IDs in this list.")
                # Show the user which ones duplicated so they know
                duped_df = df[df.duplicated(subset=['Generated P/N'], keep=False)].sort_values('Generated P/N')
                st.write("**Duplicated Entries:**")
                st.dataframe(duped_df)
            else:
                st.info("✨ Clean Batch: Zero duplicates detected.")
            
            st.dataframe(df)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download P/N List",
                data=csv,
                file_name=f"{category.replace(' ', '_')}_PN_Export.csv",
                mime='text/csv'
            )