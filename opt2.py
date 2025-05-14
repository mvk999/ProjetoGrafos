# opt_2.py

def calcular_custo_rota(rota, matriz_dist, deposito):
    if not rota:
        return 0
    custo = matriz_dist[deposito][rota[0][1]]  # do depósito até o primeiro serviço
    for i in range(len(rota) - 1):
        custo += matriz_dist[rota[i][2]][rota[i + 1][1]]  # destino atual -> origem do próximo
        custo += rota[i][5]  # custo do serviço
    custo += rota[-1][5]  # custo do último serviço
    custo += matriz_dist[rota[-1][2]][deposito]  # retorno ao depósito
    return custo


def aplicar_2opt_rota(rota, matriz_dist, deposito):
    """
    Aplica 2-opt para melhorar a ordem dos serviços dentro de uma rota.
    """
    if len(rota) < 3:
        return rota, calcular_custo_rota(rota, matriz_dist, deposito)

    melhor_rota = rota
    melhor_custo = calcular_custo_rota(rota, matriz_dist, deposito)
    melhorou = True

    while melhorou:
        melhorou = False
        for i in range(1, len(rota) - 1):
            for j in range(i + 1, len(rota)):
                nova_rota = rota[:i] + rota[i:j+1][::-1] + rota[j+1:]
                novo_custo = calcular_custo_rota(nova_rota, matriz_dist, deposito)
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
        rota = melhor_rota

    return melhor_rota, melhor_custo


def aplicar_2opt_em_todas(rotas, matriz_dist, deposito):
    """
    Aplica 2-opt em todas as rotas para refinar a ordem dos serviços.
    """
    novas_rotas = []
    for rota, _, carga in rotas:
        nova_rota, novo_custo = aplicar_2opt_rota(rota, matriz_dist, deposito)
        novas_rotas.append((nova_rota, novo_custo, carga))
    return novas_rotas