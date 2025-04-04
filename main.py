#Inicio do projeto de grafos

class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []  # Arestas não direcionadas: cada uma é uma tupla (u, v, custo)
        self.arcs = []   # Arcos direcionados: cada um é uma tupla (u, v, custo)

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_edge(self, u, v, cost):
        self.edges.append((u, v, cost))

    def add_arc(self, u, v, cost):
        self.arcs.append((u, v, cost)) #aprender como tratar esses arcos,sla como faz

    def print_stats(self):
        print("Quantidade de vértices:", len(self.vertices))
        print("Quantidade de arestas:", len(self.edges))
        print("Quantidade de arcos:", len(self.arcs))

#Algoritimo para fazer a busca e poder ler o grafo
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
#Inicio para realizar o tratamento de dados dos grafos
def quantidade_vertices(grafo):
    return len(grafo)

def quantidade_arestas(grafo):
    return sum(len(vizinhos) for vizinhos in grafo.values()) // 2

def grau_minimo(grafo):
    return min(len(vizinhos) for vizinhos in grafo.values())

def grau_maximo(grafo):
    return max(len(vizinhos) for vizinhos in grafo.values())

def componentes_conectados(grafo):
    visitados = set()
    componentes = []
    
    for vertice in grafo:
        if vertice not in visitados:
            componente = bfs(grafo, vertice)
            componentes.append(componente)
            visitados.update(componente)
    
    return componentes

# Entrada do usuário
grafo = {}
n = int(input("Digite o número de arestas: "))
for _ in range(n):
    u, v = input("Digite a aresta (u v): ").split()
    if u not in grafo:
        grafo[u] = []
    if v not in grafo:
        grafo[v] = []
    grafo[u].append(v)
    grafo[v].append(u)  # Remova esta linha se o grafo for direcionado

inicio = input("Digite o vértice inicial: ")
print("Ordem de visitação:", bfs(grafo, inicio))
print("Quantidade de vértices:", quantidade_vertices(grafo))
print("Quantidade de arestas:", quantidade_arestas(grafo))
print("Grau mínimo:", grau_minimo(grafo))
print("Grau máximo:", grau_maximo(grafo))
print("Componentes conectados:", componentes_conectados(grafo))


# Entrada do usuário
grafo = {}
n = int(input("Digite o número de arestas: "))
for _ in range(n):
    u, v = input("Digite a aresta (u v): ").split()
    if u not in grafo:
        grafo[u] = []
    if v not in grafo:
        grafo[v] = []
    grafo[u].append(v)
    grafo[v].append(u)  # preciso tratar caso seja direcionado

inicio = input("Digite o vértice inicial: ")
print("Ordem de visitação:", bfs(grafo, inicio)) # para saber se o algoritimo esta funcionando

if __name__ == "__main__":
    graph = Graph()
    bfs(grafo,inicio)
    grau_maximo(grafo)
    grau_minimo(grafo)
