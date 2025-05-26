import random
import time
import heapq

def busca_dijkstra(inicio, liga_arestas, liga_arcos, nos):
    nos_ids = {v if isinstance(v, int) else v[0] for v in nos}
    custos = {v: float('inf') for v in nos_ids}
    custos[inicio] = 0
    predecessores = {v: None for v in nos_ids}
    fila = [(0, inicio)]

    ligacoes = set()
    for (u, v), custo in liga_arestas:
        ligacoes.add((u, v, custo, False))
    for (u, v), custo in liga_arcos:
        ligacoes.add((u, v, custo, True))

    while fila:
        atual_custo, atual_no = heapq.heappop(fila)
        if atual_custo > custos[atual_no]:
            continue

        for u, v, custo, eh_arco in ligacoes:
            if u == atual_no:
                viz = v
            elif not eh_arco and v == atual_no:
                viz = u
            else:
                continue

            novo_custo = atual_custo + custo
            if novo_custo < custos[viz]:
                custos[viz] = novo_custo
                predecessores[viz] = atual_no
                heapq.heappush(fila, (novo_custo, viz))

    return custos, predecessores

def construir_matriz_dist(nos, liga_arestas, liga_arcos):
    matriz = {}
    for no in nos:
        distancias, _ = busca_dijkstra(no, liga_arestas, liga_arcos, nos)
        matriz[no] = {dest: distancias.get(dest, float('inf')) for dest in nos}
    return matriz

def construir_matriz_preds(nos, liga_arestas, liga_arcos):
    matriz = {}
    for no in nos:
        _, preds = busca_dijkstra(no, liga_arestas, liga_arcos, nos)
        matriz[no] = {dest: preds.get(dest, None) for dest in nos}
    return matriz

