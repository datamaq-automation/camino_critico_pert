# SRS-SPECS: Sistema de Camino Crítico (CPM / PERT) — Single Source of Truth (SSOT)

> **Documento:** `SRS-SPEC.md`  
> **Versión:** `1.0.0`  
> **Estado:** `Aprobado`  
> **Fecha:** `2026-09-02`  
> **Repositorio / Módulo:** `camino_critico_pert`  

---

## 1. Contexto Estratégico & Propuesta de Valor

### 1.1. Foco Estratégico & Alcance
* **Propósito del Sistema:** Proveer un motor de cálculo y visualizador interactivo de alta precisión para la gestión de proyectos mediante el **Método del Camino Crítico (CPM)** y análisis probabilístico **PERT (Program Evaluation and Review Technique)**.
* **Usuario Objetivo:** Ingenieros de proyectos, planificadores, directores de obra, docentes y estudiantes de Investigación Operativa / Gestión de Proyectos.
* **Modalidad Operativa:** Aplicación web local y desplegable en contenedores (*Cloud / On-Premise*), con arquitectura desacoplada y liviana.
* **Fuera de Alcance (*Out of Scope* — Evitando Sobreingeniería):**
  - **Base de Datos / ORM:** No se requiere persistencia en disco ni motores relacionales; el procesamiento se realiza en memoria (*In-Memory*) en tiempo real.
  - **Autenticación y RBAC (JWT/OAuth2):** Acceso libre e inmediato como herramienta de ingeniería (*Zero-Friction Tool*).
  - **Brokers de Mensajería / Workers Asíncronos (Kafka/RabbitMQ/Redis):** Procesamiento sincrónico directo en CPU (< 10 ms por cálculo).

### 1.2. Pilares de Valor de la Solución
| Pilar | Enfoque | Implementación en este Sistema |
| :--- | :--- | :--- |
| **1. Dominio Puro & Rigor Matemático** | Algoritmos de grafos determinísticos y probabilísticos sin dependencias externas. | Forward/Backward pass, holguras total/libre, cálculo de $\mu$, $\sigma^2$ y función normal acumulada en `src/domain/pert/`. |
| **2. Visualización Interactiva & UX** | Diagramas de red claros y manipulables en tiempo real. | Nodos estilo *Activity-on-Node* (AON) con `vis-network`, camino crítico resaltado en rojo neón y exportación a `Mermaid.js`. |
| **3. Arquitectura Limpia & Simplicidad** | Desacoplamiento estricto y código mantenible sin sobreingeniería. | Clean Architecture canónica (4 círculos de Uncle Bob), validación AST y cero dependencias innecesarias. |

---

## 2. Modelo Operativo & Gobernanza

* **Control de Calidad Automatizado:** Guantelete de Restricciones AST (`tests/test_architecture.py`) que valida la pureza del dominio, la ausencia de imports relativos y el tipado estricto.
* **Entrega Continua & Verificación:** 100% de tests unitarios, de integración y E2E pasando antes de cualquier cambio.

---

## 3. Especificación de Requisitos de Software (SRS)

### 3.1. Requisitos Funcionales (FR)
* **FR-01 - Ingesta y Validación de Actividades:** El sistema debe procesar solicitudes web y API validando estrictamente identificadores, nombres, duraciones ($o \le m \le p$) y dependencias mediante Pydantic v2.
* **FR-02 - Procesamiento en Memoria (In-Memory Processing):** El sistema debe procesar y resolver el proyecto en tiempo real sin requerir conexiones ni transacciones en bases de datos relacionales o NoSQL.
* **FR-03 - Detección de Ciclos y Validación de DAG:** El sistema debe validar que la red de actividades sea un Grafo Dirigido Acíclico (DAG), detectando y notificando cualquier ciclo cerrado tanto a nivel dominio (algoritmo de Kahn) como en infraestructura (`NetworkX`).
* **FR-04 - Cálculo de Camino Crítico (CPM):**
  - Realizar el *Forward Pass* para calcular Inicio Temprano ($ES$) y Fin Temprano ($EF$).
  - Realizar el *Backward Pass* para calcular Fin Tardío ($LF$) e Inicio Tardío ($LS$).
  - Calcular Holgura Total ($HT = LF - EF$) y Holgura Libre ($HL = \min(ES_{succ}) - EF$).
  - Identificar todas las secuencias completas de actividades críticas ($HT = 0$).
