export default function Header({ status }) {
  const dotColor =
    status === "ok"
      ? "bg-emerald-500"
      : status === "loading"
      ? "bg-amber-400"
      : "bg-rose-500";

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M12 2a4 4 0 0 0-4 4v1a4 4 0 0 0-3 3.87V12a4 4 0 0 0 3 3.87V17a4 4 0 0 0 4 4 4 4 0 0 0 4-4v-1.13A4 4 0 0 0 19 12v-1.13A4 4 0 0 0 16 7V6a4 4 0 0 0-4-4z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-900">
              MRI Tumor Classifier
            </h1>
            <p className="text-xs text-slate-500">
              Binary classification · CNN · ResNet · MLP
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          <span className={`h-2 w-2 rounded-full ${dotColor}`} />
          {status === "ok"
            ? "API healthy"
            : status === "loading"
            ? "Connecting…"
            : "API offline"}
        </div>
      </div>
    </header>
  );
}
