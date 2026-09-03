# 📊 Sistema de Camino Crítico (CPM / PERT)

Aplicación web interactiva para la gestión de proyectos, cálculo determinístico del **Método del Camino Crítico (CPM)** y análisis probabilístico **PERT (Program Evaluation and Review Technique)**. 

Desarrollada con **FastAPI**, plantillas **Jinja2**, motor de grafos con **NetworkX**, visualización interactiva mediante **Vis.js (`vis-network`)** y diagramación complementaria con **Mermaid.js**, bajo los principios de **Clean Architecture** (Uncle Bob) y **Screaming DDD**.

---

## 🚀 Características Principales

- **Doble Modalidad de Entrada**:
  - **CPM Determinístico**: Permite ingresar duraciones fijas conocidas para cada tarea.
  - **PERT Probabilístico**: Permite ingresar las 3 estimaciones clásicas: *Optimista ($o$)*, *Más Probable ($m$)* y *Pesimista ($p$)*.
- **Cálculo Algorítmico Canónico (Dominio Puro)**:
  - **Forward Pass (Ida)**: Inicio Temprano ($ES$) y Fin Temprano ($EF$).
  - **Backward Pass (Vuelta)**: Fin Tardío ($LF$) e Inicio Tardío ($LS$).
  - **Holgura Total y Holgura Libre**: Detección exacta de márgenes de demora admisibles.
  - **Detección de Múltiples Caminos Críticos**: Identificación de todas las trayectorias críticas continuas ($HT = 0$).
  - **Análisis Estadístico PERT**: Duración esperada ($T_e$), varianza acumulada ($\sigma^2$), desviación estándar ($\sigma$), cálculo de $Z$-score y probabilidad de cumplimiento $P(T \le T_{\text{meta}})$ con distribución normal estándar.
- **Visualización de Grafos Interactiva**:
  - **`vis-network` (Vis.js)**: Grafo dirigido interactivo *Activity-on-Node* (AON) con layout jerárquico horizontal (Left-to-Right), nodos arrastrables, zoom, física ajustable, inspector flotante al hacer clic en cualquier actividad y **resaltado del Camino Crítico en rojo**.
  - **`mermaid.js`**: Generador automático de sintaxis `graph LR` con estilos listos para copiar a documentación Markdown.
- **Validación Topológica con NetworkX**: Verificación matemática de Grafos Dirigidos Acíclicos (DAGs) y detección explícita de ciclos cerrados antes del procesamiento.
- **REST JSON API**: Endpoints OpenAPI documentados para integración con otros sistemas.

---

## 📐 Fundamentos Matemáticos

1. **Tiempo Esperado y Varianza (PERT)**:
   $$t_e = \frac{o + 4m + p}{6}$$
   $$\sigma^2 = \left(\frac{p - o}{6}\right)^2$$

2. **Pase hacia Adelante (Forward Pass)**:
   $$ES_j = \max_{i \in \text{Pred}(j)}(EF_i) \quad (ES = 0 \text{ para actividades iniciales})$$
   $$EF_j = ES_j + t_{e,j}$$

3. **Pase hacia Atrás (Backward Pass)**:
   $$LF_i = \min_{j \in \text{Succ}(i)}(LS_j) \quad (LF = \max(EF) \text{ para actividades finales})$$
   $$LS_i = LF_i - t_{e,i}$$

4. **Holguras y Criticidad**:
   $$\text{Holgura Total } (HT_i) = LF_i - EF_i = LS_i - ES_i$$
   $$\text{Holgura Libre } (HL_i) = \min_{j \in \text{Succ}(i)}(ES_j) - EF_i$$
   $$\text{Actividad Crítica } \iff HT_i = 0$$

5. **Probabilidad de Culminación en Plazo Meta ($T_{\text{meta}}$)**:
   $$\sigma_{\text{proyecto}} = \sqrt{\sum_{k \in \text{Camino Crítico}} \sigma_k^2}$$
   $$Z = \frac{T_{\text{meta}} - T_{\text{proyecto}}}{\sigma_{\text{proyecto}}}$$
   $$P(T \le T_{\text{meta}}) = \Phi(Z) = \frac{1}{2} \left[1 + \text{erf}\left(\frac{Z}{\sqrt{2}}\right)\right]$$

---

## 🏗️ Arquitectura del Proyecto (Clean Architecture & Screaming DDD)

El proyecto sigue una separación estricta en 4 capas concéntricas:

