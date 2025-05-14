def read_file(path):
    with open(path, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
    header = {}
    vertices = set()
    arestas = set()
    arcos = set()
    vertices_requeridos = set()
    arestas_requeridas = set()
    arcos_requeridos = set()
    secao_atual = None
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("Optimal value:") or linha.startswith("Capacity:") or \
           linha.startswith("Depot Node:") or linha.startswith("#Nodes:") or \
           linha.startswith("#Edges:") or linha.startswith("#Arcs:") or \
           linha.startswith("#Required N:") or linha.startswith("#Required E:") or \
           linha.startswith("#Required A:"):
            chave, valor = linha.split(":", 1)
            header[chave.strip()] = valor.strip()
            continue
        if not linha or linha.startswith("//"):
            continue
        if linha.startswith("ReN."): secao_atual = "ReN"; continue
        elif linha.startswith("ReE."): secao_atual = "ReE"; continue
        elif linha.startswith("EDGE"): secao_atual = "EDGE"; continue
        elif linha.startswith("ReA."): secao_atual = "ReA"; continue
        elif linha.startswith("ARC"): secao_atual = "ARC"; continue
        partes = linha.split("\t")
        try:
            if secao_atual == "ReN":
                vertice = int(partes[0].replace("N", ""))
                demanda = int(partes[1])
                custo_servico = int(partes[2])
                vertices_requeridos.add((vertice, (demanda, custo_servico)))
                vertices.add(vertice)
            elif secao_atual in ["ReE", "EDGE"]:
                origem, destino = int(partes[1]), int(partes[2])
                vertices.update([origem, destino])
                aresta = (min(origem, destino), max(origem, destino))
                custo_transporte = int(partes[3])
                arestas.add((aresta, custo_transporte))
                if secao_atual == "ReE":
                    demanda = int(partes[4])
                    custo_servico = int(partes[5])
                    arestas_requeridas.add((aresta, (custo_transporte, demanda, custo_servico)))
            elif secao_atual in ["ReA", "ARC"]:
                origem, destino = int(partes[1]), int(partes[2])
                vertices.update([origem, destino])
                arco = (origem, destino)
                custo_transporte = int(partes[3])
                arcos.add((arco, custo_transporte))
                if secao_atual == "ReA":
                    demanda = int(partes[4])
                    custo_servico = int(partes[5])
                    arcos_requeridos.add((arco, (custo_transporte, demanda, custo_servico)))
        except (ValueError, IndexError):
            continue
    return header, vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos

def validar_grafo(vertices, arestas, arcos):
    for (u, v), _ in arestas:
        if u not in vertices or v not in vertices:
            print(f"Erro: Aresta ({u}, {v}) inválida.")
            exit()
    for (u, v), _ in arcos:
        if u not in vertices or v not in vertices:
            print(f"Erro: Arco ({u}, {v}) inválido.")
            exit()

def floyd_warshall(vertices, edges, arcs):
    dist = {v: {u: float('inf') for u in vertices} for v in vertices}
    pred = {v: {u: None for u in vertices} for v in vertices}
    for v in vertices:
        dist[v][v] = 0
    for (u, v), dados in edges:
        cost = dados if isinstance(dados, int) else dados[0]
        dist[u][v] = cost
        dist[v][u] = cost
        pred[u][v] = u
        pred[v][u] = v
    for (u, v), dados in arcs:
        cost = dados if isinstance(dados, int) else dados[0]
        dist[u][v] = cost
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
