import pytest
import os
from backend import database
from backend.llm_integration import compute_cache_key, cached_generate_ai_answer

# Use a test database for isolation
TEST_DB = "data/test_cache.db"

@pytest.fixture
def setup_db():
    # Helper to switch DB connection 
    # (Since our app uses a global connection string, we might mock it or just rely on isolation)
    # For now, we test the logic functions.
    pass

def test_cache_key_computation():
    """Test that cache keys are consistent and ignore whitespace in context."""
    q = "What is the budget?"
    c1 = "The budget is $100."
    c2 = "The budget is   $100.  "
    c3 = "Different content"
    
    k1_q, k1_c = compute_cache_key(q, c1, "model1")
    k2_q, k2_c = compute_cache_key(q, c2, "model1") # Should match k1
    k3_q, k3_c = compute_cache_key(q, c3, "model1") # Should differ
    
    assert k1_q == k2_q
    assert k1_c == k2_c
    assert k1_c != k3_c

def test_database_cache_crud():
    """Test storing and retrieving from cache."""
    # We'll use the real DB functions but check if they work without error
    # Note: This runs against the real dev DB unless we mock. 
    # Given the requirements, we'll just insert a unique test key.
    
    q_hash = "test_q_hash_123"
    c_hash = "test_c_hash_123"
    model = "test_model"
    resp_type = "ai_answer"
    text = "This is a cached answer."
    
    # Clear any previous test artifact
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM response_cache WHERE query_hash=?", (q_hash,))
    conn.commit()
    conn.close()
    
    # 1. Ensure it's empty
    val = database.get_cached_response(q_hash, c_hash, model, resp_type)
    assert val is None
    
    # 2. Store
    database.cache_response(q_hash, c_hash, model, resp_type, text)
    
    # 3. Retrieve
    val = database.get_cached_response(q_hash, c_hash, model, resp_type)
    assert val == text
    
    # 4. Check Hit Count
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT hit_count FROM response_cache WHERE query_hash=?", (q_hash,))
    hit_count = c.fetchone()[0]
    # It starts at 1 (creation), accessed once -> should be 2? 
    # Implementation: Insert sets hit_count=1. Update increments it.
    # So get_cached_response call should have incremented it to 2.
    # Wait, my implementation returns None if not found, so no update.
    # If found, it updates.
    # So after cache_response: count=1
    # After get_cached_response: count=2
    assert hit_count >= 2
    conn.close()
    
    # Clean up
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM response_cache WHERE query_hash=?", (q_hash,))
    conn.commit()
    conn.close()
