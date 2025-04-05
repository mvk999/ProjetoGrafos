# O que ja foi implementado
# - Contagem de vértices      Feito
# - Contagem de arestas       Feito
# - Contagem de arcos         Feito
# - Contagem de vértices obrigatórios  Feito
# - Contagem de arestas obrigatórias   Feito
# - Contagem de arcos obrigatórios     Feito
# - Cálculo da densidade (order strength)   Feito
# - Identificação de componentes conectados Feito
# - Determinação do grau mínimo Feito
# - Determinação do grau máximo Feito
# - Cálculo da intermediação (frequência de um nó em caminhos mais curtos)
# - Cálculo do caminho médio Feito
# - Determinação do diâmetro  Feito

from pathlib import Path as P

class Graph:
    #criação do vetor dos vertices,aretas e arcos
    def __init__(self):
        self.vertices = [] 
        self.edges = []
        self.arcs = []

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_edge(self, u, v, cost):
        self.edges.append((u, v, cost))

    def add_arc(self, u, v, cost):
        self.arcs.append((u, v, cost))

def read_file(path):
     #tentativa para arrumar o erro de ler o arquivo (deu bom)
    try:
        with open(path, "r", encoding="utf-8") as arq:
            raw_lines = arq.readlines()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {path}")
        return None  # Retorna nada so para poder voltar o cod 
    except Exception as error:
        print(f"Não foi possivel abrir o arquivo. Erro: {error}") #Fiz uma exception para caso o erro nao seja de leitura
        return None
    node_pool = set()
    edge_list = set()
    arc_list = set()
    key_nodes = set()
    key_edges = set()
    key_arcs = set()
    current_block = None

    #Vou começar a leitura a patir da seção,para ignorar o cabeçalho
    for entry in raw_lines:
        entry = entry.strip()

        if entry.startswith("ReN."):
            current_block = "ReN"
            continue
        elif entry.startswith("ReE."):
            current_block = "ReE"
            continue
        elif entry.startswith("EDGE"):
            current_block = "EDGE"
            continue
        elif entry.startswith("ReA."):
            current_block = "ReA"
            continue
        elif entry.startswith("ARC"):
            current_block = "ARC"
            continue

        if entry and current_block:
            chunks = entry.split("\t")

            if current_block == "ReN":
                try:
                    nid = int(chunks[0].replace("N", ""))
                    demand_val = int(chunks[1])
                    service_fee = int(chunks[2])
                    key_nodes.add((nid, (demand_val, service_fee)))
                    node_pool.add(nid)
                except ValueError:
                    continue

            elif current_block in ["ReE", "EDGE"]:
                try:
                    n1, n2 = int(chunks[1]), int(chunks[2])
                    node_pool.update([n1, n2])
                    connection = (min(n1, n2), max(n1, n2))
                    total_fee = int(chunks[3])
                    edge_list.add((connection, total_fee))

                    if current_block == "ReE":
                        demand_val = int(chunks[4])
                        service_fee = int(chunks[5])
                        key_edges.add((connection, (total_fee, demand_val, service_fee)))
                except ValueError:
                    continue

            elif current_block in ["ReA", "ARC"]:
                try:
                    src, tgt = int(chunks[0]), int(chunks[1])
                    node_pool.update([src, tgt])
                    arc_conn = (src, tgt)
                    total_fee = int(chunks[3])
                    arc_list.add((arc_conn, total_fee))

                    if current_block == "ReA":
                        demand_val = int(chunks[4])
                        service_fee = int(chunks[5])
                        key_arcs.add((arc_conn, (total_fee, demand_val, service_fee)))
                except ValueError:
                    continue

    return node_pool, edge_list, arc_list, key_nodes, key_edges, key_arcs

def bfs(grafo, inicio):
    visitados = set()
    fila = [inicio]
    resultado = []

    while fila:
        vertice = fila.pop(0)
        if vertice not in visitados:
            visitados.add(vertice)
            resultado.append(vertice)
            fila.extend(v for v in grafo.get(vertice, []) if v not in visitados)
    return resultado

def quantidade_vertices(grafo):
    return len(grafo)

def quantidade_arestas(grafo):
    return sum(len(vizinhos) for vizinhos in grafo.values()) // 2

