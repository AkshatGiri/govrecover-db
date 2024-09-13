#!/usr/bin/env python3

from dotenv import load_dotenv
import psycopg2
import os
import requests
import zipfile
from io import BytesIO
import shutil
from datetime import datetime


load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


# Database connection parameters
conn_params = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host':  DB_HOST,
    'port': DB_PORT
}

def connect_to_db():
    try:
        conn = psycopg2.connect(**conn_params)
        print("Connection established.")
        return conn
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")

def purge_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS claims CASCADE;")
        conn.commit()
        cursor.close()
        print("Table 'claims' purged successfully.")
    except Exception as e:
        print(f"Error purging the table: {e}")

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
           CREATE TABLE claims (
              id SERIAL PRIMARY KEY,
              PROPERTY_ID BIGINT,
              PROPERTY_TYPE TEXT,
              CASH_REPORTED NUMERIC(10, 2),
              SHARES_REPORTED NUMERIC(14, 6),
              NO_OF_OWNERS TEXT,
              OWNER_NAME TEXT,
              OWNER_STREET_1 TEXT,
              OWNER_STREET_2 TEXT,
              OWNER_STREET_3 TEXT,
              OWNER_CITY TEXT,
              OWNER_STATE CHAR(2),
              OWNER_ZIP VARCHAR(10),
              OWNER_COUNTRY_CODE CHAR(3),
              HOLDER_NAME TEXT,
              HOLDER_STREET_1 TEXT,
              HOLDER_STREET_2 TEXT,
              HOLDER_STREET_3 TEXT,
              HOLDER_CITY TEXT,
              HOLDER_STATE CHAR(2),
              HOLDER_ZIP VARCHAR(10)
          );
        """)
        conn.commit()
        cursor.close()
        print("Table 'claims' created successfully.")
    except Exception as e:
        print(f"Error creating the table: {e}")

def create_index(conn):
    """Create an index on the PROPERTY_ID column in the 'claims' table."""
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX idx_property_id ON claims (PROPERTY_ID);")
        conn.commit()
        cursor.close()
        print("Index on PROPERTY_ID created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")
        
        
def import_csv_to_db(conn, file_path):
    """Import data from a CSV file into the 'claims' table."""
    try:
        cursor = conn.cursor()
        with open(file_path, 'r') as f:
            # Skip the header row (change to f if your CSV doesn't have a header)
            next(f)
            cursor.copy_from(f, 'claims', sep=',')
        conn.commit()
        cursor.close()
        print("Data imported successfully from CSV.")
    except Exception as e:
        print(f"Error importing data from CSV: {e}")
        
def import_csv_to_db_with_copy_expert(conn, file_path):
    """Import data from a CSV file into the 'claims' table using copy_expert."""
    cursor = conn.cursor()
    sql = """
    COPY claims (
        PROPERTY_ID, 
        PROPERTY_TYPE, 
        CASH_REPORTED, 
        SHARES_REPORTED, 
        NO_OF_OWNERS, 
        OWNER_NAME, 
        OWNER_STREET_1, 
        OWNER_STREET_2, 
        OWNER_STREET_3, 
        OWNER_CITY, 
        OWNER_STATE, 
        OWNER_ZIP, 
        OWNER_COUNTRY_CODE, 
        HOLDER_NAME, 
        HOLDER_STREET_1, 
        HOLDER_STREET_2, 
        HOLDER_STREET_3, 
        HOLDER_CITY, 
        HOLDER_STATE, 
        HOLDER_ZIP
    ) FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"' ESCAPE '"';
    """
    with open(file_path, 'r', encoding='ISO-8859-1', errors='replace') as f:
        cursor.copy_expert(sql, f)
    conn.commit()
    cursor.close()
    print("Data imported successfully using copy_expert.")
    
    
def download_and_unzip(url: str, extract_to: str ='.'):
      """
      Download a ZIP file from a URL and unzip it in the specified directory with progress indicator.

      Args:
      url (str): The URL of the ZIP file to download.
      extract_to (str): Directory path to extract the files.
      """
      # Send a GET request to the URL
      response = requests.get(url, stream=True)  # Use stream=True to download the content in chunks
      total_size = int(response.headers.get('content-length', 0))  # Get the total size of the file
      block_size = 2048  # Set the block size to 1KB

      print("Downloading ZIP file...")
      with open('temp.zip', 'wb') as file:
          downloaded = 0
          for data in response.iter_content(block_size):
              downloaded += len(data)
              file.write(data)
              done = int(50 * downloaded / total_size)
              print(f"\r[{'#' * done}{'.' * (50-done)}] {downloaded * 100 / total_size:.2f}%", end='\r')
      print("Download completed.")

      # Open the ZIP file contained in the temporary file
      with zipfile.ZipFile('temp.zip', 'r') as the_zip:
          # Extract all the contents into the directory specified
          the_zip.extractall(path=extract_to)
          print(f"Files extracted to {extract_to}")
      # Optionally remove the temp.zip file if not needed
      os.remove('temp.zip')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=========================")
    print(f"Start Time: {datetime.now()}")
    print("=========================")
    
    download_url = "https://dpupd.sco.ca.gov/00_All_Records.zip"
    extract_to_path = ROOT_DIR
    
    download_and_unzip(download_url, extract_to_path)
    
    extracted_folder_path = os.path.join(ROOT_DIR, "00_All_Records")
    file_path = os.path.join(extracted_folder_path, "All_Records__File_1_of_1.csv")
    
    conn = connect_to_db()
    if conn is not None:
        purge_table(conn)
        create_table(conn)
        import_csv_to_db_with_copy_expert(conn, file_path)
        create_index(conn)
        conn.close()
        
    shutil.rmtree(extracted_folder_path)
    print("Temporary folder deleted.")
    print(f"End Time: {datetime.now()}")
    print("=========================")
        

if __name__ == "__main__":
    main()