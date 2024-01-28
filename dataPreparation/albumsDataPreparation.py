"""A script regarding reading a csv regarding Music albums and artis/bands file
and add the rows into a MongoDB.
"""
import os
import zipfile
from datetime import datetime

import musicbrainzngs
import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame
from pymongo.collection import Collection

from common.mongoDb import MyMongoClient
from common.webUtils import WebUtils

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


def group_albums_by_artist(collection: Collection, zip_file_path: str, csv_file_path: str):
    try:
        aa = 0
        # Read CSV file into a DataFrame
        df = read_csv_from_zip(zip_file_path, csv_file_path)

        # Group by the artist column
        grouped_by_artist = df.groupby(df.columns[3])

        # Iterate over groups and create a nested array for each artist
        for artist, group in grouped_by_artist:
            aa += 1
            count = collection.count_documents({"$and": [{"artist_name": {"$eq": artist}}, {"year": {"$ne": None}}]})

            if count <= 0:
                collection_artist_delete(collection, artist)

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
                result["year"] = get_artist_data_all(artist, albums[0][1])

                collection.insert_one(result)
    except Exception as e:
        print(f"Error grouping albums by artist: {e}. Group: {group}, Row: {group}")
        raise


"""Functionality regarding deletion of artist."""


def collection_artist_delete(collection: Collection, artist_name: str):
    collection.delete_one({"artist_name": {"$eq": artist_name}})


def read_csv_from_zip(zip_file_path: str, csv_file_name: str) -> DataFrame:
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            # Assuming the CSV file is at the root of the zip archive
            with zip_file.open(csv_file_name) as csv_file:
                df = pd.read_csv(csv_file)
                return df
    except Exception as e:
        print(f"Error reading CSV from zip file: {e}")
        raise


"""Tries for all options in order to load artist year."""


def get_artist_data_all(artist_name: str, album_name: str):
    try:
        return get_artist_data(artist_name, album_name)
    except:
        try:
            return get_artist_data_open(artist_name)
        except:
            try:
                return get_artist_data_musicbrainzngs(artist_name)
            except:
                return None


def get_artist_data(artist_name: str, album_name: str):
    key = os.environ.get("EXTERNAL_API_ARTIST_KEY")
    url = f"http://api.onemusicapi.com/20171116/release?artist={artist_name}&user_key={key}&maxResultCount={1}&title={album_name}"

    response = requests.get(url)

    if response.status_code == 200:
        # Print the response content (assuming the API returns JSON)
        jsonResponse = response.json()

        if jsonResponse[0]["year"]:
            return jsonResponse[0]["year"]
        else:
            raise Exception(f"Error getting artist")
    else:
        raise Exception(f"Error getting artist")


"""Calling an OPEN API regarding get information about artists."""


def get_artist_data_open(artist_name: str):
    url = f"https://www.theaudiodb.com/api/v1/json/2/search.php?s={artist_name}"

    response = requests.get(url)

    if response.status_code == 200:
        # Print the response content (assuming the API returns JSON)
        jsonResponse = response.json()

        if (jsonResponse and jsonResponse["artists"] and jsonResponse["artists"]
                and jsonResponse["artists"][0]["intBornYear"]):
            return jsonResponse["artists"][0]["intBornYear"]
        else:
            return None
    else:
        raise Exception(f"Error getting artist")


def get_artist_data_musicbrainzngs(artist_name: str):
    try:
        musicbrainzngs.set_useragent("Mozilla/5.0 (Windows NT 10.0;", "v1.0.0", "bbaggellis1997@gmail.com")
        artist = musicbrainzngs.search_artists(query=artist_name, limit=None, offset=None, strict=False)

        vartist_names = set([artist_name.lower()])
        if artist_name.find("&"):
            # Split the string using "&" as the delimiter
            split_strings = artist_name.split("&")

            # Create a set from the list of substrings
            vartist_names = set(el.lower() for el in split_strings)

        for art in artist["artist-list"]:
            if str(art["name"]).lower() in vartist_names and WebUtils.dictionary_contains_key(art, "life-span"):
                art = art["life-span"]
                if WebUtils.dictionary_contains_key(art, "begin"):
                    return art["begin"]

        raise Exception(f"Error getting artist")
    except Exception as e:
        print(f"Error getting {e}")

        raise e


def main():
    # MongoDB connection settings
    mongo_uri = os.environ.get("MONGODB_URI")
    database_name = os.environ.get("MONGODB_NAME")
    collection_name = os.environ.get("MONGODB_COLLECTION_NAME")

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
