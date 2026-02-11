import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def join_filter_movie_reviews(df, use_prov=False):

    provenance_col = "provenance_id" if use_prov else None

    extracted_df = df.sem_extract(
        ["review"],
        {"key_quote": "A short characteristic quote from the review."},
        provenance=use_prov,
        provenance_col=provenance_col,
    )

    filtered_df = extracted_df.sem_filter(
        "{review} expresses a negative sentiment toward the film", provenance=use_prov, provenance_col=provenance_col
    )
    categories = pd.DataFrame(
        {"category": ["technical and analytical", "emotional and subjective"]}
    )
    joined_df = filtered_df.sem_join(
        categories,
        "{review} primarily falls under the {category} style of writing. Only answer with the EXACT category.",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    bench_df = joined_df.sem_filter(
        "{key_quote} fits the {category} style",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    
    return bench_df


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(join_filter_movie_reviews(df, use_prov=True))
