"""A script regarding reading a csv regarding Music albums and artis/bands file
and add the rows into a MongoDB.
"""
import os
import zipfile
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from common.mongoDb import MyMongoClient

# Load environment variables from .env file
load_dotenv()


def merge_list(list_of_lists):
    try:
        # Convert the list of lists into a set of lists with unique elements
        set_of_lists = {tuple(set(inner.split(',') if isinstance(inner, str) else [inner]))
                        for outer in list_of_lists
                        for inner in outer
                        if inner and not pd.isna(inner)
                        }

        # Convert the set of lists back to a list for display purposes
        return list(
            set([item.strip() if isinstance(item, str) else item for inner_set in set_of_lists for item in inner_set]))
    except Exception as e:
        print(f"Error merging list input [{list_of_lists}]: {e}")
        raise


def group_albums_by_artist(collection, zip_file_path, csv_file_path):
    try:
        aa = 0
        # Read CSV file into a DataFrame
        df = read_csv_from_zip(zip_file_path, csv_file_path)

        # Group by the artist column
        grouped_by_artist = df.groupby(df.columns[3])

        # Iterate over groups and create a nested array for each artist
        for artist, group in grouped_by_artist:
            aa += 1
            result = {}
            albums = group.iloc[:,
                     [1, 2, 4, 5, 9, 10, 11]].values.tolist()  # Assuming the first 3 columns are album information
            result["aa"] = aa
            result["albums"] = []

            for al in albums:
                result["albums"].append({
                    "position": al[0],
                    "release_name": al[1],
                    "release_date": datetime.strptime(al[2], "%Y-%m-%d"),
                    "release_type": al[3],
                    "avg_rating": al[4],
                    "rating_count": al[5],
                    "review_count": al[6],
                })

            result["artist_name"] = artist
            # Merge the comma-separated strings and convert to a list
            result["primary_genres"] = merge_list(group.iloc[:, [6]].values.tolist())
            result["secondary_genres"] = merge_list(group.iloc[:, [7]].values.tolist())
            result["descriptors"] = merge_list(group.iloc[:, [8]].values.tolist())

            collection.insert_one(result)
    except Exception as e:
        print(f"Error grouping albums by artist: {e}")
        raise


def read_csv_from_zip(zip_file_path, csv_file_name):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            # Assuming the CSV file is at the root of the zip archive
            with zip_file.open(csv_file_name) as csv_file:
                df = pd.read_csv(csv_file)
                return df
    except Exception as e:
        print(f"Error reading CSV from zip file: {e}")
        raise


def main():
    # MongoDB connection settings
    mongo_uri = os.environ.get("MONGODB_URI")
    database_name = "MusicAlbums"
    collection_name = "Albums"

    # CSV file path
    csv_zip_file_path = "resources/rym_clean1.csv.zip"
    csv_file_path = "rym_clean1.csv"

    collection = None
    client = None

    try:
        # Connect to MongoDB
        collection, client = MyMongoClient.connect_to_mongodb(mongo_uri, database_name, collection_name)

        # Insert CSV data into MongoDB collection
        group_albums_by_artist(collection, csv_zip_file_path, csv_file_path)

        print(f"CSV data successfully inserted into {database_name}.{collection_name} collection.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close MongoDB connection in the finally block to ensure it happens regardless of exceptions
        if client:
            MyMongoClient.close_mongodb_connection(client)


if __name__ == "__main__":
    main()
