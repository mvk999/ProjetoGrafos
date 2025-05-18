import os
import time
from leitura import read_file, validar_grafo, floyd_warshall, caminho_minimo
from heuristicas import (
    Demanda,
    clarke_wright_completo,
    two_opt,
    remover_repeticoes_consecutivas,
    reconstruir_rota_valida,
    three_opt,
    melhorar_rotas_pelo_servico,
    realocar_rotas_pequenas
)
from metricas import (
    calcular_graus,
    imprimir_graus,
    caminho_medio,
    calc_densidade,
    calc_diametro,
    calc_intermediacao,
)

def calcular_custo_rota(rota, dist, deposito):
    atual = deposito
    custo = 0
    for d in rota:
        custo += dist[atual][d.u] + d.custo
        atual = d.v
    custo += dist[atual][deposito]
    return custo

CPU_GHZ = 3.0
PASTA_ENTRADA = "GrafosDeTeste"
PASTA_SAIDA = "SolucoesGeradas"
os.makedirs(PASTA_SAIDA, exist_ok=True)

arquivos = [arq for arq in os.listdir(PASTA_ENTRADA) if arq.endswith(".dat")]

for nome in arquivos:
    print(f"\n📂 PROCESSANDO: {nome}")
    caminho = os.path.join(PASTA_ENTRADA, nome)

    header, vertices, edges, arcs, req_vertices, req_edges, req_arcs = read_file(caminho)
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, pred = floyd_warshall(vertices, edges, arcs)

    validar_grafo(vertices, edges, arcs)

    # Montar todas as demandas do grafo
    demandas = []
    for (u, v), (custo, demanda, _) in req_edges:
        demandas.append(Demanda(u, v, custo, demanda, "aresta"))
    for (u, v), (custo, demanda, _) in req_arcs:
        demandas.append(Demanda(u, v, custo, demanda, "arco"))
    for v, (demanda, custo) in req_vertices:
        demandas.append(Demanda(v, v, custo, demanda, "vertice"))

    inicio = time.perf_counter_ns()
    rotas_reais, custo_total, rotas_demandas = clarke_wright_completo(demandas, dist, pred, deposito, capacidade)

    if custo_total == float("inf"):
        print("❌ Solução inválida (grafo desconexo)")
        continue

    # 🔁 Fusão com heurística iterativa baseada em economia real
    rotas_demandas = melhorar_rotas_pelo_servico(rotas_demandas, dist, pred, deposito, capacidade)

    # 🔄 Realocar sobras para reduzir rotas pequenas e economizar
    rotas_demandas = realocar_rotas_pequenas(rotas_demandas, capacidade)

    # 🚚 Reconstrução final com 2-opt e 3-opt
    rotas_otimizadas = []
    custo_3opt = 0
    for rota_d in rotas_demandas:
        atual = deposito
        caminho = []
        for d in rota_d:
            trecho = caminho_minimo(pred, atual, d.u)
            if not trecho:
                continue
            caminho += trecho[1:] if caminho else trecho
            caminho.append(d.v)
            atual = d.v
            custo_3opt += dist[trecho[-2]][d.u] + d.custo
        caminho += caminho_minimo(pred, atual, deposito)[1:]
        custo_3opt += dist[atual][deposito]

        rota_2opt = two_opt(caminho, dist)
        rota_3opt = three_opt(rota_2opt, dist)
        rota_final = remover_repeticoes_consecutivas(rota_3opt)
        rotas_otimizadas.append(rota_final)

    fim = time.perf_counter_ns()
    tempo_ns = fim - inicio
    clocks = int(tempo_ns * CPU_GHZ)

    # 📤 Salvar no formato exigido pela banca
    saida_nome = os.path.join(PASTA_SAIDA, f"sol-{os.path.splitext(nome)[0]}-opt.dat")
    with open(saida_nome, "w", encoding="utf-8") as f:
        f.write(f"{round(custo_3opt)}\n")
        f.write(f"{len(rotas_otimizadas)}\n")
        f.write(f"{clocks}\n")
        f.write(f"{clocks}\n")

        id_servico = 1
        for idx, rota in enumerate(rotas_otimizadas):
            demanda_total = 0
            custo_rota = 0
            servicos = []
            for i in range(len(rota) - 1):
                u, v = rota[i], rota[i + 1]
                custo_rota += dist[u][v]
                for d in demandas:
                    if (d.u, d.v) == (u, v) or (d.tipo != "n" and (d.v, d.u) == (u, v)):
                        servicos.append((id_servico, d.u, d.v))
                        demanda_total += d.demanda
                        id_servico += 1
                        break

            f.write(f"0 1 {idx+1} {demanda_total} {round(custo_rota)} {len(servicos)} ")
            f.write("(D 0,1,1) ")
            for sid, u, v in servicos:
                f.write(f"(S {sid},{u},{v}) ")
            f.write("(D 0,1,1)\n")

    # 📊 Diagnóstico
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
    print("✅ Arquivo salvo:", saida_nome)
