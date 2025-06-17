import random
import time
from leitura import read_and_extract
from heuristicas import construir_matriz_dist, construir_matriz_preds, custo_rota_individual
from copy import deepcopy

def executar_memetico(caminho_arquivo, capacidade, deposito, matriz_dist, matriz_pred, obrig_v, obrig_e, obrig_a):
    # Etapa 1: Gerar tarefas obrigatórias
    tarefas = gerar_tarefas(obrig_v, obrig_e, obrig_a, matriz_dist)

    # Etapa 2: População inicial com Path Scanning
    tamanho_pop = 20
    populacao = construir_populacao_inicial(tarefas, matriz_dist, capacidade, deposito, tamanho_pop)

    # Etapa 3: Loop evolutivo
    num_geracoes = 50
    elite = 2

    for geracao in range(num_geracoes):
        populacao.sort(key=lambda ind: custo_individuo(ind, tarefas, matriz_dist, deposito))
        nova_pop = populacao[:elite]  # elitismo: mantém os melhores

        while len(nova_pop) < tamanho_pop:
            pai1, pai2 = random.sample(populacao[:5], 2)  # seleção por torneio simples
            filho = crossover_rbx(pai1, pai2, tarefas, capacidade, deposito, matriz_dist)
            nova_pop.append(filho)

        populacao = nova_pop

    populacao.sort(key=lambda ind: custo_individuo(ind, tarefas, matriz_dist, deposito))
    melhor = populacao[0]
    return melhor, {t['id']: t for t in tarefas}


def gerar_tarefas(obrig_v, obrig_e, obrig_a, matriz_dist):
    tarefas = []
    id_global = 0

    for v, (demanda, servico) in obrig_v:
        tarefas.append({
            'id': id_global,
            'origem': v,
            'destino': v,
            'demanda': demanda,
            'servico': servico,
            'tipo': 'V'
        })
        id_global += 1

    for (u, v), (custo, demanda, servico) in obrig_e:
        tarefas.append({
            'id': id_global,
            'origem': u,
            'destino': v,
            'demanda': demanda,
            'servico': servico,
            'tipo': 'E'
        })
        id_global += 1

    for (u, v), (custo, demanda, servico) in obrig_a:
        tarefas.append({
            'id': id_global,
            'origem': u,
            'destino': v,
            'demanda': demanda,
            'servico': servico,
            'tipo': 'A'
        })
        id_global += 1

    return tarefas



def construir_populacao_inicial(tarefas, matriz_dist, capacidade, deposito, tamanho_pop=20):
    populacao = []
    for _ in range(tamanho_pop):
        random.shuffle(tarefas)
        individuo = construir_individuo(tarefas, capacidade)
        populacao.append(individuo)
    return populacao


def construir_individuo(tarefas, capacidade):
    rotas = []
    rota_atual = []
    carga_atual = 0

    for t in tarefas:
        if carga_atual + t['demanda'] > capacidade:
            rotas.append(rota_atual)
            rota_atual = []
            carga_atual = 0

        rota_atual.append(t)
        carga_atual += t['demanda']

    if rota_atual:
        rotas.append(rota_atual)

    return rotas


def custo_individuo(individuo, tarefas, matriz_dist, deposito):
    custo_total = 0
    mapa_tarefas = {t['id']: t for t in tarefas}

    for rota in individuo:
        if not rota:
            continue
        pos = deposito
        for t in rota:
            tarefa = mapa_tarefas[t['id']] if isinstance(t, dict) else mapa_tarefas[t]
            custo_total += matriz_dist[pos][tarefa['origem']]
            custo_total += tarefa['servico']
            pos = tarefa['destino']
        custo_total += matriz_dist[pos][deposito]

    return custo_total


