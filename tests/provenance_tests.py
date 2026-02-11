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

def test_sem_agg_provenance():
    df = pd.DataFrame({"note": ["Bad", "Good", "Great"]})
    res = df.sem_agg("Summarize these {note}", provenance=True)

    # For aggregation, provenance_id is a list of the source indices
    assert isinstance(res["provenance_id"].iloc[0], list)
    assert 0 in res["provenance_id"].iloc[0]
    assert 2 in res["provenance_id"].iloc[0]

def test_sem_topk_provenance():
    df = pd.DataFrame({"item": ["Human", "Ant", "Elephant"]})
    # Sort by size (Elephant > Human > Ant)
    res = df.sem_topk("Which is {item} larger?", K=2, provenance=True)
    
    # Check that we got 2 results    
    assert len(res) == 2

    # The first row should be Elephant (original index 2)
    assert res["provenance_id"].iloc[0] == 2
    # The second row should be Human (original index 0)
    assert res["provenance_id"].iloc[1] == 0

def test_sem_extract_provenance():
    df = pd.DataFrame({
        "info": ["John is 30 years old", "Jane is 25 years old"]
    })

    extract_cols = {
        "masked_col_1": "The name of the person",
        "masked_col_2": "The age of the person",
    }

    res = df.sem_extract(["info"], extract_cols, provenance=True)
    
    assert len(res) == 2
    
    # Check if the provenance column exists (using your default name)
    assert "provenance_id" in res.columns
    
    # Verify that index 0 maps to 0 and 1 maps to 1
    assert res["provenance_id"].iloc[0] == 0
    assert res["provenance_id"].iloc[1] == 1
    
    # Verify the extraction itself (simple content check)
    assert "John" in str(res.iloc[0]["masked_col_1"])
    assert "Jane" in str(res.iloc[1]["masked_col_1"])
