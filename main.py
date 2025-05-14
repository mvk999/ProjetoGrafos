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
# - Cálculo da intermediação (frequência de um nó em caminhos mais curtos) Feito
# - Cálculo do caminho médio Feito
# - Determinação do diâmetro  Feito

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
    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{path}' não encontrado.")
        exit()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        exit()

    # Inicializa os dados
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

        if linha.startswith("ReN."):
            secao_atual = "ReN"
            continue
        elif linha.startswith("ReE."):
            secao_atual = "ReE"
            continue
        elif linha.startswith("EDGE"):
            secao_atual = "EDGE"
            continue
        elif linha.startswith("ReA."):
            secao_atual = "ReA"
            continue
        elif linha.startswith("ARC"):
            secao_atual = "ARC"
            continue

        if linha and secao_atual:
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
                print(f"Erro ao processar linha: {linha}")
                continue

    if not vertices:
        print("Erro: Nenhum vértice encontrado no arquivo.")
        exit()

    return header, vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos



def validar_grafo(vertices, arestas, arcos):
    for (u, v), _ in arestas:
        if u not in vertices or v not in vertices:
            print(f"Erro: Aresta ({u}, {v}) contém vértices inexistentes.")
            exit()

    for (u, v), _ in arcos:
        if u not in vertices or v not in vertices:
            print(f"Erro: Arco ({u}, {v}) contém vértices inexistentes.")
            exit()

    print("Grafo validado com sucesso.")


def calcular_graus(vertices, arestas, arcos):
    graus = {v: [0, 0, 0] for v in vertices}  # [grau, entrada, saída]

    for (u, v), _ in arestas:
        graus[u][0] += 1
        graus[v][0] += 1

    for (u, v), _ in arcos:
        graus[u][2] += 1  # saída
        graus[v][1] += 1  # entrada

    return tuple((v, tuple(g)) for v, g in graus.items())


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

def imprimir_graus(graus):
    grau_maximo = max(sum(g[1]) for g in graus)
    grau_minimo = min(sum(g[1]) for g in graus)
    print("Grau máximo:", grau_maximo)
    print("Grau mínimo:", grau_minimo)

def quantidade_arcos(grafo):
    arcos = 0
    for u in grafo:
        for v in grafo[u]:
            if u in grafo[v]:
                arcos += 1
    return arcos // 2

def floyd_warshall(vertices, edges, arcs):
    """
    Calcula a matriz de distâncias e predecessores usando Floyd-Warshall,
    considerando custos nas arestas e arcos.
    """
    # Inicializa as matrizes
    dist = {v: {u: float('inf') for u in vertices} for v in vertices}
    pred = {v: {u: None for u in vertices} for v in vertices}

    for v in vertices:
        dist[v][v] = 0

    # Preenche com arestas (não direcionadas)
    for (u, v), dados in edges:
        cost = dados if isinstance(dados, int) else dados[0]
        dist[u][v] = cost
        dist[v][u] = cost
        pred[u][v] = u
        pred[v][u] = v

    # Preenche com arcos (direcionados)
    for (u, v), dados in arcs:
        cost = dados if isinstance(dados, int) else dados[0]
        dist[u][v] = cost
        pred[u][v] = u

    # Algoritmo principal
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]

    return dist, pred


def caminho_medio(vertices, edges, arcs):
    dist, _ = floyd_warshall(vertices, edges, arcs)  #usa o floud warshall para calcular a matriz de distancias
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
    densidade = (num_arestas + num_arcos) / (edges_max + arcs_max)
    return densidade


def calc_diametro(matriz_distancias):#nao estava funcionando pq meu floyd warshall 
   # estava com todas as arrestas e arcos com custo 1,ou seja ignorava oque o read_file retornava
    diametro = 0
    for origem in matriz_distancias:
        for destino in matriz_distancias[origem]:
            d = matriz_distancias[origem][destino]
            if d != float('inf') and origem != destino:
                diametro = max(diametro, d)
    return diametro

