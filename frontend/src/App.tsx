
import { useState } from "react";
import {
  FileText,
  MessageSquareText,
  LayoutDashboard,
  Settings,
  Sparkles,
  ShieldCheck,
  Menu,
  X,
  ArrowRight,
  Upload,
  Search,
  BookOpen,
  CheckCircle2,
} from "lucide-react";
import "./App.css";
import DocumentChat from "./components/DocumentChat";

type Tab = "Dashboard" | "PDF Chat" | "Summarize" | "Settings";

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("Dashboard");
  const [mobileOpen, setMobileOpen] = useState(false);

  const navigation = [
    { label: "Dashboard" as const, icon: LayoutDashboard },
    { label: "PDF Chat" as const, icon: MessageSquareText },
    { label: "Summarize" as const, icon: FileText },
    { label: "Settings" as const, icon: Settings },
  ];

  const navigateTo = (tab: Tab) => {
    setActiveTab(tab);
    setMobileOpen(false);
  };

  return (
    <div className="app-shell">
      {mobileOpen && (
        <button
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={22} />
          </div>
          <div>
            <h2>DocuMind</h2>
            <span>AI DOCUMENT INTELLIGENCE</span>
          </div>
          <button
            className="mobile-close"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
          >
            <X size={19} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation" aria-label="Main navigation">
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${activeTab === label ? "active" : ""}`}
              onClick={() => navigateTo(label)}
              aria-current={activeTab === label ? "page" : undefined}
            >
              <Icon size={19} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="security-note">
            <ShieldCheck size={20} />
            <div>
              <strong>Privacy first</strong>
              <p>Review how your documents are processed.</p>
            </div>
          </div>
          <p className="version">AI Document Intelligence · v1.0</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            aria-label="Open navigation"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={21} />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> {activeTab}
          </div>

          <div className="status">
            <span className="status-dot" />
            AI workspace
          </div>
        </header>

        <section className="page-content">
          {activeTab === "Dashboard" && (
            <>
              <section className="dashboard-hero">
                <div className="eyebrow">
                  <Sparkles size={15} />
                  YOUR AI WORKSPACE
                </div>

                <h1>
                  Make your documents
                  <br />
                  <span>work smarter.</span>
                </h1>

                <p className="subtitle">
                  Ask questions, uncover important information, and turn
                  lengthy PDFs into useful insights—all from one workspace.
                </p>

                <button
                  className="primary-button dashboard-primary"
                  onClick={() => navigateTo("PDF Chat")}
                >
                  <MessageSquareText size={17} />
                  Start chatting with a PDF
                  <ArrowRight size={16} />
                </button>
              </section>

              <div className="dashboard-section-heading">
                <div>
                  <h2>What would you like to do?</h2>
                  <p>Choose a tool to get started with your document.</p>
                </div>
              </div>

              <div className="dashboard-action-grid">
                <button
                  className="dashboard-action-card"
                  onClick={() => navigateTo("PDF Chat")}
                >
                  <div className="dashboard-action-icon purple">
                    <MessageSquareText size={22} />
                  </div>
                  <div className="dashboard-card-topline">
                    <span className="dashboard-card-category">ASK QUESTIONS</span>
                    <ArrowRight size={17} />
                  </div>
                  <h3>Chat with a PDF</h3>
                  <p>
                    Ask questions about your document and review relevant
                    passages with page references.
                  </p>
                  <span className="dashboard-card-link">Open PDF Chat</span>
                </button>

                <button
                  className="dashboard-action-card"
                  onClick={() => navigateTo("Summarize")}
                >
                  <div className="dashboard-action-icon blue">
                    <FileText size={22} />
                  </div>
                  <div className="dashboard-card-topline">
                    <span className="dashboard-card-category">FIND THE KEY POINTS</span>
                    <ArrowRight size={17} />
                  </div>
                  <h3>Summarize a document</h3>
                  <p>
                    Generate a concise overview of the main ideas and important
                    points in a PDF.
                  </p>
                  <span className="dashboard-card-link">Create a summary</span>
                </button>
              </div>

              <section className="workflow-panel">
                <div className="workflow-heading">
                  <div className="workflow-heading-icon">
                    <BookOpen size={19} />
                  </div>
                  <div>
                    <h2>How DocuMind works</h2>
                    <p>From PDF to useful answers in three steps.</p>
                  </div>
                </div>

                <div className="workflow-steps">
                  <div className="workflow-step">
                    <div className="workflow-step-icon">
                      <Upload size={19} />
                    </div>
                    <div>
                      <span>STEP 01</span>
                      <h3>Upload</h3>
                      <p>Select a text-based PDF to analyse.</p>
                    </div>
                  </div>

                  <div className="workflow-connector" />

                  <div className="workflow-step">
                    <div className="workflow-step-icon">
                      <Search size={19} />
                    </div>
                    <div>
                      <span>STEP 02</span>
                      <h3>Explore</h3>
                      <p>Ask a question or request a summary.</p>
                    </div>
                  </div>

                  <div className="workflow-connector" />

                  <div className="workflow-step">
                    <div className="workflow-step-icon">
                      <CheckCircle2 size={19} />
                    </div>
                    <div>
                      <span>STEP 03</span>
                      <h3>Review</h3>
                      <p>Read the response and inspect its sources.</p>
                    </div>
                  </div>
                </div>
              </section>

              <div className="dashboard-note">
                <ShieldCheck size={18} />
                <p>
                  <strong>Designed for document-grounded answers.</strong>{" "}
                  Check the cited passages against your original PDF when
                  verifying important information.
                </p>
              </div>
            </>
          )}

          {(activeTab === "PDF Chat" || activeTab === "Summarize") && (
            <>
              <div className="tool-page-heading">
                <div className="eyebrow">
                  <Sparkles size={15} />
                  DOCUMENT WORKSPACE
                </div>
                <h1>
                  {activeTab === "PDF Chat"
                    ? "Chat with your PDF."
                    : "Summarize your PDF."}
                </h1>
                <p className="subtitle">
                  {activeTab === "PDF Chat"
                    ? "Ask a question and explore the supporting passages from your document."
                    : "Generate a concise overview of your document's main ideas and key points."}
                </p>
              </div>

              <DocumentChat
                mode={activeTab === "Summarize" ? "summary" : "chat"}
              />
            </>
          )}

          {activeTab === "Settings" && (
            <>
              <div className="tool-page-heading">
                <div className="eyebrow">
                  <Settings size={15} />
                  WORKSPACE PREFERENCES
                </div>
                <h1>Settings</h1>
                <p className="subtitle">
                  Information about your current DocuMind workspace.
                </p>
              </div>

              <section className="settings-panel">
                <div className="settings-row">
                  <div className="settings-row-icon">
                    <Sparkles size={19} />
                  </div>
                  <div>
                    <h3>AI document analysis</h3>
                    <p>
                      Responses and summaries are generated using the
                      configured Gemini API service.
                    </p>
                  </div>
                </div>

                <div className="settings-row">
                  <div className="settings-row-icon">
                    <FileText size={19} />
                  </div>
                  <div>
                    <h3>Supported documents</h3>
                    <p>
                      PDF upload is supported. Scanned PDFs that contain no
                      extractable text may not be processed.
                    </p>
                  </div>
                </div>

                <div className="settings-row">
                  <div className="settings-row-icon">
                    <ShieldCheck size={19} />
                  </div>
                  <div>
                    <h3>API configuration</h3>
                    <p>
                      Keep API keys in your backend environment variables.
                      Never place secret keys in frontend code.
                    </p>
                  </div>
                </div>

                <p className="settings-footnote">
                  Customisable preferences and persistent document history are
                  not available in the current version.
                </p>
              </section>
            </>
          )}

          <footer className="page-footer">
            <span>Built for smarter document workflows.</span>
            <span>
              <ShieldCheck size={15} />
              Evidence-based AI answers
            </span>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;
