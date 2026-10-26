
import {
  useRef,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";

import {
  FileText,
  Upload,
  Send,
  LoaderCircle,
  X,
  BookOpen,
  AlertCircle,
  CheckCircle2,
  Copy,
  Sparkles,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Citation = {
  page_number: number;
  chunk_id: number;
  text: string;
  similarity: number;
};

type ChatResponse = {
  filename: string;
  page_count: number;
  answer: string;
  citations: Citation[];
};

type SummaryResponse = {
  filename: string;
  page_count: number;
  summary: string;
  character_count: number;
};

type DocumentChatProps = {
  mode: "chat" | "summary";
};

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const MAX_QUESTION_LENGTH = 1000;
const REQUEST_TIMEOUT_MS = 120_000;

function isRecord(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function isValidCitation(value: unknown): value is Citation {
  if (!isRecord(value)) {
    return false;
  }

  return (
    typeof value.page_number === "number" &&
    Number.isInteger(value.page_number) &&
    value.page_number > 0 &&
    typeof value.chunk_id === "number" &&
    Number.isFinite(value.chunk_id) &&
    typeof value.text === "string" &&
    typeof value.similarity === "number" &&
    Number.isFinite(value.similarity)
  );
}

function getApiError(data: unknown, status: number): string {
  if (isRecord(data)) {
    const detail = data.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .filter(isRecord)
        .map((item) => item.msg)
        .filter(
          (message): message is string =>
            typeof message === "string",
        );

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  }

  if (status === 413) {
    return "The uploaded file is too large for the server to process.";
  }

  if (status === 429) {
    return "The service is receiving too many requests. Please try again later.";
  }

  if (status >= 500) {
    return "The server encountered an error. Please try again later.";
  }

  return `The request failed (HTTP ${status}). Please try again.`;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(0)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatSimilarity(score: number): string {
  return `${(Math.max(0, Math.min(1, score)) * 100).toFixed(1)}% match`;
}

export default function DocumentChat({ mode }: DocumentChatProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [chatResult, setChatResult] =
    useState<ChatResponse | null>(null);
  const [summaryResult, setSummaryResult] =
    useState<SummaryResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");

  function clearResults() {
    setChatResult(null);
    setSummaryResult(null);
    setCopyMessage("");
  }

  function openFilePicker() {
    if (loading || !fileInputRef.current) {
      return;
    }

    // Allows the user to select the same file again.
    fileInputRef.current.value = "";
    fileInputRef.current.click();
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    setError("");
    clearResults();

    if (!selectedFile) {
      return;
    }

    const hasPdfExtension = selectedFile.name
      .toLowerCase()
      .endsWith(".pdf");

    const hasValidMimeType =
      selectedFile.type === "" ||
      selectedFile.type === "application/pdf";

    if (!hasPdfExtension || !hasValidMimeType) {
      setFile(null);
      setError("Please select a valid PDF file.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size === 0) {
      setFile(null);
      setError("The selected file is empty.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setFile(null);
      setError("The PDF must not exceed 10 MB.");
      event.target.value = "";
      return;
    }

    setFile(selectedFile);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) {
      return;
    }

    setError("");
    clearResults();

    if (!file) {
      setError("Please select a PDF before continuing.");
      return;
    }

    if (mode === "chat" && question.trim().length < 3) {
      setError("Please enter a question with at least 3 characters.");
      return;
    }

    if (mode === "chat" && question.trim().length > MAX_QUESTION_LENGTH) {
      setError("Your question exceeds the maximum allowed length.");
      return;
    }

    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      REQUEST_TIMEOUT_MS,
    );

    try {
      const formData = new FormData();
      formData.append("file", file);

      const url =
        mode === "chat"
          ? `${API_BASE_URL}/api/documents/chat?question=${encodeURIComponent(
              question.trim(),
            )}`
          : `${API_BASE_URL}/api/documents/summarize`;

      const response = await fetch(url, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      const data: unknown = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(getApiError(data, response.status));
      }

      if (!isRecord(data)) {
        throw new Error("The server returned an invalid response.");
      }

      if (mode === "chat") {
        if (
          typeof data.answer !== "string" ||
          !data.answer.trim()
        ) {
          throw new Error(
            "The server response did not contain a valid answer.",
          );
        }

        const citations = Array.isArray(data.citations)
          ? data.citations.filter(isValidCitation)
          : [];

        setChatResult({
          filename:
            typeof data.filename === "string"
              ? data.filename
              : file.name,
          page_count:
            typeof data.page_count === "number" &&
            Number.isFinite(data.page_count) &&
            data.page_count >= 0
              ? data.page_count
              : 0,
          answer: data.answer,
          citations,
        });
      } else {
        if (
          typeof data.summary !== "string" ||
          !data.summary.trim()
        ) {
          throw new Error(
            "The server response did not contain a valid summary.",
          );
        }

        setSummaryResult({
          filename:
            typeof data.filename === "string"
              ? data.filename
              : file.name,
          page_count:
            typeof data.page_count === "number" &&
            Number.isFinite(data.page_count) &&
            data.page_count >= 0
              ? data.page_count
              : 0,
          summary: data.summary,
          character_count:
            typeof data.character_count === "number" &&
            Number.isFinite(data.character_count)
              ? data.character_count
              : data.summary.length,
        });
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        setError(
          "The request took too long. Please try again with a smaller document or a simpler question.",
        );
      } else if (err instanceof TypeError) {
        setError(
          "Could not connect to the API. Check that the backend is running and the API URL is correct.",
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  }

  function handleRemoveFile() {
    if (loading) {
      return;
    }

    setFile(null);
    setError("");
    clearResults();

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function handleCopy(text: string) {
    setCopyMessage("");

    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard access is unavailable.");
      }

      await navigator.clipboard.writeText(text);
      setCopyMessage("Copied to clipboard.");
    } catch {
      setCopyMessage(
        "Copy was unavailable. Select the text and copy it manually.",
      );
    }
  }

  return (
    <section className="document-panel" aria-busy={loading}>
      <div className="document-panel-heading">
        <div className="document-panel-icon">
          {mode === "chat" ? (
            <BookOpen size={21} aria-hidden="true" />
          ) : (
            <FileText size={21} aria-hidden="true" />
          )}
        </div>

        <div>
          <h2>
            {mode === "chat" ? "Chat with your PDF" : "Document summary"}
          </h2>

          <p>
            {mode === "chat"
              ? "Ask questions and explore supporting passages from your document."
              : "Generate a concise overview of your document's main ideas and key points."}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <input
          ref={fileInputRef}
          className="hidden-file-input"
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          disabled={loading}
          aria-label="Choose a PDF file"
        />

        <div
          className={`document-dropzone ${file ? "has-file" : ""}`}
          aria-busy={loading}
        >
          {file ? (
            <>
              <div className="dropzone-icon">
                <FileText size={23} aria-hidden="true" />
              </div>

              <div className="selected-file-details">
                <strong title={file.name}>{file.name}</strong>
                <span>
                  {formatFileSize(file.size)} · PDF selected
                </span>
              </div>

              <button
                type="button"
                className="file-action-button"
                onClick={openFilePicker}
                disabled={loading}
              >
                Replace
              </button>

              <button
                type="button"
                className="remove-file"
                aria-label="Remove selected PDF"
                onClick={handleRemoveFile}
                disabled={loading}
              >
                <X size={17} aria-hidden="true" />
              </button>
            </>
          ) : (
            <button
              type="button"
              className="dropzone-trigger"
              onClick={openFilePicker}
              disabled={loading}
            >
              <span className="dropzone-icon">
                <Upload size={23} aria-hidden="true" />
              </span>

              <strong>Select a PDF document</strong>
              <span>Browse your files to upload a document</span>

              <span className="upload-hint">
                PDF files only · Maximum 10 MB
              </span>
            </button>
          )}
        </div>

        {mode === "chat" && (
          <div className="question-field">
            <label htmlFor="document-question">Your question</label>

            <textarea
              id="document-question"
              value={question}
              onChange={(event) => {
                setQuestion(event.target.value);
                setError("");
              }}
              placeholder="Ask something about your PDF..."
              minLength={3}
              maxLength={MAX_QUESTION_LENGTH}
              rows={4}
              disabled={loading}
              required
            />

            <span className="character-count">
              {question.length}/{MAX_QUESTION_LENGTH}
            </span>
          </div>
        )}

        {error && (
          <div className="document-error" role="alert">
            <AlertCircle size={17} aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        <button
          type="submit"
          className="primary-button document-submit"
          disabled={
            loading ||
            !file ||
            (mode === "chat" && question.trim().length < 3)
          }
        >
          {loading ? (
            <>
              <LoaderCircle
                className="loading-spinner"
                size={17}
                aria-hidden="true"
              />
              {mode === "chat"
                ? "Finding an answer..."
                : "Generating summary..."}
            </>
          ) : mode === "chat" ? (
            <>
              <Send size={17} aria-hidden="true" />
              Ask question
              <Sparkles size={16} aria-hidden="true" />
            </>
          ) : (
            <>
              <FileText size={17} aria-hidden="true" />
              Generate summary
            </>
          )}
        </button>

        {loading && (
          <p className="processing-note" role="status">
            Processing your PDF. This may take a little while.
          </p>
        )}
      </form>

      {chatResult && (
        <section className="result-panel" aria-live="polite">
          <div className="result-heading">
            <div>
              <span className="result-label">AI RESPONSE</span>
              <h3>Your answer</h3>
              {chatResult.filename && (
                <p className="result-filename">
                  {chatResult.filename}
                </p>
              )}
            </div>

            <span className="page-count">
              {chatResult.page_count}{" "}
              {chatResult.page_count === 1 ? "page" : "pages"}
            </span>
          </div>

          <div className="answer-card">
            <div className="answer-card-heading">
              <span>
                <Sparkles size={16} aria-hidden="true" />
                Generated answer
              </span>

              <button
                type="button"
                className="copy-button"
                onClick={() => handleCopy(chatResult.answer)}
                aria-label="Copy answer"
              >
                <Copy size={15} aria-hidden="true" />
                Copy
              </button>
            </div>

            <div className="answer-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {chatResult.answer}
              </ReactMarkdown>
            </div>
          </div>

          {copyMessage && (
            <p className="copy-feedback" role="status">
              {copyMessage}
            </p>
          )}

          <div className="citations-section">
            <div className="citations-heading">
              <div>
                <h4>Source passages</h4>
                <p>
                  Review the retrieved text and verify important
                  information against the original document.
                </p>
              </div>

              <span className="source-count">
                {chatResult.citations.length}{" "}
                {chatResult.citations.length === 1 ? "source" : "sources"}
              </span>
            </div>

            {chatResult.citations.length > 0 ? (
              chatResult.citations.map((citation, index) => (
                <details
                  className="citation-item"
                  key={`${citation.page_number}-${citation.chunk_id}-${index}`}
                >
                  <summary>
                    <span className="citation-page-icon">
                      <FileText size={16} aria-hidden="true" />
                    </span>

                    <span className="citation-title">
                      <strong>Page {citation.page_number}</strong>
                      <span>Source passage {index + 1}</span>
                    </span>

                    <span
                      className="citation-score"
                      title="Vector retrieval similarity, not an answer confidence score"
                    >
                      {formatSimilarity(citation.similarity)}
                    </span>
                  </summary>

                  <div className="citation-body">
                    <p>{citation.text}</p>
                    <span className="citation-disclaimer">
                      Retrieved passage · Verify against the original PDF.
                    </span>
                  </div>
                </details>
              ))
            ) : (
              <div className="no-citations">
                <AlertCircle size={17} aria-hidden="true" />
                <p>
                  No source passages were returned for this answer.
                  Verify the answer against your document.
                </p>
              </div>
            )}
          </div>
        </section>
      )}

      {summaryResult && (
        <section className="result-panel" aria-live="polite">
          <div className="result-heading">
            <div>
              <span className="result-label">AI DOCUMENT ANALYSIS</span>
              <h3>Document summary</h3>

              {summaryResult.filename && (
                <p className="result-filename">
                  {summaryResult.filename}
                </p>
              )}
            </div>

            <span className="page-count">
              {summaryResult.page_count}{" "}
              {summaryResult.page_count === 1 ? "page" : "pages"}
            </span>
          </div>

          <div className="answer-card">
            <div className="answer-card-heading">
              <span>
                <CheckCircle2 size={16} aria-hidden="true" />
                Summary
              </span>

              <button
                type="button"
                className="copy-button"
                onClick={() => handleCopy(summaryResult.summary)}
                aria-label="Copy document summary"
              >
                <Copy size={15} aria-hidden="true" />
                Copy
              </button>
            </div>

            <div className="answer-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {summaryResult.summary}
              </ReactMarkdown>
            </div>
          </div>

          {copyMessage && (
            <p className="copy-feedback" role="status">
              {copyMessage}
            </p>
          )}
        </section>
      )}
    </section>
  );
}
