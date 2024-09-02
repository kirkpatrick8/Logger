import streamlit as st
import pandas as pd
import os
from datetime import datetime

def generate_unique_name(last_six_digits, existing_names):
    base_name = last_six_digits
    counter = 1
    new_name = base_name
    while new_name in existing_names:
        new_name = f"{base_name}_{counter}"
        counter += 1
    return new_name

def process_csv(file, existing_names):
    # Read data from the CSV file
    data = pd.read_csv(file, encoding='utf-8')
    
    # Ensure that the data frame has "Datatime" and a second column
    if len(data.columns) < 2:
        st.warning(f"The CSV file {file} does not have at least two columns. Skipping this file.")
        return None, None
    
    # Extract the last six digits from the file name
    last_six_digits = os.path.splitext(file)[0][-6:]
    
    # Generate a unique name for this column
    unique_name = generate_unique_name(last_six_digits, existing_names)
    
    # Rename the second column to the unique name
    data.columns = ['Datatime', unique_name]
    
    # Convert Datatime to datetime
    data['Datatime'] = pd.to_datetime(data['Datatime'], format='%d/%m/%Y %H:%M')
    
    return data[['Datatime', unique_name]], unique_name

def main():
    st.title('Prime Logger Data Processor')

    # File uploader
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')

    if uploaded_files:
        existing_names = []
        data_list = []

        for file in uploaded_files:
            result, name = process_csv(file, existing_names)
            if result is not None:
                data_list.append(result)
                existing_names.append(name)

        if data_list:
            # Combine all data frames
            combined_data = pd.concat(data_list, axis=1).drop_duplicates(subset=['Datatime'])

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
                file_name="combined_data_check_for_duplicates.csv",
                mime="text/csv",
            )

            # Print column names to verify
            st.write("Column names:", combined_data.columns.tolist())
        else:
            st.warning("No valid data found in the uploaded files.")

if __name__ == "__main__":
    main()
