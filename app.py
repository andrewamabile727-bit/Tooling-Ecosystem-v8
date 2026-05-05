import streamlit as st
import pandas as pd
import io

# --- 1. TOOLING ENGINE (THE BRAIN) ---
def poly_hash_v8(string_in, modulo=10000):
    """Generates a 4-digit unique numerical code (0000-9999)"""
    h = 0
    # Removes dashes and spaces, making it uppercase for a perfect match
    clean_str = str(string_in).upper().replace("-", "").replace(" ", "")
    for char in clean_str:
        h = (h * 53 + ord(char))
    h += len(clean_str)
    return f"{h % modulo:04d}"

# --- 2. APP CONFIGURATION & CATEGORY DATA ---
st.set_page_config(page_title="Molds & Fixtures Ecosystem", layout="wide")

# Map the categories to their prefixes and specific Generator Names
# Z0 added as the primary Master Assembly tier
category_data = {
    "Molds-Cladding-Master-Assy": {
        "prefix": "Z0",
        "title": "Molds-Cladding-Master-Assy P/N Code Generator"
    },
    "Molds-Cladding": {
        "prefix": "Z1", 
        "title": "Molds-Cladding P/N Code Generator"
    },
    "Molds-Countertop": {
        "prefix": "Z2", 
        "title": "Molds-Countertop P/N Code Generator"
    },
    "Mfg. Fixtures & Jigs": {
        "prefix": "Y1", 
        "title": "Mfg. Fixtures & Jigs P/N Code Generator"
    }
}

# Sidebar Navigation
category = st.sidebar.selectbox("Select Tooling Category", list(category_data.keys()))
prefix = category_data[category]["prefix"]
app_title = category_data[category]["title"]

# Dynamic Title based on selection
st.title(f"🗜️ {app_title}")
st.markdown("### Production Tooling & Fixture Master Control")

# --- 3. DATA PROCESSING ---
uploaded_file = st.file_uploader(f"Upload CSV for {category}", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Safety Check: Ensure the MasterCode column exists
    if "MasterCode" not in df.columns:
        st.error("❌ Error: Your CSV file is missing the 'MasterCode' column!")
        st.info("Please ensure the first row of your column is exactly 'MasterCode'.")
    else:
        if st.button(f"🚀 Generate {prefix} Codes"):
            # Create the ID: Prefix + "-" + 4-digit Hash
            df['Generated P/N'] = df['MasterCode'].apply(lambda x: f"{prefix}-{poly_hash_v8(x)}")
            
            # Twin Check (Duplication monitor)
            duplicates = df.duplicated(subset=['Generated P/N']).sum()
            
            st.success(f"✅ Part Numbers Generated Successfully!")
            
            if duplicates > 0:
                st.warning(f"⚠️ Warning: Found {duplicates} duplicate IDs in this list.")
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