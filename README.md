# 📈 Airflow Stock Market Pipeline

Um pipeline moderno de dados para coleta, processamento e armazenamento de preços de ações, construído com **Apache Airflow**, **Spark**, **MinIO** e **PostgreSQL**.

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Componentes Principais](#componentes-principais)
- [Fluxo de Dados](#fluxo-de-dados)
- [Configuração de Conexões](#configuração-de-conexões)
- [Comandos Úteis](#comandos-úteis)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este projeto implementa um **pipeline automatizado de dados** que:

1. **Coleta** preços de ações em tempo real da API do Yahoo Finance
2. **Valida** a disponibilidade da API através de sensores
3. **Armazena** dados brutos em um bucket MinIO (S3-compatível)
4. **Processa** e transforma os dados usando Spark
5. **Carrega** os dados transformados em um Data Warehouse PostgreSQL

O pipeline é orquestrado por **Apache Airflow** e executa automaticamente a cada dia.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Airflow (Orquestrador)               │
└─────────────────────────────────────────────────────────────────┘
           │
           ├─────────► Yahoo Finance API (Coleta de Dados)
           │
           ├─────────► MinIO / S3 (Armazenamento Bruto)
           │
           ├─────────► Spark (Processamento & Transformação)
           │
           └─────────► PostgreSQL DW (Data Warehouse)

┌─────────────────────────────────────────────────────────────────┐
│                     Infraestrutura                              │
│  • PostgreSQL (Metastore Airflow + DW)  │  • Redis (Cache)     │
│  • MinIO (Object Storage)                │  • Spark (Cluster)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Pré-requisitos

### Requisitos do Sistema
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.9+ (para ambiente local)
- **Git**
- **Mínimo 8GB de RAM** alocado para Docker

### Verificar Instalação
```bash
docker --version
docker-compose --version
python --version
```

---

## 🚀 Instalação

### 1. Clonar o Repositório
```bash
cd c:\Users\Gustavo\Documents\repositoriosGit\
```

### 2. Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env`:

```env
# AWS / MinIO Config
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
AWS_REGION=us-east-1
ENDPOINT=http://host.docker.internal:9000

# Airflow Config
AIRFLOW_UID=50000
AIRFLOW_HOME=/opt/airflow

# Banco de Dados
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Data Warehouse
DW_USER=datawarehouse
DW_PASSWORD=datawarehouse123
DW_DB=stock_dw
```

### 3. Construir e Inicializar

**Opção A: Com Docker Compose (Recomendado)**
```bash
cd docker
docker-compose up -d
```

**Opção B: Com Make**
```bash
make docker_run_airflow
```

### 4. Inicializar Airflow
```bash
make docker_build_airflow_init
```

---

## 🎮 Como Executar

### Iniciar o Pipeline via Web UI

1. **Abra o Airflow UI:**
   ```
   http://localhost:8080
   ```

2. **Credenciais padrão:**
   - Usuário: `admin`
   - Senha: `admin`

3. **Ativar a DAG:**
   - Procure por `stock_market` na lista de DAGs
   - Clique no toggle para ativar
   - A DAG executará automaticamente todos os dias
   - Ou clique em "Trigger DAG" para executar manualmente

### Monitorar Execução

**MinIO UI** (Storage):
```
http://localhost:9001
```
- Usuário: `minio`
- Senha: `minio123`

**Metabase** (Visualização de Dados):
```
http://localhost:3000
```

### Verificar Logs

```bash
# Logs do Airflow Scheduler
docker-compose logs airflow-scheduler

# Logs do Airflow Worker
docker-compose logs airflow-worker

# Logs do Spark Driver
docker-compose logs spark-master
```

---

## 📁 Estrutura do Projeto

```
airflow-udemy/
├── dags/
│   ├── dags.py                          # DAG principal (stock_market)
│   └── include/
│       └── stock_market/
│           └── tasks.py                 # Tasks do pipeline
│
├── spark/
│   ├── master/
│   │   ├── Dockerfile                  # Imagem Spark Master
│   │   └── master.sh                   # Script de inicialização
│   │
│   ├── worker/
│   │   ├── Dockerfile                  # Imagem Spark Worker
│   │   └── worker.sh                   # Script de inicialização
│   │
│   └── stock_transform/
│       ├── stock_transform.py          # Aplicação Spark (transformação)
│       ├── Dockerfile                  # Imagem da aplicação
│       └── requirements.txt            # Dependências Spark
│
├── docker/
│   ├── Dockerfile                      # Imagem Airflow customizada
│   ├── docker-compose.yml              # Orquestração de containers
│   ├── config/
│   │   └── airflow.cfg                # Configuração do Airflow
│   ├── include/
│   │   └── data/
│   │       ├── minio/                 # Buckets MinIO
│   │       └── metabase/              # Dados Metabase
│   ├── logs/                           # Logs de execução
│   ├── plugins/                        # Plugins customizados Airflow
│
├── minio/
│   └── stock_market/
│       └── tasks.py                    # Tasks do MinIO
│
├── requirements.txt                    # Dependências Python
├── Makefile                            # Comandos úteis
├── .env                                # Variáveis de ambiente
└── README.md                           # Este arquivo
```

---

## 🔧 Componentes Principais

### 1. **Apache Airflow** (Orquestrador)
- **Versão:** 3.1.3
- **Executor:** LocalExecutor (desenvolvimento)
- **Banco de Dados:** PostgreSQL
- **Interface Web:** http://localhost:8080

**Responsabilidade:**
- Orquestração e agendamento do pipeline
- Monitoramento de tasks
- Tratamento de falhas e retries
- Armazenamento de metadados

### 2. **PostgreSQL** (Banco de Dados)
- **Airflow Metastore:** Armazena metadados das DAGs e execuções
- **Data Warehouse:** Armazena dados transformados de ações

**Porta:** 5432

### 3. **MinIO** (Object Storage)
- **Compatível com S3**
- **Armazena:** Preços de ações em JSON bruto
- **Buckets:** `stock-market`
- **Portas:**
  - API: 9000
  - Console UI: 9001

### 4. **Apache Spark** (Processamento)
- **Master:** Coordena o processamento
- **Workers:** Executam tarefas distribuídas
- **Aplicação:** `stock_transform.py`
- **Portas:**
  - Master UI: 8081
  - Worker UI: 8082

**Responsabilidade:**
- Transformação de dados JSON para formato tabular
- Enriquecimento e limpeza de dados
- Processamento distribuído

### 5. **Metabase** (Visualização)
- **Porta:** 3000
- **Visualização:** Dashboards de dados de ações

---

## 📊 Fluxo de Dados

```
ETAPA 1: VALIDAÇÃO
┌─────────────────────────────────────┐
│ is_api_available (Sensor)           │
│ - Verifica se API Yahoo Finance OK  │
│ - Timeout: 300s, Intervalo: 30s     │
└──────────────┬──────────────────────┘
               │ (URL da API extraído via XCom)
               ▼

ETAPA 2: COLETA (Extract)
┌─────────────────────────────────────┐
│ get_stock_prices (Python Operator)  │
│ - Faz request à API Yahoo Finance   │
│ - Extrai dados do símbolo (NVDA)    │
│ - Retorna JSON com OHLCV            │
└──────────────┬──────────────────────┘
               │ (JSON extraído via XCom)
               ▼

ETAPA 3: ARMAZENAMENTO BRUTO (Load Raw)
┌─────────────────────────────────────┐
│ store_prices (Python Operator)      │
│ - Conecta ao MinIO                  │
│ - Armazena JSON em bucket           │
│ - Path: stock-market/NVDA/prices.json
└──────────────┬──────────────────────┘
               │ (Path retornado via XCom)
               ▼

ETAPA 4: TRANSFORMAÇÃO (Transform)
┌─────────────────────────────────────┐
│ format_prices (Docker Operator)      │
│ - Executa stock_transform.py no Spark│
│ - Lê JSON do MinIO                  │
│ - Transforma: JSON → Parquet        │
│ - Operações:                         │
│   - Explode arrays                  │
│   - Zip colunas                     │
│   - Converte timestamps → datas     │
└──────────────┬──────────────────────┘
               │
               ▼

ETAPA 5: COLETA DO RESULTADO
┌─────────────────────────────────────┐
│ get_formatted_csv (Python Operator) │
│ - Recupera dados transformados      │
│ - Formata para CSV                  │
└──────────────┬──────────────────────┘
               │
               ▼

ETAPA 6: CARREGAMENTO NO DW (Load)
┌─────────────────────────────────────┐
│ load_to_dw (Python Operator)        │
│ - Conecta ao PostgreSQL DW          │
│ - Insere dados transformados        │
│ - Tabela: stock_prices              │
└─────────────────────────────────────┘
```

---

## ⚙️ Configuração de Conexões

### 1. Configurar Conexão com API (Airflow)

**Admin → Connections → New**

```
Connection ID: stock_api
Connection Type: HTTP
Host: https://query2.finance.yahoo.com/v11/finance/quoteSummary/
Port: [deixar vazio]
Login: [deixar vazio]
Password: [deixar vazio]
Extra JSON:
{
    "endpoint": "v11/finance/quoteSummary/",
    "headers": {
        "User-Agent": "Mozilla/5.0"
    }
}
```

### 2. Configurar Conexão MinIO (Airflow)

**Admin → Connections → New**

```
Connection ID: minio
Connection Type: S3
Host: minio
Extra JSON:
{
    "aws_access_key_id": "minio",
    "aws_secret_access_key": "minio123",
    "endpoint_url": "http://minio:9000",
    "use_ssl": false
}
```

### 3. Configurar Conexão PostgreSQL DW (Airflow)

**Admin → Connections → New**

```
Connection ID: postgres_dw
Connection Type: Postgres
Host: postgres_dw
Database: stock_dw
Schema: public
Login: datawarehouse
Password: datawarehouse123
Port: 5432
```

---

## 📝 Comandos Úteis

### Docker

```bash
# Iniciar containers
make docker_run_airflow
# ou
cd docker && docker-compose up -d

# Parar containers
make docker_down

# Parar e remover volumes
make docker_down_vol

# Remover imagens
make docker_down_imgs

# Limpeza do sistema
make docker_system_prune

# Ver logs
docker-compose logs -f [service_name]

# Executar comando em container
docker-compose exec airflow-scheduler bash
```

### Airflow

```bash
# Criar usuário admin
make docker_run

# Listar DAGs
docker-compose exec airflow-scheduler airflow dags list

# Trigger DAG manualmente
docker-compose exec airflow-scheduler airflow dags trigger stock_market

# Ver execuções da DAG
docker-compose exec airflow-scheduler airflow dags test stock_market

# Ver status das tasks
docker-compose exec airflow-scheduler airflow tasks list stock_market
```

### Profiling & Performance

```bash
# Profile com cProfile (por tempo)
make cprofile_time

# Profile com cProfile (salvar em arquivo)
make cprofile_prof

# Visualizar profile com SnakeViz
make snakeviz
```

### Python (Ambiente Local)

```bash
# Criar ambiente virtual
make venv

# Instalar dependências
make venv_requirements

# Rodar testes
make venv_run_tests

# Remover ambiente virtual
make venv_remove
```

---

## 🐛 Troubleshooting

### 1. **"Initial job has not accepted any resources"** (Spark)
**Problema:** Tasks do Spark ficam presas no agendamento.

**Solução:**
```bash
# Reiniciar instância Airflow
docker-compose down
docker-compose up -d
```
**Nota:** Certifique-se de ter alocado **mínimo 8GB de RAM** para Docker.

### 2. **"Container ainda rodando após conclusão"**
**Problema:** Container de Spark não encerra corretamente.

**Solução:**
```bash
# Forçar parada
docker-compose down -v

# Reconstruir imagens
docker-compose up -d --build

# Reiniciar Airflow
make docker_build_airflow_init
```

### 3. **PostgreSQL não inicia (permission denied)**
**Problema:** Erro de permissão nos volumes PostgreSQL.

**Solução (Linux/Mac):**
```bash
# Ajustar permissões
sudo chown -R 999:999 ~/docker/data/postgres
```

**Solução (Docker Desktop):**
- Docker → Preferences → Resources → Reset to Defaults

### 4. **MinIO Bucket não encontrado**
**Problema:** `NoSuchBucket` ao tentar acessar.

**Solução:**
```bash
# Verificar buckets via UI: http://localhost:9001
# Criar manualmente se necessário
# Ou deixar a task _store_prices criar automaticamente
```

### 5. **Timeout na API do Yahoo Finance**
**Problema:** Sensor `is_api_available` sempre falha.

**Solução:**
- Verificar conectividade: `curl -I https://query2.finance.yahoo.com`
- Aumentar timeout no DAG (padrão: 300s)
- Verificar headers (User-Agent necessário)

### 6. **XCom não encontrado**
**Problema:** Task não consegue recuperar dados de task anterior.

**Solução:**
```bash
# Verificar dependências no DAG
# Verificar names das tasks (case-sensitive)
# Limpar XCom no Airflow UI: Admin → XCom
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- **Apache Airflow:** https://airflow.apache.org/docs/
- **Apache Spark:** https://spark.apache.org/docs/
- **MinIO:** https://docs.min.io/
- **PostgreSQL:** https://www.postgresql.org/docs/

### Endpoints Importantes
| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | admin / admin |
| MinIO | http://localhost:9001 | minio / minio123 |
| Metabase | http://localhost:3000 | [configurar] |
| PostgreSQL Airflow | localhost:5432 | airflow / airflow |
| PostgreSQL DW | localhost:5433 | datawarehouse / datawarehouse123 |
| Spark Master | http://localhost:8081 | - |

### DAG Schedule
- **Frequência:** Diária (@daily)
- **Hora:** 00:00 UTC
- **Catchup:** Desativado (não processa backfills)
- **Símbolo:** NVDA (customizável em `SYMBOL` no dags.py)

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença **Apache License 2.0** (seguindo Airflow oficial).

---

## ❓ FAQ

**P: Posso usar para múltiplos símbolos de ações?**  
R: Sim! Altere a variável `SYMBOL` em `dags.py` ou crie múltiplas DAGs parametrizadas.

**P: Como carregar dados históricos?**  
R: Ative `catchup=True` no decorator `@dag` e mude `start_date` no dags.py.

**P: Posso usar em produção?**  
R: Este projeto usa LocalExecutor para desenvolvimento. Para produção, considere:
- CeleryExecutor com Redis
- KubernetesExecutor
- Implementar autenticação robusta
- Adicionar monitoramento (Datadog, New Relic)

**P: Como adicionar novas transformações Spark?**  
R: Edite `spark/stock_transform/stock_transform.py` e reconstrua com `docker-compose up -d --build`.

---

## 📞 Suporte

Para dúvidas ou problemas, abra uma **Issue** neste repositório ou entre em contato com os mantenedores.

---

**Última atualização:** Abril 2026  
**Mantido por:** Gustavo