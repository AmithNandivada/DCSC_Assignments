import pandas as pd
import sys
import numpy as np
from sqlalchemy import create_engine, text


def extract_data(input_file):
    return pd.read_csv(input_file)

def transform_data(data):
    # Perform data transformation
    data['Month'], data['Year'] = data['MonthYear'].str.split(' ', expand=True)
    data['Name'].fillna('Unknown', inplace=True)
    data['Sex upon Outcome'] = data['Sex upon Outcome'].replace('Unknown', np.nan)

    # Split 'Sex upon Outcome' column into 'reprod' and 'gender'
    data[['reprod', 'gender']] = data['Sex upon Outcome'].str.split(' ', expand=True)

    # Create new columns for renamed attributes
    data['animal_id'] = data['Animal ID']
    data['animal_name'] = data['Name']
    data['timestmp'] = data['DateTime']
    data['dob'] = data['Date of Birth']
    data['outcome_type'] = data['Outcome Type']
    data['outcome_subtype'] = data['Outcome Subtype']
    data['animal_type'] = data['Animal Type']
    data['breed'] = data['Breed']
    data['color'] = data['Color']
    data['mnth'] = data['Month']
    data['yr'] = data['Year']

    # Drop unnecessary columns
    data.drop(['MonthYear', 'Age upon Outcome', 'Sex upon Outcome',
               'Animal ID', 'Name', 'DateTime', 'Date of Birth',
               'Outcome Type', 'Outcome Subtype', 'Animal Type',
               'Breed', 'Color', 'Month', 'Year'], axis=1, inplace=True)

    return data

def load_data(trans_data, db_url):
    conn = create_engine(db_url)
    
    # Load data into 'temp_table'
    trans_data.to_sql("temp_table", conn, if_exists="append", index=False)

    # Load data into 'timing_dim'
    timing_dim_data = trans_data[['mnth', 'yr']].drop_duplicates()
    timing_dim_data[['mnth', 'yr']].to_sql("timing_dim", conn, if_exists="append", index=False)

    # Load data into 'animal_dim'
    animal_dim_data = trans_data[['animal_id', 'animal_type', 'animal_name', 'dob', 'breed', 'color', 'reprod', 'gender', 'timestmp']]
    animal_dim_data.to_sql("animal_dim", conn, if_exists="append", index=False)

    # Load data into 'outcome_dim'
    outcome_dim_data = trans_data[['outcome_type', 'outcome_subtype']].drop_duplicates()
    outcome_dim_data.to_sql("outcome_dim", conn, if_exists="append", index=False)

    # Perform ETL and insert into 'outcome_fct'
    join_sql = text("""
                        INSERT INTO outcome_fct (outcome_dim_key, animal_dim_key, time_dim_key)
                        SELECT od.outcome_dim_key, a.animal_dim_key, td.time_dim_key
                        FROM temp_table o
                        JOIN outcome_dim od ON o.outcome_type = od.outcome_type AND o.outcome_subtype = od.outcome_subtype
                        JOIN timing_dim td ON o.mnth = td.mnth AND o.yr = td.yr
                        JOIN animal_dim a ON a.animal_id = o.animal_id AND a.animal_type = o.animal_type AND a.timestmp = o.timestmp;
                    """)

    with conn.begin() as connection:
        connection.execute(join_sql)


if __name__ == "__main__":
    input_file = sys.argv[1]
    db_url = "postgresql+psycopg2://amith:db123@db:5432/shelter"
    
    print("Start")
    data = extract_data(input_file)
    transformed_data = transform_data(data)
    transformed_data.head(3)
    load_data(transformed_data, db_url)
    print("Complete")