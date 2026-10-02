import type { NodeProps } from 'reactflow';
import { Handle, Position } from 'reactflow'

interface BaseNodeData {
  label: string
  nodeType: string
  [key: string]: string | number | boolean | undefined
}

export const DataNode = ({ data }: NodeProps<BaseNodeData>) => (
  <div className="bg-blue-900/30 border border-blue-500/50 rounded-lg px-3 py-2 min-w-[140px]">
    <div className="flex items-center gap-2">
      <span className="text-blue-400 text-lg">📊</span>
      <div>
        <div className="font-medium text-sm">{data.label}</div>
        <div className="text-xs text-blue-300/70">{data.nodeType}</div>
      </div>
    </div>
    <Handle type="source" position={Position.Right} />
  </div>
)

export const IndicatorNode = ({ data }: NodeProps<BaseNodeData & { period?: number; fast?: number; slow?: number; signal?: number; std_dev?: number }>) => (
  <div className="bg-purple-900/30 border border-purple-500/50 rounded-lg px-3 py-2 min-w-[160px]">
    <Handle type="target" position={Position.Left} />
    <div className="flex items-center gap-2 mb-1">
      <span className="text-purple-400 text-lg">📈</span>
      <div className="flex-1">
        <div className="font-medium text-sm">{data.label}</div>
        <div className="text-xs text-purple-300/70">{data.nodeType}</div>
      </div>
    </div>
    {data.period && (
      <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
        <span>Period:</span>
        <input
          type="number"
          value={data.period}
          onChange={() => {}}
          className="w-16 px-1 py-0.5 bg-purple-900/50 border border-purple-500/30 rounded text-white text-xs focus:outline-none focus:ring-1 focus:ring-purple-500"
          min="1"
          max="500"
        />
      </div>
    )}
    {data.fast && data.slow && (
      <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
        <span>Fast:</span>
        <input type="number" value={data.fast} className="w-12 px-1 py-0.5 bg-purple-900/50 border border-purple-500/30 rounded text-white text-xs" min="1" max="100" />
        <span>Slow:</span>
        <input type="number" value={data.slow} className="w-12 px-1 py-0.5 bg-purple-900/50 border border-purple-500/30 rounded text-white text-xs" min="1" max="200" />
      </div>
    )}
    <Handle type="source" position={Position.Right} />
  </div>
)

export const LogicNode = ({ data }: NodeProps<BaseNodeData>) => (
  <div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg px-3 py-2 min-w-[140px]">
    <Handle type="target" position={Position.Left} id="a" />
    <Handle type="target" position={Position.Left} id="b" style={{ top: '100%' }} />
    <div className="flex items-center justify-center gap-2">
      <span className="text-yellow-400 text-lg">⚙️</span>
      <div className="font-medium text-sm">{data.label}</div>
    </div>
    <Handle type="source" position={Position.Right} />
  </div>
)

export const ActionNode = ({ data }: NodeProps<BaseNodeData>) => (
  <div className="bg-green-900/30 border border-green-500/50 rounded-lg px-3 py-2 min-w-[140px]">
    <Handle type="target" position={Position.Left} />
    <div className="flex items-center gap-2">
      <span className="text-green-400 text-lg">🎯</span>
      <div>
        <div className="font-medium text-sm">{data.label}</div>
        <div className="text-xs text-green-300/70">{data.nodeType}</div>
      </div>
    </div>
  </div>
)

export const RiskNode = ({ data }: NodeProps<BaseNodeData & { risk_pct?: number; pct?: number }>) => (
  <div className="bg-red-900/30 border border-red-500/50 rounded-lg px-3 py-2 min-w-[160px]">
    <Handle type="target" position={Position.Left} />
    <div className="flex items-center gap-2 mb-1">
      <span className="text-red-400 text-lg">🛡️</span>
      <div className="flex-1">
        <div className="font-medium text-sm">{data.label}</div>
        <div className="text-xs text-red-300/70">{data.nodeType}</div>
      </div>
    </div>
    {data.risk_pct && (
      <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
        <span>Risk %:</span>
        <input
          type="number"
          value={data.risk_pct}
          className="w-16 px-1 py-0.5 bg-red-900/50 border border-red-500/30 rounded text-white text-xs"
          min="0.1"
          max="10"
          step="0.1"
        />
      </div>
    )}
    {data.pct && (
      <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
        <span>%:</span>
        <input type="number" value={data.pct} className="w-16 px-1 py-0.5 bg-red-900/50 border border-red-500/30 rounded text-white text-xs" min="0.1" max="50" step="0.1" />
      </div>
    )}
    <Handle type="source" position={Position.Right} />
  </div>
)