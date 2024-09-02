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
    # Read data from the CSV file, skipping the first 9 rows
    data = pd.read_csv(file, skiprows=9, header=0, encoding='utf-8')
    
    # Rename columns based on the number of columns present
    if len(data.columns) == 2:
        data.columns = ["Datatime", "Value"]
    elif len(data.columns) >= 3:
        data.columns = ["Datatime", "Value", "Unit"] + [f"Extra_{i}" for i in range(len(data.columns) - 3)]
    else:
        st.error(f"File {file.name} has an unexpected number of columns: {len(data.columns)}")
        return None, None
    
    # Extract the last six digits from the file name (or use the whole name if it's shorter)
    file_name = os.path.splitext(file.name)[0]
    last_six_digits = file_name[-6:] if len(file_name) > 6 else file_name
    
    # Generate a unique name for this column
    unique_name = generate_unique_name(last_six_digits, existing_names)
    
    # Rename the Value column to the unique name
    data = data.rename(columns={"Value": unique_name})
    
    # Convert Datatime to datetime
    data['Datatime'] = pd.to_datetime(data['Datatime'], format='%d/%m/%Y %H:%M', utc=True)
    
    # Select only Datatime and the renamed Value column
    data = data[['Datatime', unique_name]]
    
    return data, unique_name

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
