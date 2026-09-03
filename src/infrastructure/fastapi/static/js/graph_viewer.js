/**
 * graph_viewer.js - Controlador de renderizado e interacción de grafo con Vis.js
 */

let networkInstance = null;

function initPertGraph(graphData) {
    const container = document.getElementById('network-container');
    if (!container) return;

    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges)
    };

    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'LR',        // De izquierda a derecha
                sortMethod: 'directed',
                levelSeparation: 220,
                nodeSpacing: 160,
                treeSpacing: 200,
                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true
            }
        },
        physics: {
            hierarchicalRepulsion: {
                centralGravity: 0.0,
                springLength: 100,
                springConstant: 0.01,
                nodeDistance: 160,
                damping: 0.09
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            navigationButtons: true,
            keyboard: true
        },
        nodes: {
            shape: 'box',
            margin: 12,
            shadow: true
        },
        edges: {
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'horizontal',
                roundness: 0.4
            },
            arrows: {
                to: { enabled: true, scaleFactor: 1.1 }
            }
        }
    };

    networkInstance = new vis.Network(container, data, options);

    // Evento de selección de nodo
    networkInstance.on('selectNode', function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const nodeData = graphData.nodes.find(n => n.id === nodeId);
            if (nodeData) {
                showNodeDetails(nodeData);
            }
        }
    });

    // Deselección
    networkInstance.on('deselectNode', function () {
        hideNodeDetails();
    });
}

function showNodeDetails(node) {
    const detailsCard = document.getElementById('node-details-card');
    if (!detailsCard) return;

    detailsCard.classList.remove('hidden');

    document.getElementById('detail-node-id').textContent = node.id;
    document.getElementById('detail-node-status').innerHTML = node.is_critical
        ? '<span class="badge badge-error text-white font-bold">Actividad Crítica</span>'
        : '<span class="badge badge-success text-white">No Crítica</span>';

    document.getElementById('detail-node-dur').textContent = node.duration;
    document.getElementById('detail-node-es').textContent = node.early_start;
    document.getElementById('detail-node-ef').textContent = node.early_finish;
    document.getElementById('detail-node-ls').textContent = node.late_start;
    document.getElementById('detail-node-lf').textContent = node.late_finish;
    document.getElementById('detail-node-slack').textContent = node.total_slack;
}

function hideNodeDetails() {
    const detailsCard = document.getElementById('node-details-card');
    if (detailsCard) {
        detailsCard.classList.add('hidden');
    }
}

function fitGraph() {
    if (networkInstance) {
        networkInstance.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
    }
}

function togglePhysics() {
    if (networkInstance) {
        const isPhysicsEnabled = networkInstance.physics.physicsEnabled;
        networkInstance.setOptions({ physics: { enabled: !isPhysicsEnabled } });
        const btn = document.getElementById('btn-toggle-physics');
        if (btn) {
            btn.textContent = !isPhysicsEnabled ? 'Física: ON' : 'Física: OFF';
        }
    }
}
