import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  /* ---------------------------
     Fetch History
  --------------------------- */
  const fetchHistory = async () => {
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/history/"
      );
      setHistory(res.data);
    } catch {
      console.log("Failed to fetch history");
    }
  };

  /* ---------------------------
     Upload
  --------------------------- */
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a CSV file");
      return;
    }

    setLoading(true);
    setProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append("csv_file", file);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/analyze/",
        formData,
        {
          onUploadProgress: (e) => {
            const percent = Math.round(
              (e.loaded * 100) / e.total
            );
            setProgress(percent);
          },
        }
      );

      setReport(res.data);
      fetchHistory();

    } catch (err) {
      setError(
        err.response?.data?.error || "Upload failed"
      );
    }

    setLoading(false);
    setProgress(0);
  };

  /* ---------------------------
     Delete
  --------------------------- */
  const handleDelete = async (id) => {
    const ok = window.confirm(
      "Are you sure you want to delete this report?"
    );

    if (!ok) return;

    await axios.delete(
      `http://127.0.0.1:8000/api/history/${id}/`
    );

    fetchHistory();
  };

  return (
    <div className="min-h-screen bg-slate-100">

      {/* ================= HEADER ================= */}
      <header className="bg-blue-700 text-white shadow">

        <div className="max-w-7xl mx-auto px-6 py-6">

          <h1 className="text-3xl font-bold">
            📊 Sales Forecaster
          </h1>

          <p className="text-blue-100 text-sm mt-1">
            Smart CSV Analytics & Reporting
          </p>

        </div>

      </header>

      {/* ================= MAIN ================= */}
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-10">

        {/* ========== UPLOAD CARD ========== */}
        <section className="bg-white rounded-xl shadow-lg p-6">

          <h2 className="text-xl font-semibold mb-4">
            Upload Dataset
          </h2>

          <div className="flex flex-col md:flex-row items-center gap-4">

            <input
              type="file"
              accept=".csv"
              onChange={(e) =>
                setFile(e.target.files[0])
              }
              className="
                w-full md:w-auto
                text-sm text-gray-600
                file:mr-4 file:px-4 file:py-2
                file:rounded-lg file:border-0
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
              "
            />

            <button
              onClick={handleUpload}
              disabled={loading}
              className="
                px-6 py-2 rounded-lg
                bg-blue-600 text-white
                font-medium
                hover:bg-blue-700
                transition
                disabled:opacity-50
              "
            >
              {loading
                ? "Analyzing..."
                : "Upload & Analyze"}
            </button>

          </div>

          {/* Progress Bar */}
          {loading && (
            <div className="mt-4">

              <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">

                <div
                  className="bg-blue-600 h-3 transition-all"
                  style={{
                    width: `${progress}%`,
                  }}
                />

              </div>

              <p className="text-sm text-gray-500 mt-1">
                Processing... {progress}%
              </p>

            </div>
          )}

          {/* Error */}
          {error && (
            <p className="text-red-600 mt-3 text-sm">
              ⚠ {error}
            </p>
          )}

        </section>

        {/* ========== STATS ========== */}
        {report && (
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6">

            <div className="bg-white rounded-xl shadow p-6">

              <p className="text-gray-500 text-sm">
                Total Value
              </p>

              <h3 className="text-3xl font-bold mt-2">
                ${report.total?.toLocaleString()}
              </h3>

            </div>

            <div className="bg-white rounded-xl shadow p-6">

              <p className="text-gray-500 text-sm">
                Average Value
              </p>

              <h3 className="text-3xl font-bold mt-2">
                ${report.average?.toFixed(2)}
              </h3>

            </div>

            <div className="bg-white rounded-xl shadow p-6">

              <p className="text-gray-500 text-sm">
                Detected Column
              </p>

              <h3 className="text-lg font-semibold mt-3">
                {report.used_column || "N/A"}
              </h3>

            </div>

          </section>
        )}

        {/* ========== CHART ========== */}
        {report?.chart && (
          <section className="bg-white rounded-xl shadow-lg p-6">

            <h2 className="text-xl font-semibold mb-4">
              Trend Analysis
            </h2>

            <div className="bg-slate-50 p-4 rounded-lg border">

              <img
                src={`data:image/png;base64,${report.chart}`}
                alt="Chart"
                className="mx-auto rounded-lg"
              />

            </div>

          </section>
        )}

        {/* ========== HISTORY ========== */}
        <section className="bg-white rounded-xl shadow-lg overflow-hidden">

          <div className="p-6 border-b">

            <h2 className="text-xl font-semibold">
              Recent Reports
            </h2>

          </div>

          {history.length === 0 ? (

            <p className="p-6 text-gray-500 text-sm">
              No reports yet. Upload a CSV file.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-sm">

                <thead className="bg-slate-50 border-b">

                  <tr>

                    <th className="px-6 py-3 text-left text-gray-500 font-medium">
                      Date
                    </th>

                    <th className="px-6 py-3 text-left text-gray-500 font-medium">
                      File
                    </th>

                    <th className="px-6 py-3 text-left text-gray-500 font-medium">
                      Total
                    </th>

                    <th className="px-6 py-3 text-left text-gray-500 font-medium">
                      Actions
                    </th>

                  </tr>

                </thead>

                <tbody className="divide-y">

                  {history.map((item) => (

                    <tr
                      key={item.id}
                      className="hover:bg-slate-50 transition"
                    >

                      <td className="px-6 py-4 text-gray-600">
                        {item.upload_date}
                      </td>

                      <td className="px-6 py-4 font-medium">
                        {item.filename}
                      </td>

                      <td className="px-6 py-4 font-semibold text-blue-600">
                        ${item.total_sales || 0}
                      </td>

                      <td className="px-6 py-4 flex gap-4">

                        <a
                          href={`http://127.0.0.1:8000/api/download/${item.id}/`}
                          target="_blank"
                          rel="noreferrer"
                          className="
                            text-green-600 hover:underline
                            font-medium
                          "
                        >
                          📄 PDF
                        </a>

                        <button
                          onClick={() =>
                            handleDelete(item.id)
                          }
                          className="
                            text-red-600 hover:underline
                            font-medium
                          "
                        >
                          🗑 Delete
                        </button>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>
          )}

        </section>

      </main>

      {/* ================= FOOTER ================= */}
      <footer className="text-center py-6 text-gray-500 text-sm">

        Built with React • Tailwind • Django • MongoDB

      </footer>

    </div>
  );
}

export default App;
