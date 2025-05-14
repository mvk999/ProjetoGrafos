import random

def grasp_path_scanning(tarefas, matriz_dist, deposito, rotas_esperadas, capacidade, iteracoes=5, rcl_size=3, seed_base=42):
    melhores_rotas = None
    melhor_custo_total = float('inf')
    criterios = ['proximo', 'distante', 'maior_demanda', 'menor_ratio', 'random']

    criterios_usados = criterios * ((iteracoes // len(criterios)) + 1)
    criterios_usados = criterios_usados[:iteracoes]

    for idx, criterio in enumerate(criterios_usados):
        random.seed(seed_base + idx)
        rotas = path_scanning_rcl(
            tarefas, matriz_dist, deposito, capacidade,
            criterio=criterio, rcl_size=rcl_size, seed=seed_base + idx
        )
        rotas = realocacao_tarefa_inteligente(rotas, capacidade, matriz_dist, deposito, min_rotas=rotas_esperadas)
        rotas = melhor_fusao_rotas(rotas, capacidade, matriz_dist, deposito, min_rotas=rotas_esperadas)

        if rotas_esperadas is not None and len(rotas) < rotas_esperadas:
            rotas = tentar_recompor_rotas(rotas, tarefas, capacidade, matriz_dist, deposito, rotas_esperadas)

        custo_total = sum(r[1] for r in rotas)
        if custo_total < melhor_custo_total:
            melhores_rotas = rotas
            melhor_custo_total = custo_total

    return melhores_rotas

def tentar_recompor_rotas(rotas, tarefas, capacidade, matriz_dist, deposito, rotas_esperadas):
    tarefas_usadas = set(t for rota in rotas for t in rota[0])
    tarefas_restantes = [t for t in tarefas if t not in tarefas_usadas]

    if not tarefas_restantes:
        rotas_atuais = rotas[:]
        rotas_atuais.sort(key=lambda r: len(r[0]), reverse=True)

        while len(rotas_atuais) < rotas_esperadas:
            rota_maior = rotas_atuais.pop(0)
            meio = len(rota_maior[0]) // 2
            nova_rota_1 = rota_maior[0][:meio]
            nova_rota_2 = rota_maior[0][meio:]

            c1 = calcular_custo_rota(nova_rota_1, matriz_dist, deposito)
            c2 = calcular_custo_rota(nova_rota_2, matriz_dist, deposito)
            d1 = sum(t[4] for t in nova_rota_1)
            d2 = sum(t[4] for t in nova_rota_2)

            if d1 <= capacidade and d2 <= capacidade:
                rotas_atuais.append((nova_rota_1, c1, d1))
                rotas_atuais.append((nova_rota_2, c2, d2))
            else:
                rotas_atuais.append(rota_maior)
                break

        return rotas_atuais
    else:
        novas_rotas = path_scanning_rcl(tarefas_restantes, matriz_dist, deposito, capacidade)
        return rotas + novas_rotas

def path_scanning_rcl(tarefas, matriz_dist, deposito, capacidade, criterio='proximo', max_por_rota=6, rcl_size=3, seed=None):
    if seed is not None:
        random.seed(seed)
    tarefas_pendentes = set(tarefas)
    rotas = []
    while tarefas_pendentes:
        rota = []
        carga = 0
        custo = 0
        pos = deposito
        tarefas_na_rota = 0

        candidatos = [t for t in tarefas_pendentes if t[4] + carga <= capacidade]
        if not candidatos:
            break
        candidatos.sort(key=lambda t: (-t[4], matriz_dist[deposito][t[1]]))
        primeira = candidatos[0]
        rota.append(primeira)
        custo += matriz_dist[deposito][primeira[1]] + primeira[5]
        carga += primeira[4]
        pos = primeira[2] if primeira[3] != 'V' else primeira[1]
        tarefas_pendentes.remove(primeira)
        tarefas_na_rota += 1

        while True:
            candidatos = [t for t in tarefas_pendentes if t[4] + carga <= capacidade]
            if not candidatos or tarefas_na_rota >= max_por_rota:
                break
            if criterio == 'proximo':
                candidatos.sort(key=lambda t: matriz_dist[pos][t[1]])
            elif criterio == 'distante':
                candidatos.sort(key=lambda t: -matriz_dist[pos][t[1]])
            elif criterio == 'maior_demanda':
                candidatos.sort(key=lambda t: -t[4])
            elif criterio == 'menor_ratio':
                candidatos.sort(key=lambda t: matriz_dist[pos][t[1]] / (t[4] + 1e-6))
            elif criterio == 'random':
                random.shuffle(candidatos)
            rcl_len = min(rcl_size, max(1, len(candidatos)//2 + 1))
            rcl = candidatos[:rcl_len]
            proximo = random.choice(rcl)
            rota.append(proximo)
            custo += matriz_dist[pos][proximo[1]] + proximo[5]
            carga += proximo[4]
            pos = proximo[2] if proximo[3] != 'V' else proximo[1]
            tarefas_pendentes.remove(proximo)
            tarefas_na_rota += 1
        custo += matriz_dist[pos][deposito]
        rotas.append((rota, custo, carga))
    return rotas

def realocacao_tarefa_inteligente(rotas, capacidade, matriz_dist, deposito, min_rotas=None):
    melhorou = True
    while melhorou:
        melhorou = False
        for i, (rota_origem, custo_o, carga_o) in enumerate(rotas):
            for idx_tarefa, tarefa in enumerate(rota_origem):
                for j, (rota_dest, custo_d, carga_d) in enumerate(rotas):
                    if i == j or carga_d + tarefa[4] > capacidade:
                        continue
                    for pos in range(len(rota_dest)+1):
                        nova_rota_dest = rota_dest[:pos] + [tarefa] + rota_dest[pos:]
                        nova_rota_origem = rota_origem[:idx_tarefa] + rota_origem[idx_tarefa+1:]
                        if not nova_rota_origem:
                            continue
                        novo_custo_dest = calcular_custo_rota(nova_rota_dest, matriz_dist, deposito)
                        novo_custo_origem = calcular_custo_rota(nova_rota_origem, matriz_dist, deposito)
                        if novo_custo_dest + novo_custo_origem < custo_d + custo_o:
                            rotas[j] = (nova_rota_dest, novo_custo_dest, carga_d + tarefa[4])
                            rotas[i] = (nova_rota_origem, novo_custo_origem, carga_o - tarefa[4])
                            melhorou = True
                            break
                    if melhorou:
                        break
                if melhorou:
                    break
            if melhorou:
                break
        if min_rotas is not None:
            rotas_validas = [r for r in rotas if r[0]]
            if len(rotas_validas) >= min_rotas:
                rotas = rotas_validas
        else:
            rotas = [r for r in rotas if r[0]]
    return rotas

def validar_direcao(rota):
    for tarefa in rota:
        if tarefa[3] == 'A' and tarefa[1] == tarefa[2]:
            return False
    return True

def melhor_fusao_rotas(rotas, capacidade, matriz_dist, deposito, max_ratio=3, min_rotas=None):
    novas = rotas[:]
    mudou = True
    while mudou:
        mudou = False
        for i in range(len(novas)):
            for j in range(i+1, len(novas)):
                if min_rotas is not None and len(novas) - 1 < min_rotas:
                    continue
                r1, c1, d1 = novas[i]
                r2, c2, d2 = novas[j]
                if d1 + d2 > capacidade or max(len(r1), len(r2)) > max_ratio * min(len(r1), len(r2)):
                    continue
                opcoes = [
                    (r1 + r2, d1 + d2),
                    (r2 + r1, d1 + d2),
                ]
                for nova_rota, nova_carga in opcoes:
                    if not validar_direcao(nova_rota):
                        continue
                    novo_custo = calcular_custo_rota(nova_rota, matriz_dist, deposito)
                    if novo_custo < c1 + c2:
                        novas[i] = (nova_rota, novo_custo, nova_carga)
                        novas.pop(j)
                        mudou = True
                        break
                if mudou:
                    break
            if mudou:
                break
    return novas

def calcular_custo_rota(rota, matriz_dist, deposito):
    if not rota:
        return 0
    custo = matriz_dist[deposito][rota[0][1]]
    for i in range(len(rota)):
        custo += rota[i][5]
        if i < len(rota) - 1:
            custo += matriz_dist[rota[i][2]][rota[i+1][1]]
    custo += matriz_dist[rota[-1][2]][deposito]
    return custo
