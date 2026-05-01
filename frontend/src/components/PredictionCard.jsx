function pct(x) {
  return `${(x * 100).toFixed(1)}%`;
}

export default function PredictionCard({ prediction }) {
  const {
    display_name,
    available,
    error,
    label,
    confidence,
    probability_malignant,
    metrics,
  } = prediction;

  const isMalignant = label === "Malignant";

  if (!available) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900">{display_name}</h3>
        <p className="mt-2 text-xs text-rose-600">{error || "Unavailable"}</p>
        <p className="mt-1 text-[11px] text-slate-400">
          Train this model to enable it.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{display_name}</h3>
        <span
          className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
            isMalignant
              ? "bg-rose-100 text-rose-700"
              : "bg-emerald-100 text-emerald-700"
          }`}
        >
          {label}
        </span>
      </div>

      <div className="mt-4">
        <div className="flex items-baseline justify-between">
          <span className="text-xs text-slate-500">Confidence</span>
          <span className="text-lg font-bold text-slate-900">
            {pct(confidence)}
          </span>
        </div>
        <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className={`h-full ${
              isMalignant ? "bg-rose-500" : "bg-emerald-500"
            }`}
            style={{ width: `${Math.round(confidence * 100)}%` }}
          />
        </div>
      </div>

      <p className="mt-3 text-[11px] text-slate-500">
        P(Malignant) ={" "}
        <span className="font-mono">{probability_malignant.toFixed(4)}</span>
      </p>

      {metrics && (
        <dl className="mt-4 grid grid-cols-2 gap-x-3 gap-y-1 border-t border-slate-100 pt-3 text-[11px] text-slate-500">
          <dt>Test acc</dt>
          <dd className="text-right font-mono text-slate-700">
            {pct(metrics.accuracy ?? 0)}
          </dd>
          <dt>F1</dt>
          <dd className="text-right font-mono text-slate-700">
            {(metrics.f1 ?? 0).toFixed(3)}
          </dd>
          <dt>ROC-AUC</dt>
          <dd className="text-right font-mono text-slate-700">
            {metrics.roc_auc != null ? metrics.roc_auc.toFixed(3) : "—"}
          </dd>
        </dl>
      )}
    </div>
  );
}
