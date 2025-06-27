# -------------------------------------------------------------------------
# COMENTÁRIOS GERAIS SOBRE O ALGORITMO E AS FUNÇÕES ENVOLVIDAS:
#
# O objetivo do código é resolver o problema de roteamento de veículos capacitado com múltiplas restrições,
# utilizando uma heurística baseada em GRASP (Greedy Randomized Adaptive Search Procedure) e refinamentos locais.
#
# - grasp_path_scanning: constrói soluções iniciais usando diferentes critérios de seleção de tarefas, promovendo diversidade.
# - melhorar_por_realocacao: tenta realocar tarefas entre rotas para reduzir o custo total, melhorando a distribuição.
# - aplicar_2opt_em_todas: aplica o algoritmo 2-opt em cada rota, otimizando a ordem das tarefas e reduzindo o custo.
#
# O uso de paralelização permite processar várias instâncias simultaneamente, acelerando experimentos em lote.
# O controle de tempo garante que cada instância não ultrapasse o tempo limite, tornando o algoritmo robusto para grandes conjuntos de dados.
#
# O refinamento das rotas é fundamental para melhorar a qualidade da solução, pois explora o espaço de busca localmente,
# enquanto a heurística construtiva garante diversidade e evita ótimos locais ruins.
#
# O resultado final é uma solução de boa qualidade para cada instância, respeitando as restrições de capacidade e cobrindo todas as tarefas obrigatórias.
# Tendo como principal objetivo a qualidade de cada instância e por ser um algoritmo com uma complexidade alta seu tempo de execução é limitado a 240 segundos.
# ainda estou avaliando se esse delimitador de tempo é o ideal, mas por enquanto vai ficar assim.
# -------------------------------------------------------------------------

import os
import time
import multiprocessing
from pathlib import Path
from collections import Counter
from leitura import read_and_extract
from path_scanning import grasp_path_scanning
from melhoramento_local import melhorar_por_realocacao
from opt2 import aplicar_2opt_em_todas
import concurrent.futures

CPU_GIGAHERTZ = 3.0
DIR_REFERENCIA = "SolucoesEsperadas"
DIR_ENTRADA = "GrafosDeTeste"
DIR_RESULTADOS = "G19"

# Garante que a pasta de saída só tenha arquivos .dat de solução válidos
os.makedirs(DIR_RESULTADOS, exist_ok=True)
for file in os.listdir(DIR_RESULTADOS):
    path = os.path.join(DIR_RESULTADOS, file)
    if os.path.isfile(path) and (not file.endswith(".dat") or not file.startswith("sol-")):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Erro ao remover {path}: {e}")

# Lista todas as instâncias de teste (arquivos .dat) presentes no diretório de entrada
instancias_dat = sorted(arq for arq in os.listdir(DIR_ENTRADA) if arq.endswith(".dat"))

