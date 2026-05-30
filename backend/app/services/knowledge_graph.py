"""Knowledge graph service — Neo4j operations for cross-meeting entity linking."""

from neo4j import AsyncSession


async def upsert_meeting_node(session: AsyncSession, meeting_id: str, title: str, date: str):
    await session.run(
        """
        MERGE (m:Meeting {id: $id})
        SET m.title = $title, m.date = $date
        """,
        id=meeting_id, title=title, date=date,
    )


async def upsert_person_node(session: AsyncSession, name: str, user_id: str | None = None):
    await session.run(
        """
        MERGE (p:Person {name: $name})
        SET p.user_id = $user_id
        """,
        name=name, user_id=user_id,
    )


async def link_person_to_meeting(session: AsyncSession, person_name: str, meeting_id: str, role: str = "PARTICIPATED"):
    await session.run(
        """
        MATCH (p:Person {name: $name}), (m:Meeting {id: $meeting_id})
        MERGE (p)-[:PARTICIPATED_IN {role: $role}]->(m)
        """,
        name=person_name, meeting_id=meeting_id, role=role,
    )


async def upsert_topic_node(session: AsyncSession, topic: str):
    await session.run(
        "MERGE (t:Topic {name: $topic})",
        topic=topic,
    )


async def link_topic_to_meeting(session: AsyncSession, topic: str, meeting_id: str):
    await session.run(
        """
        MATCH (t:Topic {name: $topic}), (m:Meeting {id: $meeting_id})
        MERGE (t)-[:DISCUSSED_IN]->(m)
        """,
        topic=topic, meeting_id=meeting_id,
    )


async def get_meeting_graph(session: AsyncSession, meeting_id: str) -> dict:
    """Return nodes and edges for the D3.js graph viewer."""
    result = await session.run(
        """
        MATCH (m:Meeting {id: $id})
        OPTIONAL MATCH (p:Person)-[:PARTICIPATED_IN]->(m)
        OPTIONAL MATCH (t:Topic)-[:DISCUSSED_IN]->(m)
        RETURN m, collect(DISTINCT p) as people, collect(DISTINCT t) as topics
        """,
        id=meeting_id,
    )
    record = await result.single()
    if not record:
        return {"nodes": [], "edges": []}

    nodes = [{"id": meeting_id, "type": "Meeting", "label": record["m"]["title"]}]
    edges = []

    for person in record["people"]:
        nodes.append({"id": person["name"], "type": "Person", "label": person["name"]})
        edges.append({"source": person["name"], "target": meeting_id, "relation": "PARTICIPATED_IN"})

    for topic in record["topics"]:
        nodes.append({"id": topic["name"], "type": "Topic", "label": topic["name"]})
        edges.append({"source": topic["name"], "target": meeting_id, "relation": "DISCUSSED_IN"})

    return {"nodes": nodes, "edges": edges}


async def get_cross_meeting_graph(session: AsyncSession, workspace_id: str, limit: int = 50) -> dict:
    """Return a cross-meeting knowledge graph for the D3.js viewer."""
    result = await session.run(
        """
        MATCH (m:Meeting)
        WHERE m.workspace_id = $workspace_id
        WITH m LIMIT $limit
        OPTIONAL MATCH (p:Person)-[:PARTICIPATED_IN]->(m)
        OPTIONAL MATCH (t:Topic)-[:DISCUSSED_IN]->(m)
        RETURN collect(DISTINCT m) as meetings,
               collect(DISTINCT p) as people,
               collect(DISTINCT t) as topics
        """,
        workspace_id=workspace_id, limit=limit,
    )
    record = await result.single()
    if not record:
        return {"nodes": [], "edges": []}

    nodes, edges = [], []

    for m in record["meetings"]:
        nodes.append({"id": m["id"], "type": "Meeting", "label": m["title"]})

    for p in record["people"]:
        nodes.append({"id": p["name"], "type": "Person", "label": p["name"]})

    for t in record["topics"]:
        nodes.append({"id": t["name"], "type": "Topic", "label": t["name"]})

    return {"nodes": nodes, "edges": edges}
