import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def filter_movie_reviews(df, use_prov=False):
    filtered_df = df.sem_filter(
        "The {review} is positive about the movie's storyline?", provenance=use_prov
    )
    return filtered_df


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(filter_movie_reviews(df, use_prov=True))
