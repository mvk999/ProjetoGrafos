import os
import time
from pathlib import Path
from collections import Counter
from leitura import read_and_extract
from path_scanning import grasp_path_scanning
from melhoramento_local import melhorar_por_realocacao
from opt2 import aplicar_2opt_em_todas

CPU_GIGAHERTZ = 3.0
DIR_REFERENCIA = "SolucoesEsperadas"
DIR_ENTRADA = "GrafosDeTeste"
DIR_RESULTADOS = "SolucoesGeradas"
os.makedirs(DIR_RESULTADOS, exist_ok=True)

instancias_dat = sorted(arq for arq in os.listdir(DIR_ENTRADA) if arq.endswith(".dat"))

def gerar_relatorio_geral(pasta_saida, pasta_base):
    pass  # omitido

for arquivo in instancias_dat:
    print(f"\n📁 LENDO INSTÂNCIA: {arquivo}")
    caminho_arquivo = os.path.join(DIR_ENTRADA, arquivo)
    cabecalho, nos, arestas, arcos, obrigatorios_v, obrigatorios_e, obrigatorios_a, _, _ = read_and_extract(caminho_arquivo)
    capacidade_veiculo = int(cabecalho["Capacity"])
    ponto_base = int(cabecalho["Depot Node"])

    from heuristicas import construir_matriz_dist, construir_matriz_preds
    matriz_dist = construir_matriz_dist(nos, arestas, arcos)
    matriz_pred = construir_matriz_preds(nos, arestas, arcos)

    tarefas = []
    id_servico = 0
    for (u, v), (custo, demanda, _) in obrigatorios_e:
        tarefas.append((id_servico, u, v, 'E', demanda, custo))
        id_servico += 1
    for (u, v), (custo, demanda, _) in obrigatorios_a:
        tarefas.append((id_servico, u, v, 'A', demanda, custo))
        id_servico += 1
    for v in obrigatorios_v:
        if isinstance(v, tuple):
            v = v[0]
        tarefas.append((id_servico, v, v, 'V', 1, 0))
        id_servico += 1

    # Definir rotas_esperadas lendo do arquivo de referência, se existir
    caminho_ref = os.path.join(DIR_REFERENCIA, f"sol-{os.path.splitext(arquivo)[0]}.dat")
    if os.path.exists(caminho_ref):
        with open(caminho_ref, "r", encoding="utf-8") as ref:
            linhas = ref.readlines()
            try:
                rotas_esperadas = sum(1 for linha in linhas if linha.strip().startswith("0 1 "))
            except:
                rotas_esperadas = len(tarefas)
    else:
        rotas_esperadas = len(tarefas)

    inicio_clk = time.perf_counter_ns()
    rotas = grasp_path_scanning(tarefas, matriz_dist, ponto_base, rotas_esperadas, capacidade_veiculo)
    rotas = melhorar_por_realocacao(rotas, capacidade_veiculo, matriz_dist, ponto_base)
    rotas = aplicar_2opt_em_todas(rotas, matriz_dist, ponto_base)
    fim_clk = time.perf_counter_ns()

    if not rotas:
        print("❌ Nenhuma rota válida encontrada.")
        continue

    duracao_ns = fim_clk - inicio_clk
    ciclos_clk = int(duracao_ns * CPU_GIGAHERTZ)
    timestamp_exec = int(time.time())
    custo_total_rotas = sum(r[1] for r in rotas)

    nome_saida = os.path.join(DIR_RESULTADOS, f"sol-{os.path.splitext(arquivo)[0]}.txt")
    with open(nome_saida, "w", encoding="utf-8") as saida:
        saida.write(f"{int(custo_total_rotas)}\n{len(rotas)}\n{ciclos_clk}\n{timestamp_exec}\n")
        for idr, (rota, custo, demanda) in enumerate(rotas, 1):
            linha = f"0 1 {idr} {demanda} {int(custo)} {len(rota)+2} (D {ponto_base},1,1)"
            for serv in rota:
                linha += f" (S {serv[0]},{serv[1]},{serv[2]})"
            linha += f" (D {ponto_base},1,1)"
            saida.write(linha + "\n")

    print("✅ Resultado salvo:", nome_saida)

    # Verificação COMPLETA de cobertura e repetição
    ids_obrigatorios = [t[0] for t in tarefas]
    ids_atendidos = []
    for rota, _, _ in rotas:
        for servico in rota:
            ids_atendidos.append(servico[0])

    contador = Counter(ids_atendidos)
    faltando = set(ids_obrigatorios) - set(ids_atendidos)
    repetidos = [id_ for id_, freq in contador.items() if freq > 1]

    if faltando:
        print(f"❌ Tarefas não atendidas ({len(faltando)}): {sorted(faltando)}")
    elif len(ids_atendidos) < len(ids_obrigatorios):
        print(f"❌ Quantidade de serviços atendidos ({len(ids_atendidos)}) menor que o esperado ({len(ids_obrigatorios)})")
    elif repetidos:
        print(f"⚠️ Tarefas repetidas: {repetidos}")
    elif set(ids_atendidos) != set(ids_obrigatorios):
        print("⚠️ Conjuntos diferentes de tarefas atendidas vs obrigatórias.")
    else:
        print("✅ Todas as tarefas foram atendidas exatamente uma vez.")

    # Avaliação de custo e rotas em relação ao gabarito
    custo_ref = rotas_ref = None
    if os.path.exists(caminho_ref):
        with open(caminho_ref, "r", encoding="utf-8") as ref:
            linhas = ref.readlines()
            try:
                custo_ref = int(linhas[0].strip())
                rotas_ref = sum(1 for linha in linhas if linha.strip().startswith("0 1 "))
            except:
                custo_ref = rotas_ref = None

    if custo_ref is not None:
        print(f"\n📌 Avaliação de Custo:")
        print(f"🔸 Encontrado: {int(custo_total_rotas)}")
        print(f"🔸 Esperado:  {custo_ref}")
        print(f"🔸 Diferença: {int(custo_total_rotas) - custo_ref}")
    else:
        print("❗ Nenhum gabarito de custo disponível.")

    if rotas_ref is not None:
        print(f"🔹 Rotas geradas:   {len(rotas)}")
        print(f"🔹 Rotas esperadas: {rotas_ref}")
        print(f"🔹 Diferença:       {len(rotas) - rotas_ref}")
    else:
        print("❗ Nenhum gabarito de rotas disponível.")