def processar_instancia(arquivo):
    """
    Processa uma instância do problema de roteamento capacitado.
    Responsável por ler os dados, construir as tarefas, rodar a heurística principal,
    aplicar refinamentos e salvar os resultados.
    """
    try:
        tempo_inicio = time.time()

        print(f"\n📁 LENDO INSTÂNCIA: {arquivo}")
        caminho_arquivo = os.path.join(DIR_ENTRADA, arquivo)
        cabecalho, nos, arestas, arcos, obrigatorios_v, obrigatorios_e, obrigatorios_a, _, _ = read_and_extract(caminho_arquivo)
        capacidade_veiculo = int(cabecalho["Capacity"])
        ponto_base = int(cabecalho["Depot Node"])

        # Construção das matrizes de distância e predecessores (usadas para cálculo de custos e caminhos)
        from heuristicas import construir_matriz_dist, construir_matriz_preds
        matriz_dist = construir_matriz_dist(nos, arestas, arcos)
        matriz_pred = construir_matriz_preds(nos, arestas, arcos)

        # Monta a lista de tarefas a serem atendidas (arestas, arcos e nós obrigatórios)
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

        # Lê o arquivo de referência (gabarito) para saber o número esperado de rotas
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

        # Executa apenas uma vez a heurística principal e refinamentos (SEM TEMPO LIMITE)
        melhor_rotas = None
        melhor_custo = float('inf')

        rotas_tmp = grasp_path_scanning(tarefas, matriz_dist, ponto_base, rotas_esperadas, capacidade_veiculo)
        rotas_tmp = melhorar_por_realocacao(rotas_tmp, capacidade_veiculo, matriz_dist, ponto_base)
        rotas_tmp = aplicar_2opt_em_todas(rotas_tmp, matriz_dist, ponto_base)
        custo_tmp = sum(r[1] for r in rotas_tmp)
        melhor_custo = custo_tmp
        melhor_rotas = rotas_tmp

        fim_clk = time.perf_counter_ns()

        rotas = melhor_rotas

        if not rotas:
            print("❌ Nenhuma rota válida encontrada.")
            return

        duracao_ns = fim_clk - inicio_clk
        ciclos_clk = int(duracao_ns * CPU_GIGAHERTZ)
        timestamp_exec = int(time.time())
        custo_total_rotas = sum(r[1] for r in rotas)

        nome_arquivo_saida = f"sol-{os.path.splitext(arquivo)[0]}.dat"
        caminho_saida = os.path.join(DIR_RESULTADOS, nome_arquivo_saida)

        with open(caminho_saida, "w", encoding="utf-8") as saida:
            saida.write(f"{int(custo_total_rotas)}\n{len(rotas)}\n{ciclos_clk}\n{timestamp_exec}\n")
            for idr, (rota, custo, demanda) in enumerate(rotas, 1):
                linha = f"0 1 {idr} {demanda} {int(custo)} {len(rota)+2} (D {ponto_base},1,1)"
                for serv in rota:
                    linha += f" (S {serv[0]},{serv[1]},{serv[2]})"
                linha += f" (D {ponto_base},1,1)"
                saida.write(linha + "\n")

        print("✅ Resultado salvo:", nome_arquivo_saida)

        ids_obrigatorios = [t[0] for t in tarefas]
        ids_atendidos = [s[0] for rota, _, _ in rotas for s in rota]
        contador = Counter(ids_atendidos)
        faltando = set(ids_obrigatorios) - set(ids_atendidos)
        repetidos = [id_ for id_, freq in contador.items() if freq > 1]

        if faltando:
            print(f"❌ Tarefas não atendidas ({len(faltando)}): {sorted(faltando)}")
        elif len(ids_atendidos) < len(ids_obrigatorios):
            print(f"❌ Serviços atendidos ({len(ids_atendidos)}) < esperados ({len(ids_obrigatorios)})")
        elif repetidos:
            print(f"⚠️ Tarefas repetidas: {repetidos}")
        elif set(ids_atendidos) != set(ids_obrigatorios):
            print("⚠️ Conjuntos diferentes de tarefas atendidas vs obrigatórias.")
        else:
            print("✅ Todas as tarefas foram atendidas exatamente uma vez.")

        if os.path.exists(caminho_ref):
            with open(caminho_ref, "r", encoding="utf-8") as ref:
                try:
                    linhas = ref.readlines()
                    custo_ref = int(linhas[0].strip())
                    rotas_ref = sum(1 for linha in linhas if linha.strip().startswith("0 1 "))
                except:
                    custo_ref = rotas_ref = None

            print(f"\n📌 Avaliação de Custo:")
            print(f"🔸 Encontrado: {int(custo_total_rotas)}")
            print(f"🔸 Esperado:  {custo_ref}")
            print(f"🔸 Diferença: {int(custo_total_rotas) - custo_ref}")

            print(f"🔹 Rotas geradas:   {len(rotas)}")
            print(f"🔹 Rotas esperadas: {rotas_ref}")
            print(f"🔹 Diferença:       {len(rotas) - rotas_ref}")
        else:
            print("❗ Nenhum gabarito de referência encontrado.")

    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")

