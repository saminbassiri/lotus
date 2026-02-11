import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def extract_movie_reviews(df, use_prov=False):
    input_cols = ["review"]
    output_cols = {
        "key_aspects": "The key aspects of the movie plot discussed in the review."
    }
    extracted_df = df.sem_extract(input_cols, output_cols, provenance=use_prov)
    return extracted_df


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(extract_movie_reviews(df, use_prov=True))
