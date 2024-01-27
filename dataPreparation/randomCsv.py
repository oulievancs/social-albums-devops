import pandas as pd
import json
import random

# Read the dataset
df = pd.read_csv("resources/MOCK_DATA.csv")

NUMBER_OF_ALBUMS = 2090
NUMBER_OF_USERS = 180


# Function to generate random numbers for album_ids and friends
def generate_random_numbers(start, end, count, excluded_values=None):
    if excluded_values is None:
        excluded_values = []
    return [value for value in random.sample(range(start, end + 1), count) if value not in excluded_values]


# Fill album_ids with a JSON array of numbers between 1 and 5000
df["artist_ids"] = df.apply(lambda x: json.dumps(generate_random_numbers(1, NUMBER_OF_ALBUMS, random.randint(2, 7))),
                            axis=1)

# Fill friends with numbers between 5 and 15
df["friends"] = df.apply(lambda x: json.dumps(generate_random_numbers(1, NUMBER_OF_USERS, random.randint(5, 15), [x.iloc[0]])),
                         axis=1)

# Save the modified dataset
df.to_csv("resources/MOCK_DATA_OUT.csv", index=False)
