import os
import time
from leitura import read_file, validar_grafo, floyd_warshall, caminho_minimo
from heuristicas import Demanda, clarke_wright_completo, two_opt, remover_repeticoes_consecutivas, reconstruir_rota_valida, three_opt
from metricas import calcular_graus, imprimir_graus, caminho_medio, calc_densidade, calc_diametro, calc_intermediacao

CPU_GHZ = 3.0  # Ajuste se necessário

if __name__ == "__main__":

    inicio_total = time.perf_counter_ns()


CPU_GHZ = 3.0
PASTA_ENTRADA = "GrafosDeTeste"
PASTA_SAIDA = "SolucoesGeradas"
os.makedirs(PASTA_SAIDA, exist_ok=True)

arquivos = [arq for arq in os.listdir(PASTA_ENTRADA) if arq.endswith(".dat")]

for nome in arquivos:
    total_rotas = 0
    print(f"\n📂 PROCESSANDO: {nome}")
    caminho = os.path.join(PASTA_ENTRADA, nome)

    header, vertices, edges, arcs, req_vertices, req_edges, req_arcs = read_file(caminho)
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, pred = floyd_warshall(vertices, edges, arcs)

    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, pred = floyd_warshall(vertices, edges, arcs)

    # Montar demandas
    demandas = []
    for (u, v), (custo, demanda, _) in req_edges:
        demandas.append(Demanda(u, v, custo, demanda, "aresta"))
    for (u, v), (custo, demanda, _) in req_arcs:
        demandas.append(Demanda(u, v, custo, demanda, "arco"))

    inicio = time.perf_counter_ns()
    rotas, custo_total = clarke_wright_completo(demandas, dist, pred, deposito, capacidade)
    

    if custo_total == float("inf"):
        print("❌ Solução inválida (grafo desconexo)")
        continue

    rotas_3opt = []
    custo_3opt = 0
    for rota in rotas:
        r3 = remover_repeticoes_consecutivas(three_opt(rota, dist))
        r3_real = reconstruir_rota_valida(r3, pred)
        if r3_real:
            rotas_3opt.append(r3_real)
            for i in range(len(r3_real) - 1):
                custo_3opt += dist[r3_real[i]][r3_real[i + 1]]
                

    fim = time.perf_counter_ns()
    tempo_ns = fim - inicio
    clocks = int(tempo_ns * CPU_GHZ)

    # Salvar saída
    saida_nome = os.path.join(PASTA_SAIDA, f"sol-{os.path.splitext(nome)[0]}-opt.dat")
    with open(saida_nome, "w", encoding="utf-8") as f:
        header, vertices, edges, arcs, req_vertices, req_edges, req_arcs = read_file(caminho)
        capacidade = int(header["Capacity"])
        deposito = int(header["Depot Node"])
        dist, pred = floyd_warshall(vertices, edges, arcs)

        print("------------------------------------------------------------------")
        print("Quantidade de vértices:", len(vertices))
        print("Quantidade de arestas:", len(edges))
        print("Quantidade de arcos:", len(arcs))
        print("Quantidade de vértices requeridos:", len(req_vertices))
        print("Quantidade de arestas requeridas:", len(req_edges))
        print("Quantidade de arcos requeridos:", len(req_arcs))

        graus = calcular_graus(vertices, edges, arcs)
        imprimir_graus(graus)
        print("Caminho médio:", round(caminho_medio(vertices, edges, arcs), 2))
        print("Densidade do grafo:", round(calc_densidade(len(edges), len(arcs), len(vertices)), 4))
        print("Diâmetro:", calc_diametro(dist))

        for i, rota in enumerate(rotas_3opt, 1):
            total_rotas += 1
        
        f.write(f"Custo total da solução: {round(custo_3opt, 2)}\n")
        f.write(f"Total de rotas: {total_rotas}\n")
        f.write(f"⏱️ Tempo total: {tempo_ns} ns\n")
        f.write(f"clocks totais do algoritimo referência: {clocks} clocks\n")
        for i, rota in enumerate(rotas_3opt, 1):
            f.write(f"Route {i}: {' '.join(map(str, rota))}\n")