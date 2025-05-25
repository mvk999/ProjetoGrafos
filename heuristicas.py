import random
import copy

def grasp_clarke_wright(
    servicos,
    deposito,
    matriz_distancias,
    capacidade,
    max_iter=50,
    alpha=0.3
):
    melhor_solucao = None
    melhor_custo = float('inf')

    for _ in range(max_iter):
        # 1. Construção gulosa randomizada
        rotas, demandas = construir_rotas_iniciais(servicos, deposito, matriz_distancias, capacidade)
        savings = calcular_savings(rotas, matriz_distancias, deposito)

        # Lista restrita de candidatos (LRC)
        savings_lrc = []
        if savings:
            max_s = savings[0][0]
            min_s = savings[-1][0]
            limite = max_s - alpha * (max_s - min_s)
            savings_lrc = [s for s in savings if s[0] >= limite]

        while savings_lrc:
            s, i, j = random.choice(savings_lrc)
            if rotas[i] and rotas[j]:
                tentar_fundir_rotas(rotas, demandas, i, j, capacidade)
            # Atualiza savings e LRC
            rotas_nao_vazias = [r for r in rotas if r]
            savings = calcular_savings(rotas_nao_vazias, matriz_distancias, deposito)
            if savings:
                max_s = savings[0][0]
                min_s = savings[-1][0]
                limite = max_s - alpha * (max_s - min_s)
                savings_lrc = [s for s in savings if s[0] >= limite]
            else:
                break

        # Remove rotas vazias
        rotas = [r for r in rotas if r]

        # 2. Busca local (2-opt)
        rotas = [aplicar_2opt_rota(rota, matriz_distancias, deposito) for rota in rotas]

        # 3. Avalia solução
        custo_total = sum(calcular_custo_rota(rota, matriz_distancias, deposito) for rota in rotas)
        if custo_total < melhor_custo:
            melhor_custo = custo_total
            melhor_solucao = copy.deepcopy(rotas)

    return melhor_solucao

def construir_rotas_iniciais(servicos, deposito, matriz_distancias, capacidade):
    rotas = []
    demandas = []
    for serv in servicos:
        demanda = serv['demanda']
        if demanda > capacidade:
            raise ValueError(f"Serviço {serv['id_servico']} demanda maior que capacidade do veículo!")
        rotas.append([serv])
        demandas.append(demanda)
    return rotas, demandas

def calcular_savings(rotas, matriz_distancias, deposito):
    savings = []
    n = len(rotas)
    for i in range(n):
        serv_i = rotas[i][0]
        origem_i = serv_i['origem']
        destino_i = serv_i['destino']

        for j in range(i+1, n):
            serv_j = rotas[j][0]
            origem_j = serv_j['origem']
            destino_j = serv_j['destino']

            # Savings entre o destino de i e a origem de j
            s = (matriz_distancias[deposito][origem_i] +
                 matriz_distancias[destino_j][deposito] -
                 matriz_distancias[destino_i][origem_j])
            savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)
    return savings

def tentar_fundir_rotas(rotas, demandas, idx_i, idx_j, capacidade):
    rota_i = rotas[idx_i]
    rota_j = rotas[idx_j]

    if not rota_i or not rota_j:
        return False

    # Só funde se o destino da última de i for igual à origem da primeira de j
    if rota_i[-1]['destino'] != rota_j[0]['origem']:
        return False

    demanda_total = demandas[idx_i] + demandas[idx_j]
    if demanda_total > capacidade:
        return False

    rotas[idx_i] = rota_i + rota_j
    demandas[idx_i] = demanda_total
    rotas[idx_j] = []
    demandas[idx_j] = 0
    return True

def aplicar_2opt_rota(rota, matriz_distancias, deposito):
    if len(rota) < 3:
        return rota  # Não há o que otimizar

    melhor_rota = rota[:]
    melhor_custo = calcular_custo_rota(melhor_rota, matriz_distancias, deposito)
    melhorou = True

    while melhorou:
        melhorou = False
        for i in range(1, len(rota) - 1):
            for j in range(i + 1, len(rota)):
                nova_rota = melhor_rota[:i] + melhor_rota[i:j][::-1] + melhor_rota[j:]
                novo_custo = calcular_custo_rota(nova_rota, matriz_distancias, deposito)
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
        rota = melhor_rota
    return melhor_rota

def calcular_custo_rota(rota, matriz_distancias, deposito):
    if not rota:
        return 0
    destinos = [serv['destino'] for serv in rota]
    custo = matriz_distancias[deposito][destinos[0]]
    for i in range(len(destinos) - 1):
        custo += matriz_distancias[destinos[i]][destinos[i + 1]]
    custo += matriz_distancias[destinos[-1]][deposito]
    return custo

def algoritmo_clarke_wright(servicos, deposito, matriz_distancias, capacidade):
    rotas, demandas = construir_rotas_iniciais(servicos, deposito, matriz_distancias, capacidade)
    savings = calcular_savings(rotas, matriz_distancias, deposito)

    for s, i, j in savings:
        if rotas[i] and rotas[j]:
            tentar_fundir_rotas(rotas, demandas, i, j, capacidade)

    # Remove rotas vazias
    rotas = [r for r in rotas if r]

    # Aplica 2-opt em cada rota para melhorar o custo
    rotas = [aplicar_2opt_rota(rota, matriz_distancias, deposito) for rota in rotas]

    return rotas

def salvar_solucao(
    nome_arquivo,
    rotas,
    matriz_distancias,
    deposito=0,
    tempo_referencia_execucao=0,
    tempo_referencia_solucao=0
):
    custo_total_solucao = 0
    total_rotas = len(rotas)
    linhas_rotas = []

    for idx_rota, rota in enumerate(rotas, start=1):
        servicos_unicos = {}
        demanda_rota = 0
        custo_servico_rota = 0
        custo_transporte_rota = 0

        destinos = []
        for serv in rota:
            id_s = serv["id_servico"]
            if id_s not in servicos_unicos:
                servicos_unicos[id_s] = serv
                demanda_rota += serv["demanda"]
                custo_servico_rota += serv["custo_servico"]
            destinos.append(serv["destino"])

        if destinos:
            custo_transporte_rota += matriz_distancias[deposito][destinos[0]]
            for i in range(len(destinos) - 1):
                custo_transporte_rota += matriz_distancias[destinos[i]][destinos[i + 1]]
            custo_transporte_rota += matriz_distancias[destinos[-1]][deposito]

        custo_rota = custo_servico_rota + custo_transporte_rota
        custo_total_solucao += custo_rota

        total_visitas = 2 + len(servicos_unicos)

        linha = f"0 1 {idx_rota} {demanda_rota} {custo_rota} {total_visitas} (D {deposito},1,1)"

        servicos_impressos = set()
        for serv in rota:
            id_s = serv["id_servico"]
            if id_s in servicos_impressos:
                continue
            servicos_impressos.add(id_s)
            linha += f" (S {id_s},{serv['origem']},{serv['destino']})"

        linha += f" (D {deposito},1,1)"
        linhas_rotas.append(linha)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"{custo_total_solucao}\n")
        f.write(f"{total_rotas}\n")
        f.write(f"{tempo_referencia_execucao}\n")
        f.write(f"{tempo_referencia_solucao}\n")
        for linha in linhas_rotas:
            f.write(linha + "\n")

    print(f"Solução salva em '{nome_arquivo}' com {total_rotas} rotas e custo total {custo_total_solucao}.")