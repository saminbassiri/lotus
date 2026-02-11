import pandas as pd

import lotus
from lotus.models import LM

lm = LM(model="gpt-4o-mini")

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

def test_sem_join_provenance():
    left_df = pd.DataFrame({"brand": ["Tesla"]}) # Index 0
    right_df = pd.DataFrame({"model": ["Civic", "Model 3"]}) # Index 0, 1
    
    res = left_df.sem_join(right_df, "{brand} makes {model}", provenance=True)
    
    # If your join logic preserves IDs from both sides:
    assert "provenance_id" in res.columns
    # The original index of "Tesla" in left_df and "Model 3" in right_df
    assert res["provenance_id"].iloc[0] == (0, 1)

def test_sem_map_provenance():
    df = pd.DataFrame({"text": ["Apple", "Banana"]})
    res = df.sem_map("What color is fruits {text}?", provenance=True)
    
    assert len(res) == 2
    # In a map, provenance should match the current index 1:1
    assert res["provenance_id"].tolist() == [0, 1]

if __name__ == "__main__":
    test_sem_map_provenance()