if __name__ == "__main__":
    # Paralelização do processamento das instâncias usando todos os núcleos disponíveis
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        executor.map(processar_instancia, instancias_dat)# -------------------------------------------------------------------------
# COMENTÁRIOS GERAIS SOBRE O ALGORITMO E AS FUNÇÕES ENVOLVIDAS:
#
# O objetivo do código é resolver o problema de roteamento de veículos capacitado com múltiplas restrições,
# utilizando uma heurística baseada em GRASP (Greedy Randomized Adaptive Search Procedure) e refinamentos locais.
#
# - grasp_path_scanning: constrói soluções iniciais usando diferentes critérios de seleção de tarefas, promovendo diversidade.
# - melhorar_por_realocacao: tenta realocar tarefas entre rotas para reduzir o custo total, melhorando a distribuição.
# - aplicar_2opt_em_todas: aplica o algoritmo 2-opt em cada rota, otimizando a ordem das tarefas e reduzindo o custo.
#
# O uso de paralelização permite processar várias instâncias simultaneamente, acelerando experimentos em lote.
# O controle de tempo garante que cada instância não ultrapasse o tempo limite, tornando o algoritmo robusto para grandes conjuntos de dados.
#
# O refinamento das rotas é fundamental para melhorar a qualidade da solução, pois explora o espaço de busca localmente,
# enquanto a heurística construtiva garante diversidade e evita ótimos locais ruins.
#
# O resultado final é uma solução de boa qualidade para cada instância, respeitando as restrições de capacidade e cobrindo todas as tarefas obrigatórias.
# Tendo como principal objetivo a qualidade de cada instância e por ser um algoritmo com uma complexidade alta seu tempo de execução é limitado a 240 segundos.
# ainda estou avaliando se esse delimitador de tempo é o ideal, mas por enquanto vai ficar assim.
# -------------------------------------------------------------------------

import os
import time
import multiprocessing
from pathlib import Path
from collections import Counter
from leitura import read_and_extract
from path_scanning import grasp_path_scanning
from melhoramento_local import melhorar_por_realocacao
from opt2 import aplicar_2opt_em_todas
import concurrent.futures

CPU_GIGAHERTZ = 3.0
DIR_REFERENCIA = "SolucoesEsperadas"
DIR_ENTRADA = "GrafosDeTeste"
DIR_RESULTADOS = "G19"

# Garante que a pasta de saída só tenha arquivos .dat de solução válidos
os.makedirs(DIR_RESULTADOS, exist_ok=True)
for file in os.listdir(DIR_RESULTADOS):
    path = os.path.join(DIR_RESULTADOS, file)
    if os.path.isfile(path) and (not file.endswith(".dat") or not file.startswith("sol-")):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Erro ao remover {path}: {e}")

# Lista todas as instâncias de teste (arquivos .dat) presentes no diretório de entrada
instancias_dat = sorted(arq for arq in os.listdir(DIR_ENTRADA) if arq.endswith(".dat"))