* **FR-05 - Análisis Probabilístico (PERT):**
  - Calcular la duración esperada $t_e = (o + 4m + p)/6$ y varianza $\sigma^2 = ((p - o)/6)^2$.
  - Calcular la desviación estándar del camino crítico $\sigma_{\text{proyecto}} = \sqrt{\sum \sigma_{\text{crítico}}^2}$.
  - Calcular el $Z$-score y la probabilidad acumulada $P(T \le T_{\text{meta}})$ si se especifica un plazo objetivo.
* **FR-06 - Visualización Gráfica Interactiva:**
  - Renderizar el grafo de red interactivo con `vis-network` (AON, zoom, pan, arrastre de nodos y panel inspector al hacer clic).
  - Resaltar visualmente las aristas y nodos del Camino Crítico en color rojo vibrante.
  - Proveer código sintáctico para renderizado y exportación con `Mermaid.js`.
* **FR-07 - API REST JSON & Web UI:**
  - Exponer endpoints OpenAPI documentados en `/api/v1/pert/calculate` y `/api/v1/pert/validate-dag`.
  - Exponer interfaz web interactiva con plantillas Jinja2, Tailwind CSS y DaisyUI en `/`.

### 3.2. Requisitos No Funcionales (NFR)
* **NFR-01 - Latencia de Cálculo:** El cálculo de un grafo de hasta 500 actividades debe ejecutarse en menos de 20 ms en CPU.
* **NFR-02 - Pureza Arquitectónica:** 0 dependencias externas en la capa de Dominio (`src/domain/pert/`).
* **NFR-03 - Tipado Estricto Exhaustivo:** 100% de funciones tipadas en parámetros y retornos validadas por Pyright (0 errores).
* **NFR-04 - Conformidad del Guantelete AST:** Superar el 100% de las 5 baterías de `tests/test_architecture.py`.

---

## 4. Stack Tecnológico, Arquitectura Limpia & Convenciones

### 4.1. Stack Tecnológico Base
* **Lenguaje:** Python 3.12+ (Tipado estricto con `typing`, `dataclasses`).
* **Arquitectura:** Clean Architecture Canónica (4 Círculos de Uncle Bob) + Screaming DDD.
* **Framework Web:** FastAPI + Uvicorn.
* **Motor de Plantillas & UI:** Jinja2 + Tailwind CSS + DaisyUI (vía CDN).
* **Librerías de Grafos:**
  - Backend: `networkx` (análisis topológico, métricas y validación de DAGs en infraestructura).
  - Frontend: `vis-network` (Vis.js CDN para grafos interactivos AON) y `mermaid.js` (diagramas markdown).
* **Validación & Schemas:** Pydantic v2 (`BaseModel`, `Field`, `ConfigDict`).
* **Configuración Centralizada:** `pydantic-settings` (`BaseSettings`).
* **Testing & Calidad:** Pytest, pytest-asyncio, HTTPX, Ruff (linter/formatter) y Pyright.

### 4.2. Estructura Canónica de Directorios

