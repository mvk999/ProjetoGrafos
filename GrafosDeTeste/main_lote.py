
import os
import time
from leitura import read_file, floyd_warshall
from heuristicas import Demanda, clarke_wright_completo, two_opt, three_opt, remover_repeticoes_consecutivas, reconstruir_rota_valida
from metricas import calcular_graus, imprimir_graus, caminho_medio, calc_densidade, calc_diametro, calc_intermediacao

CPU_GHZ = 3.0  # Ajuste se necessário

def processar_grafo(nome_arquivo):
    header, vertices, edges, arcs, req_vertices, req_edges, req_arcs = read_file(nome_arquivo)
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, pred = floyd_warshall(vertices, edges, arcs)

    demandas = []
    for (u, v), (custo, demanda, _) in req_edges:
        demandas.append(Demanda(u, v, custo, demanda, "aresta"))
    for (u, v), (custo, demanda, _) in req_arcs:
        demandas.append(Demanda(u, v, custo, demanda, "arco"))
    
    return header, vertices, edges, arcs, req_vertices, req_edges, req_arcs, capacidade, deposito, dist, pred, demandas

if __name__ == "__main__":

    inicio_total = time.perf_counter_ns()

    # Processar os arquivos de entrada
    nome_arquivo = input("Digite o nome do arquivo .dat (ex: BHW1.dat): ").strip()
    caminho = nome_arquivo if os.path.isfile(nome_arquivo) else f"/mnt/data/{nome_arquivo}"

    header, vertices, edges, arcs, req_vertices, req_edges, req_arcs, capacidade, deposito, dist, pred, demandas = processar_grafo(caminho)

    # Construir soluções
    inicio_otim = time.perf_counter_ns()
    rotas, custo_total = clarke_wright_completo(demandas, dist, pred, deposito, capacidade)
    fim_otim = time.perf_counter_ns()

    if custo_total == float('inf'):
        print("❌ Não foi possível gerar uma solução viável.")
    else:
        print("
✅ Solução inicial:")
        print("Custo total:", round(custo_total, 2))
        for i, rota in enumerate(rotas, 1):
            print(f"Rota {i}: {' → '.join(map(str, rota))}")

        # Aplicando 2-opt
        print("
🚀 Aplicando 2-opt e reconstruindo rotas reais...")
        rotas_2opt = []
        custo_2opt = 0
        for rota in rotas:
            r_otim = remover_repeticoes_consecutivas(two_opt(rota, dist))
            r_real = reconstruir_rota_valida(r_otim, pred)
            if r_real:
                rotas_2opt.append(r_real)
                for i in range(len(r_real) - 1):
                    custo_2opt += dist[r_real[i]][r_real[i+1]]

        print("✅ Custo após 2-opt:", round(custo_2opt, 2))
        for i, rota in enumerate(rotas_2opt, 1):
            print(f"Rota {i}: {' → '.join(map(str, rota))}")

        # Salvar saída
        nome_saida = f"/mnt/data/sol-{os.path.splitext(nome_arquivo)[0]}-opt.dat"
        with open(nome_saida, "w") as f:
            f.write(f"Cost {round(custo_2opt, 2)}
")
            for i, rota in enumerate(rotas_2opt, 1):
                f.write(f"Route {i}: {' '.join(map(str, rota))}
")
        print(f"📁 Arquivo salvo: {nome_saida}")

    fim_total = time.perf_counter_ns()
    print(f"⏱️ Tempo total: {fim_total - inicio_total} ns (~{int((fim_total - inicio_total)*CPU_GHZ)} clocks)")
    print(f"⏱️ Tempo de solução: {fim_otim - inicio_otim} ns (~{int((fim_otim - inicio_otim)*CPU_GHZ)} clocks)")

    # Comparar com 3-opt
    print("
🔥 Aplicando 3-opt em cada rota...")
    inicio_3opt = time.perf_counter_ns()

    rotas_3opt = []
    custo_3opt = 0

    for rota in rotas:
        # Etapa 1: aplicar 3-opt na rota original
        rota_3 = remover_repeticoes_consecutivas(three_opt(rota, dist))

        # Etapa 2: reconstruir caminho real válido
        rota_real_3 = reconstruir_rota_valida(rota_3, pred)

        if rota_real_3:
            rotas_3opt.append(rota_real_3)
            for i in range(len(rota_real_3) - 1):
                custo_3opt += dist[rota_real_3[i]][rota_real_3[i+1]]

    fim_3opt = time.perf_counter_ns()
    tempo_3opt_ns = fim_3opt - inicio_3opt
    clocks_3opt = int(tempo_3opt_ns * CPU_GHZ)

    # Exibir os resultados
    print("✅ Custo após 3-opt:", round(custo_3opt, 2))
    for i, rota in enumerate(rotas_3opt, 1):
        print(f"Rota {i}: {' → '.join(map(str, rota))}")
    print(f"⏱️ Tempo 3-opt: {tempo_3opt_ns} ns (~{clocks_3opt} clocks @ {CPU_GHZ}GHz)")
