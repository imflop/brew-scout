async def test_get_cities(client):
    res = await client.get("/api/v1/cities")
    assert res.status_code == 200
