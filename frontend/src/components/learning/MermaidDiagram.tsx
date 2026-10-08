import React, { useEffect, useId, useState } from 'react';
import mermaid from 'mermaid';
import { Network, Copy, Check, AlertCircle } from 'lucide-react';

interface MermaidDiagramProps {
  code: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  securityLevel: 'strict',
  fontFamily: 'Inter, system-ui, sans-serif',
});

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ code }) => {
  const uniqueId = useId().replace(/:/g, '_');
  const [svgContent, setSvgContent] = useState<string>('');
  const [hasError, setHasError] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const cleanCode = code.trim();

    const renderChart = async () => {
      try {
        setHasError(false);
        const { svg } = await mermaid.render(`mermaid_${uniqueId}`, cleanCode);
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err) {
        console.warn('Failed to render Mermaid diagram:', err);
        if (isMounted) {
          setHasError(true);
        }
      }
    };

    if (cleanCode) {
      renderChart();
    }

    return () => {
      isMounted = false;
    };
  }, [code, uniqueId]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (hasError) {
    return (
      <div className="my-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs font-mono text-slate-700">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200 text-slate-500 font-sans">
          <span className="flex items-center gap-1.5 font-medium">
            <AlertCircle size={14} className="text-amber-500" />
            Conceptual Diagram (Text Outline)
          </span>
          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1 hover:text-slate-900 transition-colors"
          >
            {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
        <pre className="mt-2 whitespace-pre-wrap overflow-x-auto">{code}</pre>
      </div>
    );
  }

  return (
    <div className="my-4 rounded-xl border border-indigo-100 bg-gradient-to-b from-white to-slate-50 shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-slate-100 bg-slate-50/80 text-xs font-medium text-slate-600">
        <span className="flex items-center gap-1.5 text-indigo-700 font-semibold">
          <Network size={14} className="text-indigo-600" />
          Interactive Conceptual Architecture
        </span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-slate-900 text-slate-500 transition-colors"
          title="Copy diagram source syntax"
        >
          {copied ? (
            <>
              <Check size={12} className="text-emerald-600" />
              <span className="text-emerald-600 font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy size={12} />
              <span>Copy Diagram</span>
            </>
          )}
        </button>
      </div>
      <div
        className="p-4 flex justify-center items-center overflow-x-auto min-h-[120px] [&_svg]:max-w-full [&_svg]:h-auto"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
};
