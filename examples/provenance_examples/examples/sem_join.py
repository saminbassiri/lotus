import pandas as pd
import lotus
from lotus.models import LM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
from examples.provenance_examples.examples.data.sqlite_db import get_data_from_sql_as_dict, DB_PATH

lm = LM(model=f"ollama/llama3.2:3b")

lotus.settings.configure(lm=lm)


def join_movie_reviews(df, use_prov=False):
    df_categories = pd.DataFrame(
        {
            "category": [
                "acting",
                "plot",
                "pacing",
                "dialogue",
                "cinematography",
                "sound",
                "other",
            ],
            "definition": [
                "complaints/praise about performance, cast, acting quality",
                "story, narrative, twists, logic, writing of story",
                "slow/boring/dragging, too long, rhythm of the movie",
                "lines, script quality, conversations, writing of dialogue",
                "visuals, camera work, lighting, editing, VFX, look/feel",
                "music, audio, volume, sound effects, mixing",
                "no clear single category; general opinion or mixed feedback",
            ],
        }
    )
    joined = df.sem_join(
        df_categories,
        "Choose the single best {category:right} for this review. "
        "If it matches {definition:right}, then assign it.\n\n"
        "Review: {review:left}",
        provenance=use_prov,
    )
    return joined


if __name__ == "__main__":

    data = get_data_from_sql_as_dict(limit=5)

    df = pd.DataFrame(data)
    print(join_movie_reviews(df, use_prov=True))