```
src/
├── domain/                                     # CÍRCULO 1: Reglas de Negocio Puras (0 dependencias)
│   └── pert/
│       ├── entities.py                         # Activity, CriticalPathResult, ProbabilityResult
│       ├── value_objects.py                    # DurationEstimate, TimeWindow
│       ├── services.py                         # CpmPertCalculator, PertProbabilityCalculator
│       └── exceptions.py                       # CycleDetectedError, ActivityNotFoundError, etc.
│
├── application/                                # CÍRCULO 2: Casos de Uso y Orquestación
│   └── pert/
│       ├── dtos/                               # Request/Response DTOs con Pydantic v2
│       ├── mappers/                            # Traductores bidireccionales DTO <-> Entidad
│       └── use_cases/                          # CalculateCriticalPathUseCase
│
├── adapters/                                   # CÍRCULO 3: Adaptadores de Interfaz
│   └── pert/
│       ├── controllers/                        # PertController desacoplado del framework web
│       └── presenters/                         # Generadores para Vis.js y Mermaid.js
│
├── infrastructure/                             # CÍRCULO 4: Frameworks, Drivers y Detalles
│   ├── graph/                                  # NetworkXAdapter (validación topológica de DAG)
│   ├── fastapi/
│   │   ├── dependencies.py                     # Inyección de dependencias FastAPI
│   │   ├── routers/                            # Thin Routers (web_routes.py y api_v1.py)
│   │   ├── templates/                          # Plantillas Jinja2 (base.html, index.html, result.html)
│   │   └── static/                             # JavaScript (Vis.js controller) y CSS
│   └── settings/                               # Configuración tipada y logging centralizado
│
└── main.py                                     # Entrypoint ASGI FastAPI
```

---

## 🛠️ Requisitos Previos

- **Python 3.12+**
- Gestor de paquetes **[`uv`](https://github.com/astral-sh/uv)** (o `pip` estándar).

---

## 📦 Instalación y Puesta en Marcha Rápida con `./run.sh`

El proyecto incluye el script ejecutable [`./run.sh`](file:///home/agustin/proyectos_software/camino_critico_pert/run.sh) que automatiza la verificación del entorno, la instalación de dependencias y el inicio del servidor:

```bash
# 1. Iniciar servidor web de desarrollo (http://127.0.0.1:8000)
./run.sh

# 2. Ejecutar la suite de pruebas Pytest
./run.sh test

# 3. Ejecutar la matriz completa de calidad (Ruff + Pyright + AST Gauntlet + Tests)
./run.sh check
```

---

### Puesta en Marcha Manual

Si prefieres ejecutar los comandos de forma manual:

1. **Crear y activar el entorno virtual con `uv`**:
   ```bash
   uv sync
   source .venv/bin/activate
   ```

2. **Iniciar el servidor de desarrollo**:
   ```bash
   uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Acceder a la aplicación**:
   - **Interfaz Web (Dashboard Jinja2)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Documentación Interactiva (Swagger / OpenAPI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Documentación ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Batería de Pruebas y Calidad de Código

Puedes ejecutar todas las verificaciones con un único comando:
```bash
./run.sh check
```

O individualmente:
```bash
# 1. Linter y formato con Ruff
uv run ruff check .
uv run ruff format --check .

# 2. Análisis estático de tipos estricto con Pyright
uv run pyright src/

# 3. Validación de Arquitectura y Guantelete AST (5 Baterías)
uv run python3 tests/test_architecture.py

# 4. Suite completa de pruebas con Pytest (21 tests)
uv run pytest tests/ -v

```

---

## 🔌 Uso de la API REST

### Calcular Camino Crítico & PERT

**Endpoint**: `POST /api/v1/pert/calculate`

**Cuerpo de la Solicitud (JSON)**:
```json
{
  "activities": [
    { "id": "A", "name": "Diseño", "optimistic": 3, "most_likely": 3, "pessimistic": 3, "predecessors": [] },
    { "id": "B", "name": "Investigación", "optimistic": 4, "most_likely": 4, "pessimistic": 4, "predecessors": [] },
    { "id": "C", "name": "Prototipo A", "optimistic": 2, "most_likely": 2, "pessimistic": 2, "predecessors": ["A"] },
    { "id": "D", "name": "Prototipo B", "optimistic": 5, "most_likely": 5, "pessimistic": 5, "predecessors": ["B"] },
    { "id": "E", "name": "Integración", "optimistic": 3, "most_likely": 3, "pessimistic": 3, "predecessors": ["C", "D"] }
  ],
  "target_duration": 14.0
}
```

**Respuesta Exitosa (`200 OK`)**:
Retorna:
- `result`: Métricas del proyecto, duración total, caminos críticos y tabla de actividades calculadas ($ES, EF, LS, LF, \text{holguras}$).
- `vis_graph`: Nodos y aristas preparados para renderizado con `vis-network`.
- `mermaid_code`: Código sintáctico de `Mermaid.js`.

---

## 📄 Licencia

Proyecto desarrollado bajo fines académicos y de ingeniería de software.
