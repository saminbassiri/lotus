import pandas as pd
import lotus
from lotus.models import LM
import os
import subprocess

from data.sqllite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def agg_movie_reviews(df, use_prov=False):
    summary = df.sem_agg(
        "You summarize ONE group of reviews (same {sentiment}).\n"
        "Output up to 3 bullets, each exactly:\n"
        "- Theme=<short>; Evidence=<short phrase>\n"
        "Use only {review}.",
        group_by=["sentiment"],
        provenance=use_prov,
    )
    return summary


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(DB_PATH, limit=5)

    df = pd.DataFrame(data)
    print(agg_movie_reviews(df, use_prov=True))