def caminho_minimo(matriz_pred, origem, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.insert(0, atual)
        if atual == origem:  
            break
        atual = matriz_pred[origem].get(atual)
    if caminho[0] != origem:  #verifica se é um caminho valido
        return []  # retorna nada se nao tiver caminho
    return caminho

def criar_matriz_predecessores(vertices, arestas, arcos):
    _, predecessores = floyd_warshall(vertices, arestas, arcos)
    return predecessores

def calc_intermediacao(vertices, matriz_pred):
    intermediacao = {v: 0 for v in vertices}

    for origem in vertices:
        for destino in vertices:
            if origem != destino:
                # faz o calc do minimo caminho
                caminho = caminho_minimo(matriz_pred, origem, destino)
                # Verifica se o caminho tem mais de 1 vértice
                if len(caminho) > 1:
                    for v in caminho[1:-1]:
                        intermediacao[v] += 1
    return intermediacao


def clarke_wright(deposito, required_vertices, edges, arcs, capacidade, matriz_pred, matriz_dist):
    from itertools import combinations

    # Mapeamento de demandas
    demandas = {v: dem[0] for v, dem in required_vertices}
    if deposito in demandas:
        demandas.pop(deposito)  # depósito não tem demanda

    # Inicializa rotas individuais
    rotas = {v: [deposito, v, deposito] for v in demandas}

    # Dicionário de custos reais (usando matriz de distâncias)
    custos = {}
    for (u, v), _ in list(edges) + list(arcs):
        custos[(u, v)] = matriz_dist[u][v]
        custos[(v, u)] = matriz_dist[v][u]

    # Savings: quanto se economiza unindo duas rotas
    savings = []
    for i, j in combinations(demandas.keys(), 2):
        ci = matriz_dist[deposito][i]
        cj = matriz_dist[deposito][j]
        cij = matriz_dist[i][j]

        if ci != float('inf') and cj != float('inf') and cij != float('inf'):
            s = ci + cj - cij
            savings.append(((i, j), s))

    savings.sort(key=lambda x: x[1], reverse=True)

    # União das rotas
    for (i, j), _ in savings:
        rota_i = rotas.get(i)
        rota_j = rotas.get(j)

        if not rota_i or not rota_j or rota_i == rota_j:
            continue

        if rota_i[-2] == i and rota_j[1] == j:
            demanda_total = sum(demandas[v] for v in rota_i[1:-1] + rota_j[1:-1])
            if demanda_total <= capacidade:
                nova_rota = rota_i[:-1] + rota_j[1:]
                for v in nova_rota:
                    if v != deposito:
                        rotas[v] = nova_rota

    # Remover duplicatas e manter apenas rotas únicas
    rotas_finais = []
    vistas = set()
    for rota in rotas.values():
        t = tuple(rota)
        if t not in vistas:
            vistas.add(t)
            rotas_finais.append(rota)

    # Caminhos reais e custo total
    custo_total = 0
    rotas_reais = []
    for rota in rotas_finais:
        rota_real = []
        for i in range(len(rota) - 1):
            u, v = rota[i], rota[i+1]
            caminho = caminho_minimo(matriz_pred, u, v)
            if not caminho:
                print(f"⚠️ Sem caminho entre {u} e {v}")
                continue
            if not rota_real:
                rota_real.extend(caminho)
            else:
                rota_real.extend(caminho[1:])
            custo_total += matriz_dist[u][v]
        rotas_reais.append(rota_real)

    return rotas_reais, custo_total


if __name__ == "__main__":

    nome_arquivo = "GrafosDeTeste/" + input("Digite o nome do arquivo/caminho: ").strip()
    resultado = read_file(nome_arquivo)
    

    if resultado is None:
        print("Erro ao carregar o grafo")
        exit()

    header, vertices, edges, arcs, required_vertices, required_edges, key_arcs = resultado
    
    optimalvalue = int(header["Optimal value"])
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])

    if not vertices:
        print("Erro: Grafo vazio.")
        exit()

    grafo = {v: [] for v in vertices}

    for (u, v), _ in edges:
        grafo[u].append(v)
        grafo[v].append(u)

    for (u, v), _ in arcs:
        grafo[u].append(v)

    inicio = next(iter(vertices)) 

    print("-------------------------------------------------------------------------------------------------------------------")
    print("Quantidade de vértices:", quantidade_vertices(grafo))
    print("Quantidade de arestas:", len(edges))
    print("Quantidade de arcos:", quantidade_arcos(grafo))
    print("Quantidade de vértices requeridos:", len(required_vertices))
    print("Quantidade de arestas requeridas:", len(required_edges))
    print("Quantidade de arcos requeridos:", len(key_arcs))
    print("Grau máximo e mínimo:")
    imprimir_graus(calcular_graus(vertices, edges, arcs))
    print("Caminho médio:", round(caminho_medio(vertices, edges, arcs), 2))
    print("Densidade do grafo:", round(calc_densidade(len(edges), len(arcs), len(vertices)), 2))
    matriz_distancias, _ = floyd_warshall(vertices, edges, arcs)
    print("Diâmetro do grafo:", calc_diametro(matriz_distancias))   
    matriz_pred = criar_matriz_predecessores(vertices, edges, arcs)
    print("Intermediação de cada vértice:", calc_intermediacao(vertices, matriz_pred))
    print("-------------------------------------------------------------------------------------------------------------------")


    print("\n------------------ ROTEAMENTO COM CLARKE & WRIGHT ------------------")
    matriz_dist, matriz_pred = floyd_warshall(vertices, edges, arcs)
    rotas, custo_total = clarke_wright(deposito, required_vertices, edges, arcs, capacidade, matriz_pred, matriz_dist)
    for i, rota in enumerate(rotas, 1):
        print(f"Rota {i}: {' → '.join(map(str, rota))}")
    print("Custo total das rotas:", round(custo_total, 2))
