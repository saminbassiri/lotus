import pandas as pd
import lotus
from lotus.models import LM

from data.sqllite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def filter_agg_movie_reviews(df, use_prov=False):

    provenance_col = "provenance_id" if use_prov else None

    filtered_df = df.sem_filter("{review} discusses quality", provenance=use_prov)
    extracted_df = filtered_df.sem_extract(
        ["review"],
        {"visual_flaws": "List visual flaws."},
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    agg_df = extracted_df.sem_agg(
        "Summarize {visual_flaws}", provenance=use_prov, provenance_col=provenance_col
    )
    target_col = agg_df.columns[0]
    bench_df = agg_df.sem_topk(
        f"Which summary in {{{target_col}}} is most critical?",
        K=5,
        provenance=use_prov,
        provenance_col=provenance_col,
    )

    return bench_df


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(DB_PATH, limit=5)

    df = pd.DataFrame(data)
    print(filter_agg_movie_reviews(df, use_prov=True))
