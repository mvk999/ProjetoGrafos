import os
import time
from pathlib import Path
from leitura import read_and_extract
from heuristicas import construir_matriz_dist as gerar_matriz_dist, construir_matriz_preds as gerar_matriz_preds
from heuristicas import clarke_wright_controller as executar_clarke_wright, custo_rota_individual as avaliar_rota

CPU_GIGAHERTZ = 3.0
DIR_REFERENCIA = "SolucoesEsperadas"
DIR_ENTRADA = "GrafosDeTeste"
DIR_RESULTADOS = "SolucoesGeradas"
os.makedirs(DIR_RESULTADOS, exist_ok=True)

instancias_dat = sorted(arq for arq in os.listdir(DIR_ENTRADA) if arq.endswith(".dat"))

def gerar_relatorio_geral(pasta_saida, pasta_base):
    aceito = igual = perfeitos = melhor_custo = menos_rotas = 0
    arquivos_gerados = list(Path(pasta_saida).glob("*.txt"))

    for arq in arquivos_gerados:
        nome_arq = arq.name
        esperado = Path(pasta_base) / nome_arq
        if not esperado.exists():
            continue

        with open(arq, 'r', encoding='utf-8') as g1:
            linhas_geradas = g1.readlines()
        with open(esperado, 'r', encoding='utf-8') as g2:
            linhas_base = g2.readlines()

        custo_atual = int(linhas_geradas[0])
        rotas_atual = int(linhas_geradas[1])
        custo_base = int(linhas_base[0])
        rotas_base = int(linhas_base[1])

        if custo_atual <= custo_base:
            aceito += 1
        if rotas_atual == rotas_base:
            igual += 1
        if custo_atual < custo_base:
            melhor_custo += 1
        if rotas_atual < rotas_base:
            menos_rotas += 1
        if custo_atual <= custo_base and rotas_atual == rotas_base:
            perfeitos += 1

    print("\n📊 Resumo das Execuções:")
    print(f"✔️ Perfeitas (custo e rotas): {perfeitos}")
    print(f"✔️ Custo aceitável: {aceito}")
    print(f"✔️ Rotas corretas: {igual}")
    print(f"⚠️ Custo melhorado: {melhor_custo}")
    print(f"⚠️ Menos rotas: {menos_rotas}")

for arquivo in instancias_dat:
    print(f"\n📁 LENDO INSTÂNCIA: {arquivo}")
    caminho_arquivo = os.path.join(DIR_ENTRADA, arquivo)
    cabecalho, nos, arestas, arcos, obrigatorios_v, obrigatorios_e, obrigatorios_a, _, _ = read_and_extract(caminho_arquivo)
    capacidade_veiculo = int(cabecalho["Capacity"])
    ponto_base = int(cabecalho["Depot Node"])

    matriz_dist = gerar_matriz_dist(nos, arestas, arcos)
    matriz_pred = gerar_matriz_preds(nos, arestas, arcos)

    caminho_ref = os.path.join(DIR_REFERENCIA, f"sol-{os.path.splitext(arquivo)[0]}.dat")
    if os.path.exists(caminho_ref):
        with open(caminho_ref, "r", encoding="utf-8") as ref:
            linhas = ref.readlines()
            try:
                custo_ref = int(linhas[0].strip())
                rotas_ref = int(linhas[1].strip())
            except:
                custo_ref = rotas_ref = None
    else:
        custo_ref = rotas_ref = None

    inicio_clk = time.perf_counter_ns()
    rotas_geradas, tarefas_geradas = executar_clarke_wright(
        arestas_obrig=obrigatorios_e,
        arcos_obrig=obrigatorios_a,
        vertices_obrig=obrigatorios_v,
        deposito=ponto_base,
        num_veiculos=-1,
        capacidade=capacidade_veiculo,
        matriz_dist=matriz_dist,
        matriz_preds=matriz_pred,
        seed=None,
        embaralhar=True
    )
    fim_clk = time.perf_counter_ns()

    if not rotas_geradas:
        print("❌ Nenhuma rota válida encontrada.")
        continue

    duracao_ns = fim_clk - inicio_clk
    ciclos_clk = int(duracao_ns * CPU_GIGAHERTZ)
    timestamp_exec = int(time.time())
    custo_total_rotas = sum(avaliar_rota(rota, tarefas_geradas, matriz_dist) for rota in rotas_geradas)

    nome_saida = os.path.join(DIR_RESULTADOS, f"sol-{os.path.splitext(arquivo)[0]}.txt")
    with open(nome_saida, "w", encoding="utf-8") as saida:
        saida.write(f"{custo_total_rotas}\n{len(rotas_geradas)}\n{ciclos_clk}\n{timestamp_exec}\n")
        for idr, rota in enumerate(rotas_geradas, 1):
            custo_atual = avaliar_rota(rota, tarefas_geradas, matriz_dist)
            linha = f"0 1 {idr} {rota['demanda']} {custo_atual} {len(rota['tarefas'])+2} (D {ponto_base},1,1)"
            for tid in rota['tarefas']:
                t = tarefas_geradas[tid]
                linha += f" (S {t['id']},{t['origem']},{t['destino']})"
            linha += f" (D {ponto_base},1,1)"
            saida.write(linha + "\n")
      
    print("✅ Resultado salvo:", nome_saida)
    if custo_ref is not None:
        print(f"\n📌 Avaliação de Custo:")
        print(f"🔸 Encontrado: {custo_total_rotas}")
        print(f"🔸 Esperado:  {custo_ref}")
        print(f"🔸 Diferença: {custo_total_rotas - custo_ref}")
    else:
        print("❗ Nenhum gabarito de custo disponível.")

    if rotas_ref is not None:
        print(f"🔹 Rotas geradas:   {len(rotas_geradas)}")
        print(f"🔹 Rotas esperadas: {rotas_ref}")
        print(f"🔹 Diferença:       {len(rotas_geradas) - rotas_ref}")
    else:
        print("❗ Nenhum gabarito de rotas disponível.")
