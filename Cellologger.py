import streamlit as st
import pandas as pd
import os
from datetime import datetime

def process_csv(file):
    # Read data from the CSV file, skipping the first 9 rows
    data = pd.read_csv(file, skiprows=9, header=0, encoding='utf-8')
    
    # Rename columns based on the number of columns present
    if len(data.columns) == 2:
        data.columns = ["Datatime", "Value"]
    elif len(data.columns) >= 3:
        data.columns = ["Datatime", "Value", "Unit"] + [f"Extra_{i}" for i in range(len(data.columns) - 3)]
    else:
        st.error(f"File {file.name} has an unexpected number of columns: {len(data.columns)}")
        return None
    
    # Extract the last six digits from the file name (or use the whole name if it's shorter)
    file_name = os.path.splitext(file.name)[0]
    last_six_digits = file_name[-6:] if len(file_name) > 6 else file_name
    
    # Rename the Value column to the last six digits (or full name) of the file
    data = data.rename(columns={"Value": last_six_digits})
    
    # Convert Datatime to datetime, trying different formats
    date_formats = ['%d/%m/%y', '%d/%m/%Y', '%d/%m/%y %H:%M', '%d/%m/%Y %H:%M']
    for date_format in date_formats:
        try:
            data['Datatime'] = pd.to_datetime(data['Datatime'], format=date_format)
            break
        except ValueError:
            continue
    else:
        st.error(f"Unable to parse dates in file {file.name}. Please check the date format.")
        return None
    
    # Select only Datatime and the renamed Value column
    data = data[['Datatime', last_six_digits]]
    
    return data

def main():
    st.title('Cello Logger Data Processor')

    # File uploader
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')

    if uploaded_files:
        # Process each CSV file
        data_list = []
        for file in uploaded_files:
            data = process_csv(file)
            if data is not None:
                data_list.append(data)

        if data_list:
            # Create a unique set of timestamps
            all_timestamps = sorted(set(pd.concat([df['Datatime'] for df in data_list])))

            # Create an empty dataframe with all timestamps
            combined_data = pd.DataFrame({'Datatime': all_timestamps})

            # Merge each processed CSV data into the combined data
            for df in data_list:
                combined_data = pd.merge(combined_data, df, on='Datatime', how='left')

            # Sort by Datatime
            combined_data = combined_data.sort_values('Datatime')

            # Fill NA values with empty string
            combined_data = combined_data.fillna('')

            # Reformat Datatime to original format
            combined_data['Datatime'] = combined_data['Datatime'].dt.strftime('%d/%m/%Y %H:%M')

            # Display the combined data
            st.write(combined_data)

            # Option to download the combined data
            csv = combined_data.to_csv(index=False)
            st.download_button(
                label="Download combined data as CSV",
                data=csv,
                file_name="combined_data.csv",
                mime="text/csv",
            )

            # Print column names to verify
            st.write("Column names:", combined_data.columns.tolist())
        else:
            st.warning("No valid data found in the uploaded files.")

if __name__ == "__main__":
    main()
