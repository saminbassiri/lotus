import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def extract_filter_movie_reviews(df, use_prov=False):

    provenance_col = "provenance_id" if use_prov else None

    input_cols = ["review"]
    output_cols = {
        "key_aspects": "The key aspect of the movie discussed in the review."
    }

    extracted_df = df.sem_extract(input_cols, output_cols, provenance=use_prov)
    filtered_df = extracted_df.sem_filter(
        "{key_aspects} is a meaningful description.",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    mapped_df = filtered_df.sem_map(
        "Classify the {key_aspects} into exactly: 'Content' or 'Other'. Respond with ONLY the word.",
        suffix="category",
        provenance=use_prov,
        provenance_col=provenance_col,
    )

    filtered_2_df = mapped_df.sem_filter(
        "{category} is 'Content'", provenance=use_prov, provenance_col=provenance_col
    )

    result = filtered_2_df.sem_agg(
        "Summarize the {key_aspects} of these {review}s?",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    return result


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(extract_filter_movie_reviews(df, use_prov=True))
