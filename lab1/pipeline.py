import sys
import pandas as pd

def process_csv_file(input_file, output_file):
    try:
        data_df = pd.read_csv(input_file)
        print(data_df.head(5))
        print(data_df.columns)
        print(f"Total number of columns before: ", data_df.shape[1])

        columns_to_drop = ["Additional Information", "Work Location 1", "Recruitment Contact", "Post Until"]
        data_df.drop(columns=columns_to_drop, inplace=True)
        print(f"Total number of columns after: ", data_df.shape[1])

        data_df.to_csv(output_file, index=False)
        print(f"Data processed and saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_csv_file(input_file, output_file)