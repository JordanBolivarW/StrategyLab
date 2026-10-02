import { useCallback, useState } from 'react'
import ReactFlow, {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  MarkerType,
  Background,
  Controls,
  MiniMap,
  type NodeTypes,
  type NodeChange,
  type EdgeChange,
  type Connection,
  type NodeDragHandler,
} from 'reactflow'
import 'reactflow/dist/style.css'
import type { StrategyGraph as StrategyGraphType, StrategyNode, StrategyEdge } from '@/types/strategy'
import { DataNode, IndicatorNode, LogicNode, ActionNode, RiskNode } from './NodeTypes'

interface StrategyGraphProps {
  strategyId: string | null
  initialGraph?: StrategyGraphType
  onChange: (graph: StrategyGraphType) => void
  readOnly?: boolean
}

const initialNodes: StrategyNode[] = [
  { id: '1', type: 'data', position: { x: 100, y: 100 }, data: { label: 'Close', nodeType: 'data.close' } },
  { id: '2', type: 'indicator', position: { x: 350, y: 50 }, data: { label: 'EMA 20', nodeType: 'indicator.ema', period: 20 } },
  { id: '3', type: 'indicator', position: { x: 350, y: 200 }, data: { label: 'EMA 50', nodeType: 'indicator.ema', period: 50 } },
  { id: '4', type: 'logic', position: { x: 600, y: 125 }, data: { label: 'Cross Above', nodeType: 'logic.cross_above' } },
  { id: '5', type: 'action', position: { x: 850, y: 125 }, data: { label: 'Buy', nodeType: 'action.buy' } },
]

const initialEdges: StrategyEdge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3', animated: true },
  { id: 'e2-4', source: '2', target: '4', sourceHandle: 'output', targetHandle: 'input-a', animated: true },
  { id: 'e3-4', source: '3', target: '4', sourceHandle: 'output', targetHandle: 'input-b', animated: true },
  { id: 'e4-5', source: '4', target: '5', sourceHandle: 'output', targetHandle: 'input', animated: true },
]

const nodeTypes: NodeTypes = {
  data: DataNode,
  indicator: IndicatorNode,
  logic: LogicNode,
  action: ActionNode,
  risk: RiskNode,
}

const PALETTE_CATEGORIES = [
  {
    title: 'Data',
    items: [
      { nodeType: 'data.open', label: 'Open' },
      { nodeType: 'data.high', label: 'High' },
      { nodeType: 'data.low', label: 'Low' },
      { nodeType: 'data.close', label: 'Close' },
      { nodeType: 'data.volume', label: 'Volume' },
    ],
  },
  {
    title: 'Indicators',
    items: [
      { nodeType: 'indicator.sma', label: 'SMA' },
      { nodeType: 'indicator.ema', label: 'EMA' },
      { nodeType: 'indicator.rsi', label: 'RSI' },
      { nodeType: 'indicator.macd', label: 'MACD' },
      { nodeType: 'indicator.atr', label: 'ATR' },
      { nodeType: 'indicator.bollinger_bands', label: 'BB' },
    ],
  },
  {
    title: 'Comparators',
    items: [
      { nodeType: 'logic.gt', label: '>' },
      { nodeType: 'logic.lt', label: '<' },
      { nodeType: 'logic.gte', label: '>=' },
      { nodeType: 'logic.lte', label: '<=' },
      { nodeType: 'logic.cross_above', label: 'Cross ↑' },
      { nodeType: 'logic.cross_below', label: 'Cross ↓' },
    ],
  },
  {
    title: 'Logic',
    items: [
      { nodeType: 'logic.and', label: 'AND' },
      { nodeType: 'logic.or', label: 'OR' },
      { nodeType: 'logic.not', label: 'NOT' },
    ],
  },
  {
    title: 'Actions',
    items: [
      { nodeType: 'action.buy', label: 'Buy' },
      { nodeType: 'action.sell', label: 'Sell' },
      { nodeType: 'action.long', label: 'Long' },
      { nodeType: 'action.short', label: 'Short' },
      { nodeType: 'action.close', label: 'Close' },
    ],
  },
  {
    title: 'Risk',
    items: [
      { nodeType: 'risk.position_size', label: 'Position Size' },
      { nodeType: 'risk.stop_loss', label: 'Stop Loss' },
      { nodeType: 'risk.take_profit', label: 'Take Profit' },
    ],
  },
]

const ICONS: Record<string, React.ReactNode> = {
  data: <span className="text-blue-400">📊</span>,
  indicator: <span className="text-purple-400">📈</span>,
  logic: <span className="text-yellow-400">⚙️</span>,
  action: <span className="text-green-400">🎯</span>,
  risk: <span className="text-red-400">🛡️</span>,
}

function NodePaletteItem({ nodeType, label }: { nodeType: string; label: string }) {
  const category = nodeType.split('.')[0]

  return (
    <div
      className="node-item"
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('application/reactflow', JSON.stringify({ nodeType, label }))
        e.dataTransfer.effectAllowed = 'copy'
      }}
    >
      {ICONS[category]}
      <span className="text-sm">{label}</span>
    </div>
  )
}

export default function StrategyGraph({
  strategyId,
  initialGraph,
  onChange,
  readOnly = false,
}: StrategyGraphProps) {
  const [nodes, setNodes] = useState<StrategyNode[]>(initialGraph?.nodes || initialNodes)
  const [edges, setEdges] = useState<StrategyEdge[]>(initialGraph?.edges || initialEdges)

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds: StrategyNode[]) => {
      const newNodes = applyNodeChanges(changes, nds) as StrategyNode[]
      if (!readOnly) {
        onChange({ nodes: newNodes, edges, metadata: {} })
      }
      return newNodes
    })
  }, [edges, onChange, readOnly])

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds: StrategyEdge[]) => applyEdgeChanges(changes, eds) as StrategyEdge[])
  }, [])

  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds: StrategyEdge[]) => {
      const newEdges = addEdge(
        { ...connection, type: 'smoothstep', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
        eds
      ) as StrategyEdge[]
      if (!readOnly) {
        onChange({ nodes, edges: newEdges, metadata: {} })
      }
      return newEdges
    })
  }, [nodes, onChange, readOnly])

  const onNodeDragStop: NodeDragHandler = useCallback((_event, _node) => {
    if (!readOnly) {
      onChange({ nodes, edges, metadata: {} })
    }
  }, [nodes, edges, onChange, readOnly])

  return (
    <div className="strategy-graph-container flex h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        nodeTypes={nodeTypes}
        fitView={!strategyId}
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={!readOnly}
      >
        <Background color="#1e293b" gap={16} />
        <Controls />
        <MiniMap />
      </ReactFlow>

      <div className="node-panel w-64 border-l border-dark-border bg-dark-card overflow-y-auto">
        {PALETTE_CATEGORIES.map((category) => (
          <div key={category.title} className="node-category p-4 border-b border-dark-border">
            <div className="node-category-title text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
              {category.title}
            </div>
            {category.items.map((item) => (
              <NodePaletteItem key={item.nodeType} nodeType={item.nodeType} label={item.label} />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}