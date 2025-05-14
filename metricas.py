def calcular_graus(vertices, arestas, arcos):
    graus = {v: [0, 0, 0] for v in vertices}
    for (u, v), _ in arestas:
        graus[u][0] += 1
        graus[v][0] += 1
    for (u, v), _ in arcos:
        graus[u][2] += 1
        graus[v][1] += 1
    return graus

def imprimir_graus(graus):
    grau_maximo = max(sum(g) for g in graus.values())
    grau_minimo = min(sum(g) for g in graus.values())
    print("Grau máximo:", grau_maximo)
    print("Grau mínimo:", grau_minimo)

def caminho_medio(vertices, edges, arcs):
    from leitura import floyd_warshall
    dist, _ = floyd_warshall(vertices, edges, arcs)
    soma = 0
    total_pares = 0
    for u in dist:
        for v in dist[u]:
            if u != v and dist[u][v] != float('inf'):
                soma += dist[u][v]
                total_pares += 1
    return soma / total_pares if total_pares > 0 else 0

def calc_densidade(num_arestas, num_arcos, num_vertices):
    edges_max = num_vertices * (num_vertices - 1) / 2
    arcs_max = num_vertices * (num_vertices - 1)
    return (num_arestas + num_arcos) / (edges_max + arcs_max)

def calc_diametro(matriz_distancias):
    diametro = 0
    for origem in matriz_distancias:
        for destino in matriz_distancias[origem]:
            d = matriz_distancias[origem][destino]
            if d != float('inf') and origem != destino:
                diametro = max(diametro, d)
    return diametro

def calc_intermediacao(vertices, pred):
    intermediacao = {v: 0 for v in vertices}
    def caminho_minimo(origem, destino):
        if pred[origem][destino] is None:
            return []
        caminho = [destino]
        while destino != origem:
            destino = pred[origem][destino]
            caminho.append(destino)
        return caminho[::-1]
    for origem in vertices:
        for destino in vertices:
            if origem != destino:
                caminho = caminho_minimo(origem, destino)
                for v in caminho[1:-1]:
                    intermediacao[v] += 1
    return intermediacao
