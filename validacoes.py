from leitura import read_file, floyd_warshall
from heuristicas import Demanda

def extrair_servicos_requeridos(req_vertices, req_edges, req_arcs):
    servicos = set()
    for v, _ in req_vertices:
        servicos.add(("n", v, v))
    for (u, v), _ in req_edges:
        servicos.add(("e", min(u, v), max(u, v)))
    for (u, v), _ in req_arcs:
        servicos.add(("a", u, v))
    return servicos

def identificar_servico(tipo, u, v):
    if tipo == "n":
        return ("n", u, u)
    elif tipo == "e":
        return ("e", min(u, v), max(u, v))
    elif tipo == "a":
        return ("a", u, v)

def validar_solucao(nome_instancia, caminho_instancia, caminho_solucao):
    header, vertices, edges, arcs, req_vertices, req_edges, req_arcs = read_file(caminho_instancia)
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])

    dist, _ = floyd_warshall(vertices, edges, arcs)
    servicos_esperados = extrair_servicos_requeridos(req_vertices, req_edges, req_arcs)
    servicos_encontrados = set()

    with open(caminho_solucao, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    rotas = [linha for linha in linhas if linha.startswith("Route")]

    for linha in rotas:
        partes = linha.strip().split(":")[1].strip().split()
        caminho = list(map(int, partes))
        carga_rota = 0

        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            if u == v:
                tipo = "n"
            elif (u, v) in arcs:
                tipo = "a"
            elif (v, u) in arcs:
                tipo = "a"
                u, v = v, u
            elif (min(u, v), max(u, v)) in [a[0] for a in req_edges]:
                tipo = "e"
                u, v = min(u, v), max(u, v)
            else:
                continue  # Caminho de trânsito

            servico = identificar_servico(tipo, u, v)
            if servico in servicos_encontrados:
                print(f"⚠️ Serviço repetido: {servico}")
            else:
                servicos_encontrados.add(servico)

            if tipo == "n":
                demanda = dict(req_vertices).get(u, (0,))[0]
            elif tipo == "e":
                demanda = dict(req_edges).get((u, v), (0,))[1]
            else:
                demanda = dict(req_arcs).get((u, v), (0,))[1]

            carga_rota += demanda

        if carga_rota > capacidade:
            print(f"❌ Rota com excesso de carga (capacidade {capacidade}, carga {carga_rota})")

    if servicos_esperados == servicos_encontrados:
        print(f"✅ Solução válida para {nome_instancia} (todos serviços cobertos sem repetições)")
    else:
        faltando = servicos_esperados - servicos_encontrados
        extras = servicos_encontrados - servicos_esperados
        if faltando:
            print(f"❌ Faltando serviços: {faltando}")
        if extras:
            print(f"⚠️ Serviços extras inesperados: {extras}")