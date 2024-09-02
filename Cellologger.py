import streamlit as st
import pandas as pd
import io

def process_csv(file):
    # Read the entire content of the file
    content = file.getvalue().decode('utf-8')
    
    # Split the content into lines
    lines = content.split('\n')
    
    # Find the line with "Time" (which is our header)
    header_index = next(i for i, line in enumerate(lines) if "Time" in line)
    
    # Extract the data part (including the header)
    data_content = '\n'.join(lines[header_index:])
    
    # Read the data into a pandas DataFrame
    df = pd.read_csv(io.StringIO(data_content), parse_dates=['Time'])
    
    # Rename columns
    df = df.rename(columns={'Time': 'Datatime'})
    
    # The second column name might vary, so we'll rename it based on the file name
    value_column = df.columns[1]
    new_column_name = file.name.split('.')[0][-6:]  # Last 6 characters of the filename
    df = df.rename(columns={value_column: new_column_name})
    
    return df[['Datatime', new_column_name]]

def main():
    st.title('Cello Logger Data Processor')

    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')

    if uploaded_files:
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
