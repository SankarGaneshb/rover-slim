from rover_slim.synthesizers.matrix import BaseImageRecommender

def test_recommends_slim_for_binary_packages():
    recommender = BaseImageRecommender(["numpy", "fastapi", "psycopg2"])
    res = recommender.recommend()
    assert "slim" in res["recommended_base_image"]
    assert res["requires_glibc"] is True

def test_recommends_alpine_for_pure_python():
    recommender = BaseImageRecommender(["click", "requests", "jinja2"])
    res = recommender.recommend()
    assert "alpine" in res["recommended_base_image"]
    assert res["requires_glibc"] is False
