# melhoramento_local.py

def calcular_custo_rota(rota, matriz_dist, deposito):
    if not rota:
        return 0
    custo = matriz_dist[deposito][rota[0][1]]  # depósito até o primeiro serviço
    for i in range(len(rota) - 1):
        custo += matriz_dist[rota[i][2]][rota[i + 1][1]]  # destino atual -> origem próximo
        custo += rota[i][5]  # custo do serviço atual
    custo += rota[-1][5]  # custo do último serviço
    custo += matriz_dist[rota[-1][2]][deposito]  # volta ao depósito
    return custo


def melhorar_por_realocacao(rotas, capacidade, matriz_dist, deposito):
    """
    Tenta melhorar as rotas por realocação de serviços entre pares de rotas.
    """
    mudou = True
    while mudou:
        mudou = False
        for i in range(len(rotas)):
            for j in range(i + 1, len(rotas)):
                rota_a, custo_a, carga_a = rotas[i]
                rota_b, custo_b, carga_b = rotas[j]
                for sa in rota_a:
                    for sb in rota_b:
                        nova_carga_a = carga_a - sa[4] + sb[4]
                        nova_carga_b = carga_b - sb[4] + sa[4]
                        if nova_carga_a <= capacidade and nova_carga_b <= capacidade:
                            nova_rota_a = rota_a.copy()
                            nova_rota_b = rota_b.copy()
                            nova_rota_a.remove(sa)
                            nova_rota_a.append(sb)
                            nova_rota_b.remove(sb)
                            nova_rota_b.append(sa)
                            novo_custo_a = calcular_custo_rota(nova_rota_a, matriz_dist, deposito)
                            novo_custo_b = calcular_custo_rota(nova_rota_b, matriz_dist, deposito)
                            if novo_custo_a + novo_custo_b < custo_a + custo_b:
                                rotas[i] = (nova_rota_a, novo_custo_a, nova_carga_a)
                                rotas[j] = (nova_rota_b, novo_custo_b, nova_carga_b)
                                mudou = True
    return rotas
