import logging

from transformationAndLoadApp import main_artists

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    main_artists()
