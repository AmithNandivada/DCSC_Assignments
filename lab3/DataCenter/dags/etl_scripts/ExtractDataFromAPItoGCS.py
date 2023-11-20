import pytz
import requests
import pandas as pd
from datetime import datetime
from google.cloud import storage


# Set the time zone to Mountain Time
mountain_time_zone = pytz.timezone('US/Mountain')


def extract_data_from_api(limit=50000, order='animal_id'):
    """
    Function to extract data from data.austintexas.gov API.
    """
    base_url = 'https://data.austintexas.gov/resource/9t4d-g238.json'
    
    api_key = '5g60pap5ab7fpp40p5copkmj1'
    
    headers = { 
        'accept': "application/json", 
        'apikey': api_key,
    }
    
    offset = 0
    all_data = []

    while offset < 157000:  # Assuming there are 157k records
        params = {
            '$limit': str(limit),
            '$offset': str(offset),
            '$order': order,
        }

        response = requests.get(base_url, headers=headers, params=params)
        print("response : ", response)
        current_data = response.json()
        
        # Break the loop if no more data is returned
        if not current_data:
            break

        all_data.extend(current_data)
        offset += limit

    return all_data


def create_dataframe(data):
    columns = [
        'animal_id', 'name', 'datetime', 'monthyear', 'date_of_birth',
        'outcome_type', 'animal_type', 'sex_upon_outcome', 'age_upon_outcome',
        'breed', 'color'
    ]

    data_list = []
    for entry in data:
        row_data = [entry.get(column, None) for column in columns]
        data_list.append(row_data)

    df = pd.DataFrame(data_list, columns=columns)
    return df


def upload_to_gcs(dataframe, bucket_name, file_path):
    """
    Upload a DataFrame to a Google Cloud Storage bucket using service account credentials.
    """
    print("Writing data to GCS.....")
    credentials_info = {
                          "type": "service_account",
                          "project_id": "warm-physics-405522",
                          "private_key_id": "81fa8d3a1b7492d9a69dd23d64d34a925103ed0f",
                          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDIg1et67MkPfDn\nmFRgQE5zfExjKdX7LHNvVFYACX6kN6lE6WRaKmxlnWBmpGsRcNRJ4Wo6HSV6NOao\nfmeKnefZ3dc5kQjmaxdxxVQZlU0ie16Ynsj+VlmXR4z2FihCXI8jm+m0LmcaaWbe\nz2/eT56uC5dL+vfijg33m76fit5kI/+X77LSlPV7lxkiKkboJFk+NKaU7tvpyH4i\nmF1866ZVWHt5rihM3f9e0h/1waByssDIsmjYtdJmGTvvvReARMMYvdKQduWQSn8r\ntuVLLTG+BrUNaACDO85aefrvmkkUtaNYMlzmYo6hF+hivkgXQjXbekS17/ObsIpG\nKVrHTXpPAgMBAAECggEAI1D25XwpLk32m2P6IIXTC4YuEh0xQi8fGdG54AHMG3Ju\nTuPot/TW6MLiUtHMxeKgkW6xfhDaI/8jTTQOWpzbVEU9fjcsYSElnPVLjcH9NwCR\ntcHp1towp3ODwWg/qQiScYwpioHNyRodc0sIAhj18uO5vzkx5eZtUVpOJd2Ys/xP\nJbleJBT8U7e0GbcRg48HZ0a5TmaBMOGUTH+3Octj+AQcojxiI05QMO8fpGlkilD0\nbvVZIi9f1c32esJ+fCzrkUKdmiOoDtxYscyvQU4K11S6oxHr5pXdNnX8mA3pp0AP\nEcsiN7P95+6TmPLUpTbWTfYoK6233U7vOfJjbFvZOQKBgQDz/rpTJ7mw/kjRzW6t\nqeGFFSnBV/srnHoNOme0NP2/SWh1EmYPoNM2ihT6ooCY5PXKpXoL+1npESgk3PbM\nSmtAVdiyY7trnb3i43mgOEdMXSkokjp2B9dW7yYwe2ONOarQpro0f2aoTqY0CCHW\ng/viIBn42OKwIo52I1TswVD7AwKBgQDSYO5++QI/TnFvSU6zJ8K1JhcO6F6SwJ1Y\nntM7T7jnCaEZ+pZPR/FskLZNXeBhDFGgMzFw8jHtm7Gh+t4KevJ3d/78+9iuKkBU\nBfDo8maXZHfAsUeZxgbE5tqhqvW8myds7AO+3G8IuMMyW30df2otZAd4guajxOtr\nm8ZQ/4EbxQKBgQDbpI8ulDBA+GetFfVwN+Ff3/E6r2zXkYD9r3nza1CRhg+Wc/2U\nS/5Wtm60QNzqxhHNXrFDX/1MJbmxlYhF1yg9PgpYbBcnhVSOjp/Kb18fiy2l7Bzc\na6qaA6apNioj06nFMpGk+Jr9H+/WHwv3A9EXejZnITbPwAvmpV+p0UyI6QKBgQCh\nFAyn9XquBB7Aaa2zaNchIif3hx2aWZZgG0N6n0DgzTOnk4Fw9JG6YVbkB+PcCrWY\n5nmNlDN8TYCFmHJYLejmZl87To2KVNlqPB5IDglVE1zJkjNTXxchvexaam662UUn\nldIMWfU+BVGXhgtXAY7HcFZ0BC4Z6JWkj+IZdHhjTQKBgGMevGX290oV4tO1Fd1J\ntuf0CBNmuDkeImxjXu/RqAxJANNpOVZDQ0HMOB8R94LghZstXoSDRjGfWv+fGlJe\nu6oeWd1WxKNHGSkCi9lKQa+/xBkXe/gGm8kKT12XmBc3RZdiGMkmBOOcBQ6t1opX\nTnjNgClRMXpP6krPqDL8+1bB\n-----END PRIVATE KEY-----\n",
                          "client_email": "accessdatacenterdata@warm-physics-405522.iam.gserviceaccount.com",
                          "client_id": "115239160111022688572",
                          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                          "token_uri": "https://oauth2.googleapis.com/token",
                          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/accessdatacenterdata%40warm-physics-405522.iam.gserviceaccount.com",
                          "universe_domain": "googleapis.com"
                        }

    client = storage.Client.from_service_account_info(credentials_info)
    csv_data = dataframe.to_csv(index=False)
    
    bucket = client.get_bucket(bucket_name)
    
    current_date = datetime.now(mountain_time_zone).strftime('%Y-%m-%d')
    formatted_file_path = file_path.format(current_date, current_date)
    
    blob = bucket.blob(formatted_file_path)
    blob.upload_from_string(csv_data, content_type='text/csv')
    print(f"Finished writing data to GCS with date: {current_date}.")


def main():
    extracted_data = extract_data_from_api(limit=50000, order='animal_id')
    shelter_data = create_dataframe(extracted_data)

    gcs_bucket_name = 'datacenter1798'
    gcs_file_path = 'data/{}/outcomes_{}.csv'

    upload_to_gcs(shelter_data, gcs_bucket_name, gcs_file_path)