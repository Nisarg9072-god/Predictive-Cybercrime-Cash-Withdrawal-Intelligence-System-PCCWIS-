import ReactFlow, { 
  Background, 
  Controls, 
  MarkerType,
  useNodesState,
  useEdgesState
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import './TransactionGraph.css';
import { useMemo, useState, useEffect } from 'react';
import { X, User, Hash, AlertTriangle, CheckCircle, HelpCircle, Activity } from 'lucide-react';

interface NetworkProps {
  nodesData: { id: string; label: string; riskType: string; amount?: string; details?: string }[];
  edgesData: { source: string; target: string; amount: string; riskType: string; timestamp?: string }[];
}

export function TransactionGraph({ nodesData, edgesData }: NetworkProps) {
  
  const initialNodes: Node[] = useMemo(() => {
    return nodesData.map((n, i) => ({
      id: n.id,
      position: { x: 100 + (i * 200), y: 150 + (i % 2 === 0 ? 50 : -50) },
      data: { ...n },
      className: `custom-node node-${n.riskType}`
    }));
  }, [nodesData]);

  const initialEdges: Edge[] = useMemo(() => {
    return edgesData.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
      label: e.amount,
      animated: true,
      className: `custom-edge edge-${e.riskType}`,
      labelBgStyle: { fill: 'var(--bg-panel)', color: '#fff', fontSize: 12 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: e.riskType === 'critical' ? 'var(--status-critical)' : e.riskType === 'warning' ? 'var(--status-warning)' : 'var(--status-safe)',
      },
      style: {
        stroke: e.riskType === 'critical' ? 'var(--status-critical)' : e.riskType === 'warning' ? 'var(--status-warning)' : 'var(--status-safe)',
        strokeWidth: 2,
      },
      data: e
    }));
  }, [edgesData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    setSelectedNode(null);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data);
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactFlow 
        nodes={nodes} 
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="var(--border-subtle)" gap={16} />
        <Controls showInteractive={false} />
      </ReactFlow>
      
      {selectedNode && (
        <div style={{ 
          position: 'absolute', top: 16, right: 16, width: '280px', 
          backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border-strong)', 
          borderRadius: 'var(--radius-md)', padding: '1.25rem', boxShadow: 'var(--shadow-lg)' 
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0, fontSize: '0.875rem' }}>
              {selectedNode.riskType === 'critical' ? <AlertTriangle size={16} className="text-critical" /> : 
               selectedNode.riskType === 'safe' ? <CheckCircle size={16} className="text-safe" /> : 
               selectedNode.riskType === 'warning' ? <AlertTriangle size={16} className="text-warning" /> : 
               <HelpCircle size={16} />}
              {selectedNode.label}
            </h4>
            <button onClick={() => setSelectedNode(null)} style={{ color: 'var(--text-muted)' }}>
              <X size={16} />
            </button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
              <Hash size={14} /> ID: <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{selectedNode.id}</span>
            </div>
            {selectedNode.details && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <User size={14} /> Details: <span style={{ color: 'var(--text-primary)' }}>{selectedNode.details}</span>
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
              <Activity size={14} /> Risk: <span style={{ textTransform: 'uppercase', fontWeight: 600, color: `var(--status-${selectedNode.riskType === 'safe' ? 'safe' : selectedNode.riskType})` }}>{selectedNode.riskType}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
