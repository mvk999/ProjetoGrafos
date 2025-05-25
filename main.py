import os
import time
import math
from pathlib import Path
from leitura import read_and_extract, floyd_warshall
from heuristicas import algoritmo_clarke_wright, salvar_solucao,grasp_clarke_wright

CPU_GHZ = 3.0
PASTA_GABARITO = "SolucoesEsperadas"
PASTA_ENTRADA = "GrafosDeTeste"
PASTA_SAIDA = "SolucoesGeradas"
os.makedirs(PASTA_SAIDA, exist_ok=True)

arquivos = sorted(f for f in os.listdir(PASTA_ENTRADA) if f.endswith(".dat"))

def analisar_estatisticas(pasta_solucoes, pasta_gabaritos):
    total_custo_aceito = 0
    total_rotas_iguais = 0
    total_custo_e_rotas_iguais = 0
    alertas_custo_menor = 0
    alertas_rotas_menor = 0

    arquivos_solucao = list(Path(pasta_solucoes).glob("*.txt"))

    for arq_solucao in arquivos_solucao:
        nome = arq_solucao.name
        arq_gabarito = Path(pasta_gabaritos) / nome
        if not arq_gabarito.exists():
            continue

        with open(arq_solucao, 'r', encoding='utf-8') as f:
            linhas_sol = f.readlines()
        with open(arq_gabarito, 'r', encoding='utf-8') as f:
            linhas_gab = f.readlines()

        custo_sol = int(linhas_sol[0])
        rotas_sol = int(linhas_sol[1])
        custo_gab = int(linhas_gab[0])
        rotas_gab = int(linhas_gab[1])

        custo_aceito = custo_sol <= custo_gab
        rotas_iguais = rotas_sol == rotas_gab

        if custo_sol < custo_gab:
            alertas_custo_menor += 1
        if rotas_sol < rotas_gab:
            alertas_rotas_menor += 1
        if custo_aceito:
            total_custo_aceito += 1
        if rotas_iguais:
            total_rotas_iguais += 1
        if custo_aceito and rotas_iguais:
            total_custo_e_rotas_iguais += 1

    print("\n# Estatísticas gerais da execução:")
    print(f"# Total de arquivos com custo_aceito=True e rotas_iguais=True: {total_custo_e_rotas_iguais}")
    print(f"# Total de arquivos com custo_aceito=True: {total_custo_aceito}")
    print(f"# Total de arquivos com rotas_iguais=True: {total_rotas_iguais}")
    print(f"# Total de ALERTAS de custo menor: {alertas_custo_menor}")
    print(f"# Total de ALERTAS de número de rotas menor: {alertas_rotas_menor}")

for nome in arquivos:
    print(f"\n📂 PROCESSANDO: {nome}")
    caminho = os.path.join(PASTA_ENTRADA, nome)

    header, vertices, edges, arcs, req_v, req_e, req_a, id_v, id_ea = read_and_extract(caminho)
    capacidade = int(header["Capacity"])
    deposito = int(header["Depot Node"])
    dist, _ = floyd_warshall(vertices, edges, arcs)

    servicos = []
    id_serv = 1

for v, (demanda, custo_servico) in req_v:
    servicos.append({
        'tipo': 'n',
        'id_servico': id_serv,
        'origem': v,
        'destino': v,
        'demanda': demanda,
        'custo_servico': custo_servico
    })
    id_serv += 1

for (u, v), dados in req_e:
    custo_transporte, demanda, custo_servico = dados
    servicos.append({
        'tipo': 'e',
        'id_servico': id_serv,
        'origem': u,
        'destino': v,
        'demanda': demanda,
        'custo_servico': custo_servico
    })
    id_serv += 1

for (u, v), dados in req_a:
    custo_transporte, demanda, custo_servico = dados
    servicos.append({
        'tipo': 'a',
        'id_servico': id_serv,
        'origem': u,
        'destino': v,
        'demanda': demanda,
        'custo_servico': custo_servico
    })
    id_serv += 1

    nome_gabarito = os.path.join(PASTA_GABARITO, f"sol-{os.path.splitext(nome)[0]}.dat")
    if os.path.exists(nome_gabarito):
        with open(nome_gabarito, "r", encoding="utf-8") as gabarito:
            linhas = gabarito.readlines()
            try:
                custo_esperado = int(linhas[0].strip())
                rotas_esperadas = int(linhas[1].strip())
            except (ValueError, IndexError):
                custo_esperado = None
                rotas_esperadas = None
    else:
        custo_esperado = None
        rotas_esperadas = None

    inicio = time.perf_counter_ns()
    rotas = grasp_clarke_wright(servicos, deposito, dist, capacidade)
    fim = time.perf_counter_ns()

    if not rotas:
        print("❌ Solução inválida.")
        continue

    tempo_ns = fim - inicio
    clocks = int(tempo_ns * CPU_GHZ)
    timestamp = int(time.time())

    saida_nome = os.path.join(PASTA_SAIDA, f"sol-{os.path.splitext(nome)[0]}.txt")
    salvar_solucao(
        nome_arquivo=saida_nome,
        rotas=rotas,
        matriz_distancias=dist,
        deposito=deposito,
        tempo_referencia_execucao=clocks,
        tempo_referencia_solucao=timestamp
    )

    print("✅ Arquivo gerado:", saida_nome)

    print("\n📌 Comparação com GABARITO G0:")
    if custo_esperado != float('inf'):
        print(f"🔸 Custo gerado:   {round(sum(int(linhas.split()[4]) for linhas in open(saida_nome).readlines()[4:]))}")
        print(f"🔸 Custo esperado: {custo_esperado}")
        print(f"🔸 Diferença:      {round(sum(int(linhas.split()[4]) for linhas in open(saida_nome).readlines()[4:])) - custo_esperado}")
    else:
        print("❗ Gabarito não encontrado para comparar custos.")

    if rotas_esperadas is not None:
        print(f"🔹 Rotas geradas:   {len(rotas)}")
        print(f"🔹 Rotas esperadas: {rotas_esperadas}")
        print(f"🔹 Diferença:       {len(rotas) - rotas_esperadas}")
    else:
        print("❗ Gabarito não encontrado para comparar número de rotas.")