```
camino_critico_pert/
├── .env                                         # Variables de entorno locales
├── .env.example                                 # Plantilla de variables de entorno
├── .gitignore                                   # Exclusiones estándar (.env, .venv, etc.)
├── pyproject.toml                               # Configuración de proyecto y herramientas
├── pyrightconfig.json                           # Configuración Pyright / Pylance
├── .vscode/settings.json                        # Exclusiones LSP para el editor
│
├── src/
│   ├── domain/                                  # CÍRCULO 1: Reglas de Negocio Puras (DDD)
│   │   └── pert/
│   │       ├── entities.py                      # Activity, CriticalPathResult, ProbabilityResult
│   │       ├── value_objects.py                 # DurationEstimate, TimeWindow
│   │       ├── services.py                      # CpmPertCalculator, PertProbabilityCalculator
│   │       └── exceptions.py                    # CycleDetectedError, InvalidDurationError, etc.
│   │
│   ├── application/                             # CÍRCULO 2: Casos de Uso
│   │   └── pert/
│   │       ├── dtos/                            # ActivityInputDTO, CriticalPathResponseDTO, etc.
│   │       ├── mappers/                         # PertMapper (DTO <-> Domain)
│   │       └── use_cases/                       # CalculateCriticalPathUseCase
│   │
│   ├── adapters/                                # CÍRCULO 3: Interface Adapters
│   │   └── pert/
│   │       ├── controllers/                     # PertController
│   │       └── presenters/                      # PertGraphPresenter (Vis.js y Mermaid.js)
│   │
│   ├── infrastructure/                          # CÍRCULO 4: Frameworks, UI & Drivers
│   │   ├── graph/                               # NetworkXAdapter (validación de DAGs con NetworkX)
│   │   ├── fastapi/
│   │   │   ├── dependencies.py                  # Inyectores de dependencias
│   │   │   ├── routers/                         # web_routes.py (HTML) y api_v1.py (JSON)
│   │   │   ├── templates/                       # Plantillas Jinja2 (base.html, index.html, result.html)
│   │   │   └── static/                          # CSS y graph_viewer.js (Vis.js controller)
│   │   └── settings/                            # Configuración tipada (config.py) y logger.py
│   │
│   └── main.py                                  # Entrypoint ASGI FastAPI (create_app)
│
└── tests/
    ├── test_architecture.py                     # Guantelete AST de 5 Baterías
    ├── unit/                                    # Pruebas unitarias de CPM, PERT y probabilidades
    ├── integration/                             # Pruebas de integración de NetworkXAdapter
    └── e2e/                                     # Pruebas de endpoints REST y rutas Jinja2
```

---

## 5. Las Siete Reglas Innegociables de Arquitectura

1. **Regla de Dependencia de Capas:**
   - `domain` nunca importa de capas externas (`application`, `adapters`, `infrastructure`) ni librerías de terceros (0 dependencias).
   - `application` solo depende de `domain` y `pydantic`.
   - `adapters` depende de `application` y `domain` (nunca de `infrastructure`).
   - `infrastructure` aísla frameworks web, librerías gráficas y drivers.
2. **Archivos `__init__.py` de 0 Bytes:**
   - El 100% de los archivos `__init__.py` en `src/` y `tests/` deben estar completamente vacíos (0 bytes).
3. **Pragmatismo sin Sobreingeniería:**
   - Componentes no requeridos (Bases de datos relacionales, brokers asíncronos, RBAC) se excluyen para mantener la máxima velocidad y simplicidad operativa.
4. **Gobernanza de Parámetros Críticos:**
   - Fórmulas de ingeniería centralizadas en el Dominio; configuración de entorno centralizada en `Settings`.
5. **Controladores Delgados (*Thin Controllers*):**
   - Los routers de FastAPI no contienen lógica algorítmica ni de negocio; delegan exclusivamente en `adapters/controllers/` o casos de uso.
6. **Imports Absolutos:**
   - Prohibidos los imports relativos. Se exige siempre sintaxis absoluta `from src....`.
7. **Tipado Estricto Exhaustivo:**
   - Toda función y método debe declarar Type Hints en sus parámetros y tipo de retorno validados por Pyright.

---

## 6. Matriz de Verificación Previa a Despliegues

Todos los cambios deben superar el 100% de la siguiente batería de comandos:

```bash
# 1. Linter y Verificación de Formato
uv run ruff check .
uv run ruff format --check .

# 2. Análisis Estático de Tipos Estricto
uv run pyright src/

# 3. Validación de Arquitectura y Guantelete AST
uv run python3 tests/test_architecture.py

# 4. Suite Completa de Pruebas Pytest
uv run pytest tests/ -v
```