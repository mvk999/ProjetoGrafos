import os
import time
from leitura import read_and_extract, floyd_warshall, caminho_minimo
from heuristicas import (
    Demanda,
    clarke_wright_completo,
    melhorar_rotas_pelo_servico,
    realocar_rotas_pequenas,
    two_opt,
    three_opt,
    reconstruir_rota_valida,
    remover_repeticoes_consecutivas,
)
from metricas import (
    calcular_graus,
    imprimir_graus,
    caminho_medio,
    calc_densidade,
    calc_diametro,
)

CPU_GHZ = 3.0
PASTA_GABARITO = "SolucoesEsperadas"
PASTA_ENTRADA = "GrafosDeTeste"
PASTA_SAIDA = "SolucoesGeradas"
os.makedirs(PASTA_SAIDA, exist_ok=True)

arquivos = [f for f in os.listdir(PASTA_ENTRADA) if f.endswith(".dat")]

for nome in sorted(arquivos):
    print(f"\n📂 PROCESSANDO: {nome}")
    caminho = os.path.join(PASTA_ENTRADA, nome)
    header, vertices, edges, arcs, req_v, req_e, req_a, id_v, id_ea = read_and_extract(caminho)

    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, pred = floyd_warshall(vertices, edges, arcs)

    # 📦 Monta lista de demandas
    demandas = []
    for (u, v), (custo, demanda, servico) in req_e:
        demandas.append(Demanda(u, v, servico, demanda, "aresta", id_ea[((u, v), (custo, demanda, servico))]))
    for (u, v), (custo, demanda, servico) in req_a:
        demandas.append(Demanda(u, v, servico, demanda, "arco", id_ea[((u, v), (custo, demanda, servico))]))
    for v, (demanda, servico) in req_v:
        demandas.append(Demanda(v, v, servico, demanda, "vertice", id_v[(v, (demanda, servico))]))

    inicio = time.perf_counter_ns()

    # 🧠 Heurística construtiva
    rotas_reais, custo_inicial, rotas_demandas = clarke_wright_completo(demandas, dist, pred, deposito, capacidade)
    if custo_inicial == float("inf"):
        print("❌ Solução inválida.")
        continue

    rotas_demandas = melhorar_rotas_pelo_servico(rotas_demandas, dist, pred, deposito, capacidade)
    rotas_demandas = realocar_rotas_pequenas(rotas_demandas, capacidade)

    # 🛠️ Refinamento e reconstrução final
    rotas_otimizadas = []
    custo_final = 0
    for rota_d in rotas_demandas:
        atual = deposito
        caminho = []
        for d in rota_d:
            trecho = caminho_minimo(pred, atual, d.u)
            if not trecho: continue
            caminho += trecho[1:] if caminho else trecho
            caminho.append(d.v)
            atual = d.v
            custo_final += dist[trecho[-2]][d.u] + d.custo
        caminho += caminho_minimo(pred, atual, deposito)[1:]
        custo_final += dist[atual][deposito]

        caminho = remover_repeticoes_consecutivas(caminho)
        caminho = two_opt(caminho, dist)
        caminho = three_opt(caminho, dist)
        caminho = remover_repeticoes_consecutivas(caminho)
        rotas_otimizadas.append(caminho)

    fim = time.perf_counter_ns()
    tempo_ns = fim - inicio
    clocks = int(tempo_ns * CPU_GHZ)

    # 💾 Gerar arquivo final no formato G0
    saida_nome = os.path.join(PASTA_SAIDA, f"sol-{os.path.splitext(nome)[0]}-opt.dat")
    with open(saida_nome, "w", encoding="utf-8") as f:
        f.write(f"{round(custo_final)}\n")
        f.write(f"{len(rotas_otimizadas)}\n")
        f.write(f"{clocks}\n")
        f.write(f"{clocks}\n")

        id_global = 1
        for idx, rota in enumerate(rotas_otimizadas):
            servicos = []
            demanda_total = 0
            custo_rota = 0

            for i in range(len(rota) - 1):
                u, v = rota[i], rota[i + 1]
                custo_rota += dist[u][v]
                for d in demandas:
                    if (d.u, d.v) == (u, v) or (d.tipo != "vertice" and (d.v, d.u) == (u, v)) or (d.tipo == "vertice" and d.u == u == v):
                        if (d.id, d.u, d.v) not in servicos:
                            servicos.append((d.id, d.u, d.v))
                            demanda_total += d.demanda
                        break

            f.write(f"0 1 {idx + 1} {demanda_total} {round(custo_rota)} {len(servicos)} ")
            f.write("(D 0,1,1) ")
            for sid, u, v in servicos:
                f.write(f"(S {sid},{u},{v}) ")
            f.write("(D 0,1,1)\n")

    # 📊 Diagnóstico
    print("------------------------------------------------------------------")
    print("Qtd vértices:", len(vertices))
    print("Qtd arestas:", len(edges))
    print("Qtd arcos:", len(arcs))
    print("Serviços:", len(demandas))
    print("✅ Arquivo gerado:", saida_nome)

    # 📌 Comparação com Gabarito
    nome_gabarito = os.path.join(PASTA_GABARITO, f"sol-{os.path.splitext(nome)[0]}.dat")
    if os.path.exists(nome_gabarito):
        with open(nome_gabarito, "r", encoding="utf-8") as gabarito:
            linhas = gabarito.readlines()
            try:
                custo_esperado = int(linhas[0].strip())
                rotas_esperadas = int(linhas[1].strip())
            except ValueError:
                custo_esperado = rotas_esperadas = None
    else:
        custo_esperado = rotas_esperadas = None

    print("\n📌 Comparação com GABARITO G0:")
    if custo_esperado is not None:
        print(f"🔸 Custo gerado:   {round(custo_final)}")
        print(f"🔸 Custo esperado: {custo_esperado}")
        print(f"🔸 Diferença:      {round(custo_final - custo_esperado)}")
    else:
        print("❗ Gabarito não encontrado para comparar custos.")

    if rotas_esperadas is not None:
        print(f"🔹 Rotas geradas:   {len(rotas_otimizadas)}")
        print(f"🔹 Rotas esperadas: {rotas_esperadas}")
        print(f"🔹 Diferença:       {len(rotas_otimizadas) - rotas_esperadas}")
    else:
        print("❗ Gabarito não encontrado para comparar número de rotas.")
