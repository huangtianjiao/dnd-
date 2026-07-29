"use client";

interface HITLDialogProps {
  question: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function HITLDialog({ question, onConfirm, onCancel }: HITLDialogProps) {
  return (
    <div className="modal-overlay visible" onClick={onCancel}>
      <div className="modal" style={{ maxWidth: 400 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="mh-title">⚠️ DM 确认</span>
          <button className="modal-close" onClick={onCancel}>✕</button>
        </div>
        <div className="modal-body">
          <div style={{
            fontSize: 13,
            lineHeight: 1.7,
            color: "var(--text-primary)",
            marginBottom: 16,
            whiteSpace: "pre-wrap",
          }}>
            {question}
          </div>
          <div className="flex-row" style={{ gap: 8 }}>
            <button className="btn btn-primary" style={{ flex: 1 }} onClick={onConfirm}>
              ✓ 确认
            </button>
            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onCancel}>
              ✕ 取消
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