def caminho_otimo(preds, origem, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.insert(0, atual)
        atual = preds[origem].get(atual)
    return caminho

def gerar_tarefas(arestas_obrig, arcos_obrig, vertices_obrig):
    tarefas = []
    for (u, v), (custo, dem, serv) in arestas_obrig:
        tarefas.append({'tipo': 'aresta', 'origem': u, 'destino': v, 'demanda': dem, 'servico': serv, 'custo_t': custo})
    for (u, v), (custo, dem, serv) in arcos_obrig:
        tarefas.append({'tipo': 'arco', 'origem': u, 'destino': v, 'demanda': dem, 'servico': serv, 'custo_t': custo})
    for v, (dem, serv) in vertices_obrig:
        tarefas.append({'tipo': 'vertice', 'origem': v, 'destino': v, 'demanda': dem, 'servico': serv, 'custo_t': 0})
    return tarefas

def custos_entre_tarefas(tarefas, matriz):
    custos = {}
    for i, t1 in enumerate(tarefas):
        for j, t2 in enumerate(tarefas):
            if i == j:
                continue
            origem = t1['destino'] if t1['tipo'] != 'vertice' else t1['origem']
            destino = t2['origem']
            custo = matriz[origem][destino] + t1['servico'] + t2['servico']
            custos[(i, j)] = custo
    return custos

def criar_rota(tarefas, indices, deposito, matriz_preds):
    rota = [deposito]
    for i, idx in enumerate(indices):
        tarefa = tarefas[idx]
        origem = tarefa['origem']
        if i == 0:
            rota += caminho_otimo(matriz_preds, rota[-1], origem)[1:]
        else:
            anterior = tarefas[indices[i - 1]]
            ult = anterior['destino'] if anterior['tipo'] != 'vertice' else anterior['origem']
            rota += caminho_otimo(matriz_preds, ult, origem)[1:]
        if tarefa['tipo'] != 'vertice':
            rota.append(tarefa['destino'])
    fim = tarefas[indices[-1]]
    ult = fim['destino'] if fim['tipo'] != 'vertice' else fim['origem']
    rota += caminho_otimo(matriz_preds, ult, deposito)[1:]
    return rota

def rotas_iniciais(tarefas, deposito, capacidade, matriz_preds):
    rotas = []
    for idx, tarefa in enumerate(tarefas):
        if tarefa['demanda'] > capacidade:
            continue
        rota = criar_rota(tarefas, [idx], deposito, matriz_preds)
        rotas.append({'tarefas': [idx], 'demanda': tarefa['demanda'], 'rota_completa': rota})
    return rotas

def calcular_savings(tarefas, custos_t, matriz, deposito, capacidade):
    savings = []
    for i, t1 in enumerate(tarefas):
        for j, t2 in enumerate(tarefas):
            if i >= j:
                continue
            if t1['demanda'] + t2['demanda'] > capacidade:
                continue
            c1 = matriz[deposito][t1['origem']]
            c2 = matriz[t2['destino']][deposito] if t2['tipo'] != 'vertice' else matriz[t2['origem']][deposito]
            s = c1 + c2 - custos_t[(i, j)]
            savings.append(((i, j), s))
    return savings

def ordenar_savings(savings, rng=None):
    if rng:
        rng.shuffle(savings)
    else:
        savings.sort(key=lambda x: x[1], reverse=True)
    return savings

def pode_unir(rota1, rota2, capacidade):
    return (rota1['demanda'] + rota2['demanda']) <= capacidade

def unir_rotas(rota1, rota2, tarefas, deposito, matriz_preds):
    novas = rota1['tarefas'] + rota2['tarefas']
    return {
        'tarefas': novas,
        'demanda': rota1['demanda'] + rota2['demanda'],
        'rota_completa': criar_rota(tarefas, novas, deposito, matriz_preds)
    }

def aplicar_savings(rotas, savings, capacidade, tarefas, deposito, matriz_preds, usar_fusao_bidirecional=False):
    for (i, j), _ in savings:
        r1 = next((r for r in rotas if r['tarefas'] and r['tarefas'][-1] == i), None)
        r2 = next((r for r in rotas if r['tarefas'] and r['tarefas'][0] == j), None)
        if r1 and r2 and r1 != r2:
            if pode_unir(r1, r2, capacidade):
                nova = unir_rotas(r1, r2, tarefas, deposito, matriz_preds)
                rotas.remove(r1)
                rotas.remove(r2)
                rotas.append(nova)
            elif usar_fusao_bidirecional and pode_unir(r2, r1, capacidade):
                nova = unir_rotas(r2, r1, tarefas, deposito, matriz_preds)
                rotas.remove(r1)
                rotas.remove(r2)
                rotas.append(nova)
    return rotas

def refinar_rota_2opt(rota, matriz):
    caminho = rota['rota_completa']
    melhor_caminho = caminho[:]
    melhor_custo = sum(matriz[caminho[i]][caminho[i+1]] for i in range(len(caminho)-1))
    for i in range(1, len(caminho) - 2):
        for j in range(i+1, len(caminho) - 1):
            novo = caminho[:i] + caminho[i:j+1][::-1] + caminho[j+1:]
            custo = sum(matriz[novo[k]][novo[k+1]] for k in range(len(novo)-1))
            if custo < melhor_custo:
                melhor_caminho = novo
                melhor_custo = custo
    rota['rota_completa'] = melhor_caminho
    return rota

def custo_rota_individual(rota, tarefas, matriz):
    custo = sum(tarefas[t]['servico'] for t in rota['tarefas'])
    caminho = rota['rota_completa']
    custo_transp = sum(matriz[caminho[i]][caminho[i + 1]] for i in range(len(caminho) - 1))
    desloc_serv = sum(tarefas[t]['custo_t'] for t in rota['tarefas'])
    return custo + (custo_transp - desloc_serv)

def custo_total(rotas, tarefas, matriz):
    return sum(custo_rota_individual(r, tarefas, matriz) for r in rotas)

def clarke_wright_controller(arestas_obrig, arcos_obrig, vertices_obrig,
                              deposito, num_veiculos, capacidade,
                              matriz_dist, matriz_preds,
                              seed=None, embaralhar=False,
                              usar_fusao_bidirecional=False,
                              refinar_2opt=False):
    rng = random.Random(seed) if seed else None
    tarefas = gerar_tarefas(arestas_obrig, arcos_obrig, vertices_obrig)
    for i, t in enumerate(tarefas):
        t['id'] = i
    if embaralhar and rng:
        rng.shuffle(tarefas)
    custos_t = custos_entre_tarefas(tarefas, matriz_dist)
    rotas = rotas_iniciais(tarefas, deposito, capacidade, matriz_preds)
    savings = calcular_savings(tarefas, custos_t, matriz_dist, deposito, capacidade)
    savings = ordenar_savings(savings, rng)
    rotas = aplicar_savings(rotas, savings, capacidade, tarefas, deposito, matriz_preds, usar_fusao_bidirecional)
    if refinar_2opt:
        for rota in rotas:
            refinar_rota_2opt(rota, matriz_dist)
    return rotas, tarefas
