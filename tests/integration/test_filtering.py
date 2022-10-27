import pytest

from labelbox import Project
from labelbox.exceptions import InvalidQueryError
from labelbox.schema.queue_mode import QueueMode


# Avoid assertions using equality to prevent intermittent failures due to
# other builds simultaneously adding projects to test org
def test_where(client):
    p_a = client.create_project(name="a", queue_mode=QueueMode.Dataset)
    p_b = client.create_project(name="b", queue_mode=QueueMode.Dataset)
    p_c = client.create_project(name="c", queue_mode=QueueMode.Dataset)

    def _get(f, where=None):
        date_where = Project.created_at >= p_a.created_at
        where = date_where if where is None else where & date_where
        return {p.uid for p in client.get_projects(where)}

    def get(where=None):
        return _get(client.get_projects, where)

    assert {p_a.uid, p_b.uid, p_c.uid}.issubset(get())
    e_a = get(Project.name == "a")
    assert p_a.uid in e_a and p_b.uid not in e_a and p_c.uid not in e_a
    not_b = get(Project.name != "b")
    assert {p_a.uid, p_c.uid}.issubset(not_b) and p_b.uid not in not_b
    gt_b = get(Project.name > "b")
    assert p_c.uid in gt_b and p_a.uid not in gt_b and p_b.uid not in gt_b
    lt_b = get(Project.name < "b")
    assert p_a.uid in lt_b and p_b.uid not in lt_b and p_c.uid not in lt_b
    ge_b = get(Project.name >= "b")
    assert {p_b.uid, p_c.uid}.issubset(ge_b) and p_a.uid not in ge_b
    le_b = get(Project.name <= "b")
    assert {p_a.uid, p_b.uid}.issubset(le_b) and p_c.uid not in le_b

    dataset = client.create_dataset(name="Dataset")
    p_a.datasets.connect(dataset)
    p_b.datasets.connect(dataset)
    p_c.datasets.connect(dataset)

    def get(where=None):
        return _get(dataset.projects, where)

    assert {p_a.uid, p_b.uid, p_c.uid}.issubset(get())
    e_a = get(Project.name == "a")
    assert p_a.uid in e_a and p_b.uid not in e_a and p_c.uid not in e_a
    not_b = get(Project.name != "b")
    assert {p_a.uid, p_c.uid}.issubset(not_b) and p_b.uid not in not_b
    gt_b = get(Project.name > "b")
    assert p_c.uid in gt_b and p_a.uid not in gt_b and p_b.uid not in gt_b
    lt_b = get(Project.name < "b")
    assert p_a.uid in lt_b and p_b.uid not in lt_b and p_c.uid not in lt_b
    ge_b = get(Project.name >= "b")
    assert {p_b.uid, p_c.uid}.issubset(ge_b) and p_a.uid not in ge_b
    le_b = get(Project.name <= "b")
    assert {p_a.uid, p_b.uid}.issubset(le_b) and p_c.uid not in le_b

    dataset.delete()
    p_a.delete()
    p_b.delete()
    p_c.delete()


def test_unsupported_where(client):
    with pytest.raises(InvalidQueryError):
        client.get_projects(where=(Project.name == "a") & (Project.name == "b"))

    # TODO support logical OR and NOT in where
    with pytest.raises(InvalidQueryError):
        client.get_projects(where=(Project.name == "a") |
                            (Project.description == "b"))

    with pytest.raises(InvalidQueryError):
        client.get_projects(where=~(Project.name == "a"))
