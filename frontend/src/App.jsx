import { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import ImageUploader from "./components/ImageUploader.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import { fetchHealth, predictImage } from "./api/client.js";

export default function App() {
  const [health, setHealth] = useState("loading");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Probe API on mount
  useEffect(() => {
    let mounted = true;
    fetchHealth()
      .then(() => mounted && setHealth("ok"))
      .catch(() => mounted && setHealth("offline"));
    return () => {
      mounted = false;
    };
  }, []);

  // Revoke preview URL on change to avoid leaks
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  async function handlePredict(file) {
    setError(null);
    setResult(null);
    setIsLoading(true);

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));

    try {
      const data = await predictImage(file);
      setResult(data);
    } catch (err) {
      setError(err.message ?? "Unknown error");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-full bg-slate-50">
      <Header status={health} />

      <main className="mx-auto max-w-5xl px-6 py-10">
        <section className="mb-10">
          <h2 className="text-2xl font-semibold text-slate-900">
            Classify an MRI image
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            Drop an MRI image and we'll run it through three trained models —
            a custom CNN, ResNet (transfer learning), and an MLP baseline —
            and show you each one's verdict and confidence.
          </p>
        </section>

        <div className="grid gap-8 lg:grid-cols-2">
          <ImageUploader
            onPredict={handlePredict}
            isLoading={isLoading}
            previewUrl={previewUrl}
          />

          <ResultsPanel
            result={result}
            error={error}
            isLoading={isLoading}
          />
        </div>

        <footer className="mt-16 border-t border-slate-200 pt-6 text-center text-xs text-slate-400">
          Trained on a sampled breast-MRI tumor classification dataset · For
          educational use only — not a medical device.
        </footer>
      </main>
    </div>
  );
}
