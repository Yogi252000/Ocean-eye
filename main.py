import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from pathlib import Path

st.set_page_config(page_title="Vessel PDF Viewer", layout="wide")

# ---------- Setup ----------
SAVE_DIR = "saved_entries"
os.makedirs(SAVE_DIR, exist_ok=True)
CSV_LOG = os.path.join(SAVE_DIR, "metadata_log.csv")
HULL_CSV = "Hull cleaning.csv"

# ---------- Load Hull cleaning.csv ----------
if os.path.exists(HULL_CSV):
    hull_df = pd.read_csv(HULL_CSV, encoding='latin1')
else:
    st.error("Hull cleaning.csv file not found!")
    st.stop()

st.header("Information on Dry Dock, Hull Cleaning , Propeller Polishing & ESD Installation")
tab1, tab2 = st.tabs(["Hull Cleaning Details", "Input Page"])

# ---------- TAB 1: Saved Entries ----------
with tab1:
    if os.path.exists(CSV_LOG):
        st.session_state.entries = pd.read_csv(CSV_LOG, on_bad_lines='skip')
        df = st.session_state.entries.copy()

        top_col1, top_col2 = st.columns([3, 1])

        # Count card (left side)
        with top_col1:
            count = len(df)
            st.markdown(
                f"""
                    <h4 style='margin: 0; color:#333;'>Total Records</h4>
                    <h2 style='margin: 2px 0; color:#007BFF;'>{count}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Multi-select filter dropdown (right side)
        with top_col2:
            vessel_list = sorted(df["Vessel Name"].dropna().unique())
            selected_vessels = st.multiselect("Filter Vessel", vessel_list, default=vessel_list, key="vessel_filter")

        # Apply filter
        if selected_vessels:
            df = df[df["Vessel Name"].isin(selected_vessels)]


        for index, row in df.iterrows():
            with st.container():
                with st.expander(f"{row['Vessel Name']} — {row.get('IMO', '')}"):
                    st.markdown(
                        """
                        <style>
                        .card {
                            background-color: #f9f9f9;
                            padding: 20px;
                            border-radius: 15px;
                            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                            margin-bottom: 20px;
                        }
                        .field-title {
                            font-weight: 600;
                            color: #444;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )


                    cols = st.columns(3)
                    fields = [col for col in df.columns if col != "PDF File"]

                    for i, field in enumerate(fields):
                        col = cols[i % 3]
                        col.markdown(f"<span class='field-title'>{field}:</span> {row[field]}", unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # PDF Display
                    if "PDF File" in row and isinstance(row["PDF File"], str) and row["PDF File"]:
                        file_path = os.path.join(SAVE_DIR, row["PDF File"])
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                            st.markdown("---")
                            st.markdown("📎 **Attached PDF Report:**")
                            st.markdown(
                                f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf"></iframe>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("⚠️ Linked PDF not found.")
    else:
        st.info("ℹ️ No entries saved yet.")

# ---------- TAB 2: Input Form ----------
with tab2:
    col1, col2 = st.columns(2)

    with st.form("entry_form", clear_on_submit=True):
        # ----------- Left Side -----------
        with col1:
            vessel_name = st.text_input("Vessel Name")
            auto_data = None

            if vessel_name:
                match = hull_df[hull_df["Vessel Name"].str.strip().str.lower() == vessel_name.strip().lower()]
                if not match.empty:
                    auto_data = match.iloc[0]
                    for field in ["Vessel Name", "IMO", "Vessel Type", "Doc", "Fleet", "Fleet Manager",
                                  "Technical Superintendent", "Technical Executive"]:
                        st.write(f"**{field}**: {auto_data[field]}")
                else:
                    st.warning("No data found for this vessel.")

            dry_dock = st.selectbox("Is there any Dry Dock carried out last month?", ["Select", "Yes", "No"])
            if dry_dock == "Yes":
                from_date = st.date_input("DD Entry Date", key="dd_from")
                to_date = st.date_input("DD Exit Date", key="dd_to")
                location = st.text_input("Dry Dock Location")

                st.markdown("### Vertical Side Coating")
                paint_type_vertical = st.text_input("Paint Type (Vertical)")
                paint_make_vertical = st.text_input("Paint Make (Vertical Side)")
                surface_prep_vertical = st.text_input("Surface Prep (Vertical Side)")
                application_vertical = st.text_input("Application Method (Vertical Side)")

                st.markdown("### Flat Bottom Coating")
                paint_make_flat = st.text_input("Paint Make (Flat Bottom)")
                paint_type_flat = st.text_input("Paint Type (Flat Bottom)")
                surface_prep_flat = st.text_input("Surface Prep (Flat Bottom)")
                application_flat = st.text_input("Application Method (Flat Bottom)")

                hull_cleaning_dd = st.radio("Hull Cleaning during DD", ["Yes", "No"])
                polishing_dd = st.radio("Propeller Polishing during DD", ["Yes", "No"])
            else:
                from_date = to_date = location = ""
                paint_type_vertical = paint_make_vertical = surface_prep_vertical = application_vertical = ""
                paint_make_flat = paint_type_flat = surface_prep_flat = application_flat = ""
                hull_cleaning_dd = polishing_dd = ""

            uploaded_file = st.file_uploader("Upload Report / Picture (PDF only)", type="pdf")
            remarks = st.text_area("Remarks")

        # ----------- Right Side -----------
        with col2:
            st.subheader("Hull Cleaning")
            hull_cleaning_last_month = st.selectbox("Is there any Hull Cleaning last month?", ["Select", "Yes", "No"])
            hull_cleaning_date = st.date_input("Hull Cleaning Date") if hull_cleaning_last_month == "Yes" else ""

            st.subheader("Propeller Polishing")
            propeller_polishing_last_month = st.selectbox("Is there any Propeller Polishing last month?",
                                                          ["Select", "Yes", "No"])
            propeller_polishing_date = st.date_input(
                "Polishing Date") if propeller_polishing_last_month == "Yes" else ""

            st.subheader("Energy Saving Device")
            energy_saving_devices = st.selectbox("Is there any ESD installation last month?", ["Select", "Yes", "No"])
            if energy_saving_devices == "Yes":
                esd_date = st.date_input("ESD Installation Date")
                tech = st.selectbox("ESD Type", [
                    "Select", "Anti fouling coating", "Propellor Boss Caps Fins PBCF", "Air Lubrication Systems",
                    "Solar Panels", "Energy Saving Propellor Designs", "Wind Turbines", "Flettner Rotor Sails",
                    "Rudder Bulb", "Pre Swirl Stators", "Wake Equalizing Duct", "Hull Coatings",
                    "Mewis Duct", "Soni hull"
                ])
            else:
                esd_date = tech = ""

        # ----------- Save Button -----------
        save_button = st.form_submit_button("💾 Save")

        if save_button:
            if not vessel_name:
                st.error("Vessel Name is required.")
            else:
                entry = {
                    "Vessel Name": vessel_name,
                    "IMO": auto_data['IMO'] if auto_data is not None else "",
                    "Vessel Type": auto_data['Vessel Type'] if auto_data is not None else "",
                    "Doc": auto_data['Doc'] if auto_data is not None else "",
                    "Fleet": auto_data['Fleet'] if auto_data is not None else "",
                    "Fleet Manager": auto_data['Fleet Manager'] if auto_data is not None else "",
                    "Technical Superintendent": auto_data['Technical Superintendent'] if auto_data is not None else "",
                    "Technical Executive": auto_data['Technical Executive'] if auto_data is not None else "",
                    "Dry Dock": dry_dock,
                    "DD Entry Date": from_date,
                    "DD Exit Date": to_date,
                    "Location": location,
                    "Paint Type (Vertical)": paint_type_vertical,
                    "Paint Make (Vertical)": paint_make_vertical,
                    "Surface Prep (Vertical)": surface_prep_vertical,
                    "Application (Vertical)": application_vertical,
                    "Paint Make (Flat)": paint_make_flat,
                    "Paint Type (Flat)": paint_type_flat,
                    "Surface Prep (Flat)": surface_prep_flat,
                    "Application (Flat)": application_flat,
                    "Hull Cleaning during DD": hull_cleaning_dd,
                    "Polishing during DD": polishing_dd,
                    "Hull Cleaning Last Month": hull_cleaning_last_month,
                    "Hull Cleaning Date": hull_cleaning_date,
                    "Propeller Polishing Last Month": propeller_polishing_last_month,
                    "Propeller Polishing Date": propeller_polishing_date,
                    "ESD Installation": energy_saving_devices,
                    "ESD Date": esd_date,
                    "ESD Type": tech,
                    "Remarks": remarks,

                }

                # Save uploaded file
                if uploaded_file:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{timestamp}_{uploaded_file.name}"
                    file_path = os.path.join(SAVE_DIR, filename)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    entry["PDF File"] = filename

                new_df = pd.DataFrame([entry])
                st.session_state.entries = pd.concat([st.session_state.entries, new_df], ignore_index=True)

                # Save to CSV
                if os.path.exists(CSV_LOG):
                    new_df.to_csv(CSV_LOG, mode='a', header=False, index=False)
                else:
                    new_df.to_csv(CSV_LOG, index=False)

                st.success("Entry saved successfully.")