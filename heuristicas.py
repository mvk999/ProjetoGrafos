from leitura import caminho_minimo
class Demanda:
    def __init__(self, origem, destino, custo, demanda, tipo):
        self.u = origem
        self.v = destino
        self.custo = custo
        self.demanda = demanda
        self.tipo = tipo

def clarke_wright_completo(demandas, dist, pred, deposito, Q):
    rotas = [[d] for d in demandas]
    savings = []
    for i in range(len(demandas)):
        for j in range(i + 1, len(demandas)):
            d1 = demandas[i]
            d2 = demandas[j]
            s = dist[deposito][d1.u] + dist[deposito][d2.v] - dist[d1.v][d2.u]
            savings.append((s, i, j))
    savings.sort(reverse=True)
    for _, i, j in savings:
        r1 = rotas[i]
        r2 = rotas[j]
        if r1 is r2:
            continue
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
                return [], float('inf')
            trecho = caminho_minimo(pred, atual, d.u)
            caminho += trecho[1:] if caminho else trecho
            caminho.append(d.v)
            custo_total += dist[atual][d.u] + d.custo
            atual = d.v
        if dist[atual][deposito] == float('inf'):
            return [], float('inf')
        caminho += caminho_minimo(pred, atual, deposito)[1:]
        custo_total += dist[atual][deposito]
        rotas_reais.append(caminho)
    return rotas_reais, custo_total

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

def three_opt(route, dist):
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 4):
            for j in range(i + 1, len(best) - 2):
                for k in range(j + 1, len(best) - 1):
                    A, B, C, D, E, F = best[i - 1], best[i], best[j - 1], best[j], best[k - 1], best[k]
                    segments = [
                        best[:i] + best[i:j][::-1] + best[j:k] + best[k:],               # Case 1: inverte i-j
                        best[:i] + best[i:j] + best[j:k][::-1] + best[k:],               # Case 2: inverte j-k
                        best[:i] + best[j:k] + best[i:j] + best[k:],                     # Case 3: troca i-j com j-k
                        best[:i] + best[j:k][::-1] + best[i:j][::-1] + best[k:],         # Case 4: inverte ambos
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