def crossover_rbx(pai1, pai2, tarefas, capacidade, deposito, matriz_dist):
    filho = []
    usados = set()
    mapa_tarefas = {t['id']: t for t in tarefas}

    rotas_selecionadas = random.sample(pai1, k=max(1, len(pai1)//2))
    for rota in rotas_selecionadas:
        filho.append(rota[:])
        for t in rota:
            usados.add(t['id'] if isinstance(t, dict) else t)

    restantes = []
    for rota in pai2:
        for t in rota:
            tid = t['id'] if isinstance(t, dict) else t
            if tid not in usados:
                restantes.append(mapa_tarefas[tid])

    rota_atual = []
    carga = 0
    for t in restantes:
        if carga + t['demanda'] > capacidade:
            if rota_atual:
                filho.append(rota_atual)
            rota_atual = [t]
            carga = t['demanda']
        else:
            rota_atual.append(t)
            carga += t['demanda']
    if rota_atual:
        filho.append(rota_atual)

    return filho

def salvar_solucao_memetica(nome_arquivo, rotas, tarefas, deposito, matriz_dist, ciclos_clk, timestamp_exec):
    with open(nome_arquivo, "w", encoding="utf-8") as saida:
        custo_total = custo_individuo(rotas, list(tarefas.values()), matriz_dist, deposito)
        saida.write(f"{custo_total}\n")
        saida.write(f"{len(rotas)}\n")
        saida.write(f"{ciclos_clk}\n")
        saida.write(f"{timestamp_exec}\n")

        for idr, rota in enumerate(rotas, 1):
            demanda = sum(t['demanda'] if isinstance(t, dict) else tarefas[t]['demanda'] for t in rota)
            custo = 0
            if rota:
                pos = deposito
                for t in rota:
                    t_data = tarefas[t['id']] if isinstance(t, dict) else tarefas[t]
                    custo += matriz_dist[pos][t_data['origem']]
                    custo += t_data['servico']
                    pos = t_data['destino']
                custo += matriz_dist[pos][deposito]

            linha = f"0 1 {idr} {demanda} {custo} {len(rota)+2} (D {deposito},1,1)"
            for t in rota:
                t_data = tarefas[t['id']] if isinstance(t, dict) else tarefas[t]
                linha += f" (S {t_data['id']},{t_data['origem']},{t_data['destino']})"
            linha += f" (D {deposito},1,1)\n"
            saida.write(linha)



# Exemplo de teste (teste isolado do algoritmo memético)
#teste inicial do BHW1.dat 
# melhorou em 5 no custo em relação ao alg anterior
# no bhw10 piorou bastante até o momento
if __name__ == "__main__":
    caminho = "GrafosDeTeste/BHW1.dat"
    cab, nos, arest, arcos, ov, oe, oa, _, _ = read_and_extract(caminho)
    capacidade = int(cab["Capacity"])
    deposito = int(cab["Depot Node"])
    dist = construir_matriz_dist(nos, arest, arcos)
    preds = construir_matriz_preds(nos, arest, arcos)

    melhor, mapa_tarefas = executar_memetico(
        caminho_arquivo=caminho,
        capacidade=capacidade,
        deposito=deposito,
        matriz_dist=dist,
        matriz_pred=preds,
        obrig_v=ov,
        obrig_e=oe,
        obrig_a=oa
    )

    custo = custo_individuo(melhor, list(mapa_tarefas.values()), dist, deposito)

    print(f"\n💰 Custo total da melhor solução: {custo}")
    print("Melhor solução encontrada:")
    for rota in melhor:
        print([t['id'] if isinstance(t, dict) else t for t in rota])

    # Simula clocks e tempo de execução
    ciclos_clk = int(time.perf_counter_ns() * 3.0)  # 3GHz
    timestamp_exec = int(time.time())

    salvar_solucao_memetica(
        nome_arquivo="SolucoesGeradas/sol-BHW1_memetico.txt",
        rotas=melhor,
        tarefas=mapa_tarefas,
        deposito=deposito,
        matriz_dist=dist,
        ciclos_clk=ciclos_clk,
        timestamp_exec=timestamp_exec
    )

    print("✅ Solução salva em SolucoesGeradas/sol-BHW1_memetico.txt")



