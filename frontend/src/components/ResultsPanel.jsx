import PredictionCard from "./PredictionCard.jsx";

export default function ResultsPanel({ result, error, isLoading }) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">
        Running inference on all 3 models…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">
        <p className="font-semibold">Something went wrong</p>
        <p className="mt-1">{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-200 bg-white/50 p-10 text-center text-sm text-slate-500">
        Upload an image to see model predictions.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Predictions
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {result.predictions.map((p) => (
          <PredictionCard key={p.model} prediction={p} />
        ))}
      </div>
    </div>
  );
}
