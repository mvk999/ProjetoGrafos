from leitura import caminho_minimo

class Demanda:
    def __init__(self, origem, destino, custo, demanda, tipo, id_servico):
        self.u = origem
        self.v = destino
        self.custo = custo
        self.demanda = demanda
        self.tipo = tipo
        self.id = id_servico

def clarke_wright_completo(demandas, dist, pred, deposito, Q):
    rotas = [[d] for d in demandas]
    savings = []
    for i in range(len(demandas)):
        for j in range(i + 1, len(demandas)):
            d1 = demandas[i]
            d2 = demandas[j]
            s = (dist[deposito][d1.u] + dist[d2.v][deposito] - dist[d1.v][d2.u]) - 0.5 * abs(d1.demanda - d2.demanda)
            savings.append((s, i, j))
    savings.sort(reverse=True)

    for _, i, j in savings:
        r1, r2 = rotas[i], rotas[j]
        if r1 is r2: continue
        total_d = sum(d.demanda for d in r1 + r2)
        if total_d <= Q:
            nova_rota = r1 + r2
            for k in range(len(rotas)):
                if rotas[k] is r1 or rotas[k] is r2:
                    rotas[k] = nova_rota

    rotas_finais = []
    for r in rotas:
        if r not in rotas_finais:
            rotas_finais.append(r)

    custo_total = 0
    rotas_reais = []
    for rota in rotas_finais:
        caminho = []
        atual = deposito
        for d in rota:
            if dist[atual][d.u] == float('inf'):
                return [], float('inf'), []
            trecho = caminho_minimo(pred, atual, d.u)
            caminho += trecho[1:] if caminho else trecho
            caminho.append(d.v)
            custo_total += dist[atual][d.u] + d.custo
            atual = d.v
        if dist[atual][deposito] == float('inf'):
            return [], float('inf'), []
        caminho += caminho_minimo(pred, atual, deposito)[1:]
        custo_total += dist[atual][deposito]
        rotas_reais.append(caminho)

    return rotas_reais, custo_total, rotas_finais

def melhorar_rotas_pelo_servico(rotas_demandas, dist, pred, deposito, Q):
    def custo_rota(rota):
        atual = deposito
        custo = 0
        for d in rota:
            custo += dist[atual][d.u] + d.custo
            atual = d.v
        custo += dist[atual][deposito]
        return custo

    rotas = rotas_demandas[:]
    melhorou = True

    while melhorou:
        melhorou = False
        candidatos = []

        for i in range(len(rotas)):
            for j in range(i + 1, len(rotas)):
                r1, r2 = rotas[i], rotas[j]
                carga1 = sum(d.demanda for d in r1)
                carga2 = sum(d.demanda for d in r2)

                if carga1 + carga2 > Q:
                    continue

                custo1 = custo_rota(r1)
                custo2 = custo_rota(r2)
                custo_antes = custo1 + custo2

                combinada = r1 + r2
                custo_depois = custo_rota(combinada)

                economia = custo_antes - custo_depois
                if economia > 0:
                    candidatos.append((economia / (carga1 + carga2), economia, i, j, combinada))

        if candidatos:
            candidatos.sort(reverse=True)
            _, _, i, j, nova_rota = candidatos[0]
            rotas[i] = nova_rota
            rotas.pop(j)
            melhorou = True

    return rotas

def realocar_rotas_pequenas(rotas_demandas, Q):
    novas_rotas = []
    rotas_pequenas = []

    for rota in rotas_demandas:
        if len(rota) <= 2:
            rotas_pequenas.append(rota)
        else:
            novas_rotas.append(rota)

    for rota_pequena in rotas_pequenas:
        demanda_total = sum(d.demanda for d in rota_pequena)
        realocado = False
        for rota_grande in novas_rotas:
            carga_atual = sum(d.demanda for d in rota_grande)
            if carga_atual + demanda_total <= Q:
                rota_grande.extend(rota_pequena)
                realocado = True
                break
        if not realocado:
            novas_rotas.append(rota_pequena)

    return novas_rotas

def two_opt(route, dist):
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue
                new_route = best[:i] + best[i:j][::-1] + best[j:]
                old_cost = sum(dist[best[k]][best[k + 1]] for k in range(len(best) - 1))
                new_cost = sum(dist[new_route[k]][new_route[k + 1]] for k in range(len(new_route) - 1))
                if new_cost < old_cost:
                    best = new_route
                    improved = True
                    break
            if improved:
                break
    return best

def three_opt(route, dist):
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 4):
            for j in range(i + 1, len(best) - 2):
                for k in range(j + 1, len(best) - 1):
                    segments = [
                        best[:i] + best[i:j][::-1] + best[j:k] + best[k:],               
                        best[:i] + best[i:j] + best[j:k][::-1] + best[k:],               
                        best[:i] + best[j:k] + best[i:j] + best[k:],                     
                        best[:i] + best[j:k][::-1] + best[i:j][::-1] + best[k:],         
                    ]
                    best_cost = sum(dist[best[x]][best[x+1]] for x in range(len(best) - 1))
                    for s in segments:
                        new_cost = sum(dist[s[x]][s[x+1]] for x in range(len(s) - 1))
                        if new_cost < best_cost:
                            best = s
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    return best

def remover_repeticoes_consecutivas(rota):
    nova = []
    for v in rota:
        if not nova or nova[-1] != v:
            nova.append(v)
    return nova

def reconstruir_rota_valida(rota, pred):
    rota_real = []
    for i in range(len(rota) - 1):
        trecho = caminho_minimo(pred, rota[i], rota[i + 1])
        if not trecho:
            return []
        rota_real += trecho[1:] if rota_real else trecho
    return rota_real
