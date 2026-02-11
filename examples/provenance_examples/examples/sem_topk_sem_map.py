import pandas as pd
import lotus
from lotus.models import LM

from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)

def topk_map_movie_reviews(df, use_prov=False):
    
    provenance_col = "provenance_id" if use_prov else None
    
    top_reviews = df.sem_topk(
        "Which {review} shows the most extreme positive enthusiasm?",
        K=5,
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    reasoned_reviews = top_reviews.sem_map(
        "Given the {review}, list the top 3 adjectives that express the user's joy. Output: [adj1, adj2, adj3]",
        suffix="Extracted_Keywords",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    aggregated_df = reasoned_reviews.sem_agg(
        "Summarize the vocabulary of joy found in these {Extracted_Keywords}?",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    target_col = aggregated_df.columns[0]
    audiences = pd.DataFrame(
        {"target_audience": ["Cinephiles", "Mainstream Popcorn Fans"]}
    )
    bench_df = aggregated_df.sem_join(
        audiences,
        f"Would a {{target_audience:right}} member use the keywords {{{target_col}:left}}?",
        provenance=use_prov,
        provenance_col=provenance_col,
    )
    
    return bench_df

if __name__ == "__main__":
    
    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(topk_map_movie_reviews(df, use_prov=True))
