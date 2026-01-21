
import pytest
from backend import database

def test_raptor_clusters_crud():
    """Test Create, Read, Delete for RAPTOR clusters table."""
    # 1. Clear existing (just in case)
    database.clear_clusters()
    
    # 2. Add clusters
    c1_id = database.add_cluster("Cluster Summary 1", level=0)
    c2_id = database.add_cluster("Cluster Summary 2", level=1)
    
    # 3. Verify IDs returned
    assert c1_id is not None
    assert c2_id is not None
    assert c1_id != c2_id
    
    # 4. Get by level
    level_0 = database.get_clusters_by_level(0)
    level_1 = database.get_clusters_by_level(1)
    level_2 = database.get_clusters_by_level(2)
    
    assert len(level_0) == 1
    assert level_0[0]['summary'] == "Cluster Summary 1"
    
    assert len(level_1) == 1
    assert level_1[0]['summary'] == "Cluster Summary 2"
    
    assert len(level_2) == 0
    
    # 5. Clear
    database.clear_clusters()
    assert len(database.get_clusters_by_level(0)) == 0
    assert len(database.get_clusters_by_level(1)) == 0
