import pandas as pd
import lotus
from lotus.models import LM

from data.sqllite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def topk_movie_reviews(df, use_prov=False):
    topk = df.sem_topk(
        "Rank by strongest positive enthusiasm and excitement.\n"
        "Prefer reviews with intense praise, strong emotion, and superlatives.\n"
        "Use ONLY the review text: {review}",
        K=5,
        provenance=use_prov,
    )
    return topk


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(DB_PATH, limit=5)

    df = pd.DataFrame(data)
    print(topk_movie_reviews(df, use_prov=True))
