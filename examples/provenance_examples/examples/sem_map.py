import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def map_movie_reviews(df, use_prov=False):
    mapped = df.sem_map(
        "From this IMDb review, output exactly ONE label from:\n"
        "acting/plot/pacing/dialogue/cinematography/sound/other\n"
        "Rules:\n"
        "- If the review is mostly positive or no clear single aspect => other\n"
        "- Return ONLY the label (one word), lowercase.\n"
        "Review: {review}",
        suffix="_aspect",
        provenance=use_prov,
    )
    return mapped


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(map_movie_reviews(df, use_prov=True))
