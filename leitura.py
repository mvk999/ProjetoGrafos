def read_and_extract(path):
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    vertices = set()
    edges = set()
    arcs = set()
    req_vertices = set()
    req_edges = set()
    req_arcs = set()
    section = None
    header = {}
    id_req = {}
    id_req_ea = {}

    id_servico = 1
    for line in lines:
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()
            continue
        if line.startswith("ReN."): section = "ReN"; continue
        if line.startswith("ReE."): section = "ReE"; continue
        if line.startswith("EDGE"): section = "EDGE"; continue
        if line.startswith("ReA."): section = "ReA"; continue
        if line.startswith("ARC"): section = "ARC"; continue
        if not line or line.startswith("//"): continue

        parts = line.split("\t")
        try:
            if section == "ReN":
                v = int(parts[0].replace("N", ""))
                d, c = int(parts[1]), int(parts[2])
                req_vertices.add((v, (d, c)))
                id_req[(v, (d, c))] = id_servico
                vertices.add(v)
                id_servico += 1
            elif section in ["ReE", "EDGE"]:
                u, v = int(parts[1]), int(parts[2])
                c = int(parts[3])
                edge = (min(u, v), max(u, v))
                edges.add((edge, c))
                vertices.update([u, v])
                if section == "ReE":
                    d, cs = int(parts[4]), int(parts[5])
                    req_edges.add((edge, (c, d, cs)))
                    id_req_ea[(edge, (c, d, cs))] = id_servico
                    id_servico += 1
            elif section in ["ReA", "ARC"]:
                u, v = int(parts[1]), int(parts[2])
                c = int(parts[3])
                arc = (u, v)
                arcs.add((arc, c))
                vertices.update([u, v])
                if section == "ReA":
                    d, cs = int(parts[4]), int(parts[5])
                    req_arcs.add((arc, (c, d, cs)))
                    id_req_ea[(arc, (c, d, cs))] = id_servico
                    id_servico += 1
        except:
            continue

    return header, vertices, edges, arcs, req_vertices, req_edges, req_arcs, id_req, id_req_ea


def floyd_warshall(vertices, edges, arcs):
    dist = {v: {u: float("inf") for u in vertices} for v in vertices}
    pred = {v: {u: None for u in vertices} for v in vertices}
    for v in vertices:
        dist[v][v] = 0
    for (u, v), c in edges:
        dist[u][v] = dist[v][u] = c
        pred[u][v], pred[v][u] = u, v
    for (u, v), c in arcs:
        dist[u][v] = c
        pred[u][v] = u
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]
    return dist, pred


def caminho_minimo(pred, u, v):
    if pred[u][v] is None:
        return []
    caminho = [v]
    while v != u:
        v = pred[u][v]
        caminho.append(v)
    return caminho[::-1]