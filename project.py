import streamlit as st
import pandas as pd
import os

col1, col2 = st.columns([1, 5])
with col1:
    st.image("WhatsApp Image 2025-06-07 at 10.39.20 PM.jpeg", width=80)  # Adjust width as needed
with col2:
    st.markdown("<h1 style='text-align: center;'>MSS</h1>", unsafe_allow_html=True)

DATA_FILE = "data.xlsx"
COLUMNS = ["date", "name", "item", "kaal X No", "Type", "Total weight", "income1", "income2", "income3", "income"]

# Load or create the database file with your columns
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
    # Ensure all columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS]  # Reorder columns
else:
    df = pd.DataFrame(columns=COLUMNS)
    df.to_excel(DATA_FILE, index=False)

# Show existing data
st.subheader("📄 Previous Entries")
st.dataframe(df)

# --- Edit or Delete Existing Row ---
st.subheader("✏️ Edit or Delete Existing Row")
if not df.empty:
    row_idx = st.selectbox("Select row to edit/delete (by index):", df.index, key="row_idx")
    if st.button("Edit Selected Row"):
        st.session_state.edit_mode = True
        st.session_state.edit_row_idx = row_idx

    if getattr(st.session_state, "edit_mode", False) and getattr(st.session_state, "edit_row_idx", None) == row_idx:
        edit_data = {}
        st.write("Edit the values below and click 'Save Changes' or click 'Delete Row' to remove it.")
        for col in df.columns:
            edit_data[col] = st.text_input(f"{col}", value=str(df.loc[row_idx, col]), key=f"edit_{col}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Changes"):
                for col in df.columns:
                    df.at[row_idx, col] = edit_data[col]
                df.to_excel(DATA_FILE, index=False)
                st.success("Row updated successfully!")
                st.session_state.edit_mode = False
                st.dataframe(df)
        with col2:
            if st.button("Delete Row"):
                df = df.drop(index=row_idx).reset_index(drop=True)
                df.to_excel(DATA_FILE, index=False)
                st.success("Row deleted successfully!")
                st.session_state.edit_mode = False
                st.dataframe(df)

    # --- Delete Multiple Rows ---
    st.markdown("#### 🗑️ Delete Multiple Rows")
    if not df.empty:
        multi_rows = st.multiselect("Select rows to delete (by index):", df.index, key="multi_delete")
        if st.button("Delete Selected Rows"):
            if multi_rows:
                df = df.drop(index=multi_rows).reset_index(drop=True)
                df.to_excel(DATA_FILE, index=False)
                st.success(f"Deleted rows: {multi_rows}")
                st.dataframe(df)
            else:
                st.warning("No rows selected for deletion.")
    else:
        st.info("No data available to delete.")

# --- Import Old Excel Data ---
st.subheader("📥 Import Old Excel Data")
uploaded_file = st.file_uploader("Upload an Excel or CSV file to add its data:", type=["xlsx", "csv"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            old_df = pd.read_csv(uploaded_file)
        else:
            old_df = pd.read_excel(uploaded_file)
        # Only keep columns that match your schema
        old_df = old_df[[col for col in COLUMNS if col in old_df.columns]]
        # Add missing columns as empty
        for col in COLUMNS:
            if col not in old_df.columns:
                old_df[col] = ""
        old_df = old_df[COLUMNS]
        # Append to main df
        df = pd.concat([df, old_df], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Old data imported successfully!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error importing file: {e}")

# --- Manual input based on columns ---
st.subheader("📝 Add New Row Manually")
if len(df.columns) > 0:
    # Clear fields if flag is set
    if st.session_state.get("clear_fields", False):
        for col in df.columns:
            st.session_state[f"add_{col}"] = ""
        st.session_state["clear_fields"] = False

    input_data = {}
    for col in df.columns:
        # Initialize session state for each input if not already set
        if f"add_{col}" not in st.session_state:
            st.session_state[f"add_{col}"] = ""
        input_data[col] = st.text_input(f"Enter value for '{col}'", key=f"add_{col}")
    if st.button("Submit"):
        df = pd.concat([df, pd.DataFrame([input_data])], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Row added successfully!")
        # Set flag to clear fields and rerun
        st.session_state["clear_fields"] = True
        st.rerun()
    st.dataframe(df)
