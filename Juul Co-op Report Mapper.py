import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -----------------------
# Column Mapping
# -----------------------
COLUMN_MAP = {
    "ID": "internal_id",
    "Retailer": "Retailer",
    "Hub": None,
    "Location Name": None,
    "Premises Name": "site_name",
    "Address": "site_address_1",
    "Post Code": "site_post_code",
    "Date of visit": "date_of_visit",
    "Time of visit": "time_of_visit",
    "Site Code": "site_code",
    "Pass/Fail": "primary_result",
    "Were you able to successfully conduct this audit?": "Were you able to successfully conduct this audit?",
    "Abort Reason": "What was the reason for aborting this audit?",
    "Abort Category": None,
    "Fail Counter": None,
    "Pass After Fail": None,
    "Pass Counter": None,
    "Fail After Pass": None,
    "Please detail why you were unable to conduct this audit:": "Please detail why you were unable to conduct this audit:",
    "How long have you been a mystery shopper? (for this company, or another company)": None,
    "Please enter your age:": "Please enter your age:",
    "Please enter your gender:": "Please enter your gender:",
    "Did you have a beard at the time of the audit?": "Did you have a beard at the time of the audit?",
    "Were you wearing any facial cosmetic products at the time of the audit?": "Were you wearing any facial cosmetic products at the time of the audit?",
    "Did the store sell Juul products?": "Did the store sell Juul products?",
    "Where were the Juul products located in the store?": "Where were the Juul products located in the store?",
    "Did you see any non-Juul branded items that were labelled ''JUUL compatible pods\" in the store during your audit?": "Did you see any non-Juul branded items that were labelled ''JUUL compatible pods\" in the store during your audit?",
    "If so, please give details:": "If so, please give details:",
    "Did you see 'Challenge 25' signage in the store?": "Did you see 'Challenge 25' signage in the store?",
    "Was the signage JUUL branded?": "Was the signage JUUL branded?",
    "Please detail the store employee's name (if wearing a name badge). If there was no name badge please record an accurate description of the employee:": "Please detail the store employee's name (if wearing a name badge). If there was no name badge please record an accurate description of the employee:",
    "What was the gender of the employee who served you?": "What was the gender of the employee who served you?",
    "In which age group was the employee?": "In which age group was the employee?",
    "Were Juul pods available to purchase?": "Were Juul pods available to purchase?",
    "Please detail the product you attempted to purchase:": "Please detail the product you attempted to purchase:",
    "Did the person who served you ask for ID?": "Did the person who served you ask for ID?",
    "Please confirm that you did not present any ID:": "Please confirm that you did not present any ID:",
    "Did the store colleague allow you to purchase the restricted item without providing ID?": "Did the store colleague allow you to purchase the restricted item without providing ID?",
    "At what point were you asked for ID?": "At what point were you asked for ID?",
    "Were you wearing a protective face covering?": None,
    "Did the employee request your ID when you asked to purchase Juul pods with your face covering on or off?": None,
    "Did the employee who served you make eye contact with you?": "Did the employee who served you make eye contact with you?",
    "When was eye contact first made?": "When was eye contact first made?",
    "Were you given a receipt?": "Were you given a receipt?",
    "From the receipt, please enter any visible codes and employee name if any:": "From the receipt, please enter any visible codes and employee name if any:",
    "Did you see any JUUL branded adverts/posters visible from the outside of the store? If yes , please make sure you upload photo": "Did you see any JUUL branded adverts/posters visible from the outside of the store? If yes , please make sure you upload photo",
    "Was there anything about the interaction that you think JUUL should take note of?": "Was there anything about the interaction that you think JUUL should take note of?",
    "If so, please detail the interaction:": "If so, please detail the interaction:",
    "Month": "__KNIME_MONTH__",
    "Year": "__KNIME_YEAR__"
}

def map_value(row, mapping):
    if mapping is None:
        return ""
    if mapping.startswith("__KNIME_"):
        return row.get(mapping, "")
    return str(row.get(mapping, "")).strip()

# -----------------------
# Streamlit UI
# -----------------------
st.title("Juul Co-op Report Mapper")
st.write("""
          1. Export the previous 2 weeks worth of Juul data
          2. Drop the file in the box below – it’ll then give you the output file
          3. Standard bits - Check data vs previous week, remove data already reported, add new data
          4. Done.
          """)

uploaded = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

if uploaded is not None:

    df = pd.read_csv(uploaded, dtype=str).fillna("")

    # Filter CoopTCG rows
    df = df[df["site_code"].astype(str).str.startswith("CoopTCG")]

    # Convert date_of_visit
    df["date_parsed"] = pd.to_datetime(df["date_of_visit"], dayfirst=True, errors="coerce")

    # -----------------------
    # REMOVE audits after most recent Saturday
    # -----------------------
    today = datetime.now().date()
    most_recent_saturday = today - timedelta(days=(today.weekday() - 5) % 7)

    df = df[df["date_parsed"].dt.date <= most_recent_saturday]

    # Retailer rename
    df["Retailer"] = df["client_name"].replace("Juul", "Co-operative Group Limited")

    # Uppercase primary result
    df["primary_result"] = df["primary_result"].astype(str).str.upper()

    # Month/Year like KNIME
    df["__KNIME_MONTH__"] = df["date_parsed"].dt.month.astype("Int64").astype(str).replace("<NA>", "")
    df["__KNIME_YEAR__"] = df["date_parsed"].dt.year.astype("Int64").astype(str).replace("<NA>", "")

    # Sort in chronological order
    df["_sort_date"] = df["date_parsed"]
    df["_sort_time"] = pd.to_datetime(df["time_of_visit"], errors="coerce")
    df = df.sort_values(by=["_sort_date", "_sort_time"])
    df = df.drop(columns=["_sort_date", "_sort_time", "date_parsed"])

    # Build final output
    final = pd.DataFrame({col: df.apply(lambda r: map_value(r, src), axis=1)
                          for col, src in COLUMN_MAP.items()})

    # Convert to CSV in memory
    csv_bytes = final.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    st.success("File processed successfully!")
    
    st.download_button(
        label="Download Juul Co-op Raw Data.csv",
        data=csv_bytes,
        file_name="Juul Co-op Raw Data.csv",
        mime="text/csv"
    )