def grau_minimo(grafo):
    return min(len(vizinhos) for vizinhos in grafo.values())

def grau_maximo(grafo):
    return max(len(vizinhos) for vizinhos in grafo.values())

def quantidade_arcos(grafo):
    arcos = 0
    for u in grafo:
        for v in grafo[u]:
            if u in grafo[v]:
                arcos += 1
    return arcos

def floyd_warshall(grafo):
    vertices = list(grafo.keys())
    dist = {v: {u: float('inf') for u in vertices} for v in vertices}

    for v in vertices:
        dist[v][v] = 0

    for u in grafo:
        for v in grafo[u]:
            dist[u][v] = 1

    for k in vertices:
        for i in vertices:
            for j in vertices:
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist

def caminho_medio(grafo):
    dist = floyd_warshall(grafo)
    soma = 0
    total_pares = 0

    for u in dist:
        for v in dist[u]:
            if u != v and dist[u][v] != float('inf'):
                soma += dist[u][v]
                total_pares += 1

    return soma / total_pares if total_pares > 0 else 0

def calc_densidade(grafo):
    num_vertices = len(grafo)  #Número de vértices
    num_arestas = quantidade_arestas(grafo)  # Número de arestas
    num_arcos = quantidade_arcos(grafo)  # Número de arcos

    # Max de arcos e arestas
    arcs_max = num_vertices * (num_vertices - 1)
    edges_max = (num_vertices * (num_vertices - 1)) / 2

    # Calc da desnsidade
    densidade = (num_arestas + num_arcos) / (edges_max + arcs_max)
    return densidade

def calc_diametro(grafo):
    #Peguei o max da lista de distancias para calcular o diametro baseado no algoritmo do floyd warshall
    return max(max(dist.values()) for dist in floyd_warshall(grafo).values())

def calc_intermediacao(grafo):
    intermed = {v: 0 for v in grafo}
    for u in grafo:
        for v in grafo:
            if u != v:
                dist = floyd_warshall(grafo)
                for w in grafo:
                    if w != u and w != v and dist[u][w] + dist[w][v] == dist[u][v]:
                        intermed[w] += 1
    return intermed

if __name__ == "__main__":
    nome_arquivo = input("Digite o nome do arquivo/caminho: ").strip()

    resultado = read_file(nome_arquivo)

    # Verificar se esta lendo arquivo,por algum motivo nao estava lendo antes
    if resultado is None:
        print("Erro ao carregar o grafo")
        exit()

    # Desempacota os dados retornados pela função read_file
    vertices, edges, arcs, required_vertices, required_edges, key_arcs = resultado

    # Verifica se o grafo está vazio
    if not vertices:
        print("Erro: Grafo vazio.")
        exit()

    # Converte os dados para um dicionário de adjacência
    grafo = {v: [] for v in vertices}

    # Adiciona as arestas ao grafo
    for (u, v), _ in edges:
        grafo[u].append(v)
        grafo[v].append(u)

    # Adiciona os arcos ao grafo
    for (u, v), _ in arcs:
        grafo[u].append(v)

    # Define o vértice inicial para a BFS
    inicio = next(iter(vertices))  # Pega o primeiro vértice do conjunto

    # Print dos calculos feito nas def acima
    print("Ordem de visitação (BFS):", bfs(grafo, inicio))
    print("Quantidade de vértices:", quantidade_vertices(grafo))
    print("Quantidade de arestas:", quantidade_arestas(grafo))
    print("Quantidade de arcos:", quantidade_arcos(grafo))
    print("Quantidade de vértices requeridos:", len(required_vertices))
    print("Quantidade de arestas requeridas:", len(required_edges))
    print("Quantidade de arcos requeridos:", len(key_arcs))# NAO TA LENDO,SLA PQ PRECISO ARRUMAR
    print("Grau mínimo:", grau_minimo(grafo))
    print("Grau máximo:", grau_maximo(grafo))
    print("Caminho médio:", round(caminho_medio(grafo), 2))
    print("Densidade do grafo:", round(calc_densidade(grafo), 2))
    print("Diâmetro do grafo:", calc_diametro(grafo))
    print("Intermediação:", calc_intermediacao(grafo))