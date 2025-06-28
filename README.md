# Trabalho Prático Final

## Algoritmos em Grafos - Universidade Federal de Lavras

Este repositório contém a implementação do Trabalho Prático Final da disciplina **GCC218 - Algoritmos em Grafos**.

# 🚚 ProjetoGrafos – Roteamento com Restrições (CARP)

Projeto para resolver o **Problema de Roteamento de Veículos com Restrições de Capacidade (CARP)** utilizando heurísticas construtivas, refinamento local, paralelização e leitura de instâncias reais em grafos.

---

## 📑 Índice

- [Descrição](#descrição)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Modelagem e Entrada](#modelagem-e-entrada)
- [Arquitetura e Organização do Código](#arquitetura-e-organização-do-código)
- [Instalação e Execução](#instalação-e-execução)
- [Formato da Saída](#formato-da-saída)
- [Melhorias Futuras](#melhorias-futuras)
- [Autor](#autor)
- [Contato](#contato)

---

## 📘 Descrição

Este projeto implementa uma solução heurística para o **CARP**, onde tarefas em arestas, vértices ou arcos obrigatórios devem ser atendidas respeitando limites de capacidade e custo.

O algoritmo utilizado é uma combinação de:

- **GRASP** (Greedy Randomized Adaptive Search Procedure)
- **Refinamento local com 2-opt**
- **Realocação de tarefas entre rotas**
- **Execução paralela com `concurrent.futures`**
- Controle de tempo por instância (timeout de 240 segundos)

---

## 🚀 Tecnologias Utilizadas

- Python 3.10+
- NumPy
- Matplotlib
- Pandas
- Concurrent.futures

---

## 📥 Modelagem e Entrada

### Estrutura dos dados `.dat`

Os arquivos estão organizados nas pastas:
- `GrafosDeTeste/`: instâncias a serem resolvidas
- `SolucoesEsperadas/`: gabaritos fornecidos

Cada arquivo `.dat` contém seções como:

- **VERTICES, EDGES, ARCS**
- **Requeridos (ReE, ReA, ReN)**
- **CAPACITY** do veículo
- **DEPOT** (vértice depósito)

O parser identifica todas as tarefas obrigatórias e prepara o grafo para o algoritmo.

---

## 🏗️ Arquitetura e Organização do Código

```
ProjetoGrafos/
├── main.py                     # Executa leitura, heurísticas e salva solução
├── leitura.py                 # Lê e interpreta os arquivos .dat
├── heuristicas.py             # GRASP, savings, fusão de rotas, heurística utilizada na etapa 2 
├── opt2.py                    # 2-opt para melhorar rotas
├── path_scanning.py           # Gera população inicial
├── melhoramento_local.py      # Realocação de tarefas entre rotas
├── GrafosDeTeste/             # Instâncias de entrada
├── SolucoesEsperadas/         # Gabaritos de referência
├── SolucoesGeradas/           # Saídas do seu algoritmo
```

---

## ⚙️ Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior
- Recomendado: ambiente virtual

### Instalação

```bash
git clone https://github.com/mvk999/ProjetoGrafos.git
cd ProjetoGrafos
pip install -r requirements.txt
```

### Execução

```bash
python main.py
```

As soluções são salvas automaticamente na pasta `G19`.

---

## 🧾 Formato da Saída

Cada instância gera um `.dat` com a seguinte estrutura:

```
0 1 <id_rota> <demanda_total> <custo_total> <qtd_serviços> (D 0,1,1) (S id,origem,destino) ... (D 0,1,1)
```

- `D` representa ida/volta ao depósito
- `S` representa tarefas obrigatórias (arestas/arcos/vértices)
- O cabeçalho inclui custo total, número de rotas e clocks de execução

---

## 👤 Autor
**Gustavo Martins**
Desenvolvedor da aprimoração path_scanning e aplicação do concurrent futures.

**Marcos Vinícius Pereira**  
Desenvolvedor principal da heurística e da estrutura do ProjetoGrafos.

---

## 📬 Contato

- GitHub: [@mvk999](https://github.com/mvk999)
- GitHub: [@Gustavo-Martins610](https://github.com/Gustavo-Martins610)
- LinkedIn: [Marcos Vinícius Pereira](https://www.linkedin.com/in/mvpereira2006)


## 📜 Licença

Este projeto é apenas para fins acadêmicos.
