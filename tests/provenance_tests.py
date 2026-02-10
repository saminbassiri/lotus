import pandas as pd

import lotus
from lotus.models import LM

lm = LM(model=f"")

lotus.settings.configure(lm=lm)

def test_sem_filter_provenance():
    df = pd.DataFrame({"city": ["Paris", "Mars", "London"]})
    # Filter for real cities
    res = df.sem_filter("{city} is a real city on Earth", provenance=True)
    
    # Ensure 'Mars' was filtered out but 'Paris' remains
    assert len(res) == 2
    
    # Check provenance_id column
    # Use .values[0] or .iloc[0] to avoid index-alignment issues
    assert "provenance_id" in res.columns, f"Available columns: {res.columns}"
    assert res["provenance_id"].iloc[0] == 0
    assert res["provenance_id"].iloc[1] == 2

