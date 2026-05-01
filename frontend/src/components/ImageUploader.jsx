import { useCallback, useRef, useState } from "react";

export default function ImageUploader({ onPredict, isLoading, previewUrl }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (files) => {
      if (!files || files.length === 0) return;
      const file = files[0];
      if (!file.type.startsWith("image/")) {
        alert("Please choose an image file.");
        return;
      }
      onPredict(file);
    },
    [onPredict]
  );

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed bg-white px-6 py-10 text-center transition-colors ${
        dragging
          ? "border-brand-500 bg-brand-50"
          : "border-slate-300 hover:border-brand-400"
      }`}
    >
      {previewUrl ? (
        <img
          src={previewUrl}
          alt="MRI preview"
          className="mb-4 max-h-64 rounded-lg border border-slate-200 object-contain"
        />
      ) : (
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-7 w-7"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
      )}

      <p className="text-sm font-medium text-slate-800">
        {previewUrl
          ? "Drop a different image to re-classify"
          : "Drag and drop an MRI image"}
      </p>
      <p className="mt-1 text-xs text-slate-500">
        PNG / JPG / JPEG · resized to 224×224 server-side
      </p>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={isLoading}
        className="mt-5 inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? (
          <>
            <svg
              className="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"
              />
            </svg>
            Classifying…
          </>
        ) : (
          <>Choose image</>
        )}
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