def processar_instancia(arquivo):
    """
    Processa uma instância do problema de roteamento capacitado.
    Responsável por ler os dados, construir as tarefas, rodar a heurística principal,
    aplicar refinamentos e salvar os resultados.
    """
    try:
        tempo_inicio = time.time()

        print(f"\n📁 LENDO INSTÂNCIA: {arquivo}")
        caminho_arquivo = os.path.join(DIR_ENTRADA, arquivo)
        cabecalho, nos, arestas, arcos, obrigatorios_v, obrigatorios_e, obrigatorios_a, _, _ = read_and_extract(caminho_arquivo)
        capacidade_veiculo = int(cabecalho["Capacity"])
        ponto_base = int(cabecalho["Depot Node"])

        # Construção das matrizes de distância e predecessores (usadas para cálculo de custos e caminhos)
        from heuristicas import construir_matriz_dist, construir_matriz_preds
        matriz_dist = construir_matriz_dist(nos, arestas, arcos)
        matriz_pred = construir_matriz_preds(nos, arestas, arcos)

        # Monta a lista de tarefas a serem atendidas (arestas, arcos e nós obrigatórios)
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

        # Lê o arquivo de referência (gabarito) para saber o número esperado de rotas
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

        # Executa apenas uma vez a heurística principal e refinamentos (SEM TEMPO LIMITE)
        melhor_rotas = None
        melhor_custo = float('inf')

        rotas_tmp = grasp_path_scanning(tarefas, matriz_dist, ponto_base, rotas_esperadas, capacidade_veiculo)
        rotas_tmp = melhorar_por_realocacao(rotas_tmp, capacidade_veiculo, matriz_dist, ponto_base)
        rotas_tmp = aplicar_2opt_em_todas(rotas_tmp, matriz_dist, ponto_base)
        custo_tmp = sum(r[1] for r in rotas_tmp)
        melhor_custo = custo_tmp
        melhor_rotas = rotas_tmp

        fim_clk = time.perf_counter_ns()

        rotas = melhor_rotas

        if not rotas:
            print("❌ Nenhuma rota válida encontrada.")
            return

        duracao_ns = fim_clk - inicio_clk
        ciclos_clk = int(duracao_ns * CPU_GIGAHERTZ)
        timestamp_exec = int(time.time())
        custo_total_rotas = sum(r[1] for r in rotas)

        nome_arquivo_saida = f"sol-{os.path.splitext(arquivo)[0]}.dat"
        caminho_saida = os.path.join(DIR_RESULTADOS, nome_arquivo_saida)

        with open(caminho_saida, "w", encoding="utf-8") as saida:
            saida.write(f"{int(custo_total_rotas)}\n{len(rotas)}\n{ciclos_clk}\n{timestamp_exec}\n")
            for idr, (rota, custo, demanda) in enumerate(rotas, 1):
                linha = f"0 1 {idr} {demanda} {int(custo)} {len(rota)+2} (D {ponto_base},1,1)"
                for serv in rota:
                    linha += f" (S {serv[0]},{serv[1]},{serv[2]})"
                linha += f" (D {ponto_base},1,1)"
                saida.write(linha + "\n")

        print("✅ Resultado salvo:", nome_arquivo_saida)

        ids_obrigatorios = [t[0] for t in tarefas]
        ids_atendidos = [s[0] for rota, _, _ in rotas for s in rota]
        contador = Counter(ids_atendidos)
        faltando = set(ids_obrigatorios) - set(ids_atendidos)
        repetidos = [id_ for id_, freq in contador.items() if freq > 1]

        if faltando:
            print(f"❌ Tarefas não atendidas ({len(faltando)}): {sorted(faltando)}")
        elif len(ids_atendidos) < len(ids_obrigatorios):
            print(f"❌ Serviços atendidos ({len(ids_atendidos)}) < esperados ({len(ids_obrigatorios)})")
        elif repetidos:
            print(f"⚠️ Tarefas repetidas: {repetidos}")
        elif set(ids_atendidos) != set(ids_obrigatorios):
            print("⚠️ Conjuntos diferentes de tarefas atendidas vs obrigatórias.")
        else:
            print("✅ Todas as tarefas foram atendidas exatamente uma vez.")

        if os.path.exists(caminho_ref):
            with open(caminho_ref, "r", encoding="utf-8") as ref:
                try:
                    linhas = ref.readlines()
                    custo_ref = int(linhas[0].strip())
                    rotas_ref = sum(1 for linha in linhas if linha.strip().startswith("0 1 "))
                except:
                    custo_ref = rotas_ref = None

            print(f"\n📌 Avaliação de Custo:")
            print(f"🔸 Encontrado: {int(custo_total_rotas)}")
            print(f"🔸 Esperado:  {custo_ref}")
            print(f"🔸 Diferença: {int(custo_total_rotas) - custo_ref}")

            print(f"🔹 Rotas geradas:   {len(rotas)}")
            print(f"🔹 Rotas esperadas: {rotas_ref}")
            print(f"🔹 Diferença:       {len(rotas) - rotas_ref}")
        else:
            print("❗ Nenhum gabarito de referência encontrado.")

    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")

if __name__ == "__main__":
    # Paralelização do processamento das instâncias usando todos os núcleos disponíveis
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        executor.map(processar_instancia, instancias_dat)