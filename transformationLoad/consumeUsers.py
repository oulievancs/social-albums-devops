import logging

from transformationAndLoadApp import main_users

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    main_users()
