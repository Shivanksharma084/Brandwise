// @ts-nocheck
import React, { useState } from 'react';
import { jsPDF } from 'jspdf';


interface Finding {
  id: string;
  category: 'claim' | 'tone' | 'terminology' | 'accessibility' | 'disclaimer';
  severity: 'high' | 'medium' | 'low' | 'advisory';
  highlightedText: string;
  explanation: string;
  sourceRef: string;
  confidence: number;
  suggestedFix: string;
  status: 'open' | 'accepted' | 'rejected' | 'routed_legal' | 'disputed';
  disputeReason?: string;
}

const INITIAL_FINDINGS: Finding[] = [
  {
    id: 'f-1',
    category: 'claim',
    severity: 'high',
    highlightedText: "India's #1 skincare brand",
    explanation: "Fact register does not substantiate '#1'. Nearest registered claim is 'top 5 in category, 2025 survey' (owner: Market Research, expires Dec 2026).",
    sourceRef: "Fact Register #FR-402 (Market Position)",
    confidence: 0.94,
    suggestedFix: "One of India's top 5 skincare brands (2025 survey)",
    status: 'open',
  },
  {
    id: 'f-2',
    category: 'claim',
    severity: 'high',
    highlightedText: "Cures acne in 7 days",
    explanation: "Guidelines strictly prohibit curative or guaranteed time-bound medical outcomes without sign-off from Legal and Regulatory Affairs.",
    sourceRef: "Guideline Clause §4.2 (Health & Regulated Claims)",
    confidence: 0.99,
    suggestedFix: "Helps reduce the look of acne",
    status: 'open',
  },
  {
    id: 'f-3',
    category: 'disclaimer',
    severity: 'high',
    highlightedText: "Use code GLOW20 for discount!",
    explanation: "Promotional commercial collaboration post lacks the mandatory prominent disclosure tag (#ad) as mandated by ASCI Influencer Code 2025.",
    sourceRef: "ASCI Influencer Code 2025 §1.1",
    confidence: 0.91,
    suggestedFix: "Add #ad at the beginning of the caption",
    status: 'open',
  },
  {
    id: 'f-4',
    category: 'tone',
    severity: 'medium',
    highlightedText: "Hey guys!! Grab this crazy deal",
    explanation: "Informal slang greeting conflicts with approved Brand Voice standard (warm, professional, accessible).",
    sourceRef: "Guideline Clause §2.1 (Tone & Language)",
    confidence: 0.88,
    suggestedFix: "Hello! Here is an offer we think you will like.",
    status: 'open',
  },
];

export default function BrandwiseDashboard() {
  const [activeTab, setActiveTab] = useState('review');
  const [content, setContent] = useState(
    "Hey guys!! Grab this crazy deal right now! Discover India's #1 skincare brand that cures acne in 7 days! Use code GLOW20 for discount!"
  );
  const [findings, setFindings] = useState(INITIAL_FINDINGS);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState('Instagram');
  const [isAiAssisted, setIsAiAssisted] = useState(true);
  const [showCertificate, setShowCertificate] = useState(false);

  const handleAcceptFix = (id, original, fix) => {
    setContent((prev) => prev.replace(original, fix));
    setFindings((prev) =>
      prev.map((f) => (f.id === id ? { ...f, status: 'accepted' } : f))
    );
  };

  const handleReject = (id) => {
    setFindings((prev) =>
      prev.map((f) => (f.id === id ? { ...f, status: 'rejected' } : f))
    );
  };

  const handleDispute = (id) => {
    const reason = prompt('Please provide a reason for disputing this guideline rule (this feeds the Guideline-Gap insights engine):');
    if (reason) {
      setFindings((prev) =>
        prev.map((f) => (f.id === id ? { ...f, status: 'disputed', disputeReason: reason } : f))
      );
    }
  };

  const handleRouteLegal = (id) => {
    setFindings((prev) =>
      prev.map((f) => (f.id === id ? { ...f, status: 'routed_legal' } : f))
    );
  };

  const generatePdfCertificate = () => {
    try {
      const jsPDFClass = typeof jsPDF !== 'undefined' ? jsPDF : ((window as any).jspdf?.jsPDF || (window as any).jsPDF);
      if (!jsPDFClass) {
        alert('jsPDF library is loading. Please click Download again.');
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        script.onload = () => generatePdfCertificate();
        document.head.appendChild(script);
        return;
      }
      const doc = new jsPDFClass({ orientation: 'landscape', unit: 'mm', format: 'a4' });

      // Page dimensions for A4 landscape: 297 x 210 mm
      // Outer double border
      doc.setLineWidth(1.5);
      doc.setDrawColor(16, 185, 129);
      doc.rect(10, 10, 277, 190);
      doc.setLineWidth(0.5);
      doc.rect(13, 13, 271, 184);

      // Top-Left Corner Logo Badge
      doc.setFillColor(15, 23, 42);
      doc.roundedRect(20, 18, 32, 16, 2, 2, 'F');
      doc.setFont("Helvetica", "bold");
      doc.setFontSize(12);
      doc.setTextColor(16, 185, 129);
      doc.text("BRANDWISE", 36, 26, { align: "center" });
      doc.setFontSize(7);
      doc.setTextColor(255, 255, 255);
      doc.text("AI GOVERNANCE", 36, 31, { align: "center" });

      // Generate Real QR Code for Public Verification
      let currentHost = window.location.hostname;
      let currentPort = window.location.port;
      if (currentHost === 'localhost' || currentHost === '127.0.0.1' || !currentHost) {
        currentHost = '172.28.82.173'; // Local Wi-Fi IP for mobile scanning
        currentPort = '8000'; // Dedicated static server port for testing
      }
      const verifyUrl = window.location.protocol + '//' + currentHost + (currentPort ? ':' + currentPort : '') + window.location.pathname.replace(/Dashboard\.tsx$/, '').replace(/\/$/, '') + '/verify.html?cert=BW-CERT-88419-2026';
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      document.body.appendChild(tempDiv);

      if (typeof (window as any).QRCode !== 'undefined') {
        new (window as any).QRCode(tempDiv, {
          text: verifyUrl,
          width: 128,
          height: 128,
          colorDark: "#0F172A",
          colorLight: "#ffffff",
          correctLevel: 1 // Medium
        });
      }

      setTimeout(() => {
        try {
          const canvas = tempDiv.querySelector('canvas') || tempDiv.querySelector('img');
          if (canvas) {
            const qrDataUrl = (canvas as HTMLElement).tagName.toLowerCase() === 'img' ? (canvas as HTMLImageElement).src : (canvas as HTMLCanvasElement).toDataURL('image/png');
            doc.addImage(qrDataUrl, 'PNG', 246, 17, 22, 22);
            doc.link(246, 17, 22, 22, { url: verifyUrl });
          }
        } catch (e) {
          console.warn('QR image capture fallback:', e);
        }
        if (document.body.contains(tempDiv)) {
          document.body.removeChild(tempDiv);
        }

        doc.setFont("Helvetica", "bold");
        doc.setFontSize(6);
        doc.setTextColor(71, 85, 105);
        doc.text("SCAN TO VERIFY", 257, 42, { align: "center" });

        // Header / Title
        doc.setFont("Helvetica", "bold");
        doc.setFontSize(26);
        doc.setTextColor(15, 23, 42);
        doc.text("BRANDWISE AI GOVERNANCE", 148.5, 28, { align: "center" });

        doc.setFontSize(13);
        doc.setTextColor(16, 185, 129);
        doc.text("OFFICIAL COMPLIANCE & QUALITY MANAGEMENT CERTIFICATE", 148.5, 35, { align: "center" });

        // Subtext
        doc.setFont("Helvetica", "normal");
        doc.setFontSize(11);
        doc.setTextColor(71, 85, 105);
        doc.text("This is to certify that the enterprise workspace", 148.5, 50, { align: "center" });

        // Organization Name
        doc.setFont("Helvetica", "bold");
        doc.setFontSize(22);
        doc.setTextColor(15, 23, 42);
        doc.text("DermaCare Global Healthcare", 148.5, 63, { align: "center" });

        // Compliance text
        doc.setFont("Helvetica", "normal");
        doc.setFontSize(11);
        doc.setTextColor(71, 85, 105);
        doc.text("has been rigorously evaluated and found in full compliance with the requirements of", 148.5, 75, { align: "center" });

        doc.setFont("Helvetica", "bold");
        doc.setFontSize(15);
        doc.setTextColor(16, 185, 129);
        doc.text("ISO 9001:2015 & DPDP 2025 Brand Governance Standards", 148.5, 87, { align: "center" });

        doc.setFont("Helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(71, 85, 105);
        doc.text("for the following approved scope of pre-publication review and automated validation:", 148.5, 98, { align: "center" });

        // Scope box
        doc.setFillColor(241, 245, 249);
        doc.roundedRect(35, 105, 227, 32, 3, 3, 'F');

        doc.setFont("Helvetica", "bold");
        doc.setFontSize(10);
        doc.setTextColor(30, 41, 59);
        doc.text("• Multi-Layer Deterministic & LLM Content Review Pipeline (§4.2 Regulated Claims)", 45, 113);
        doc.text("• Automated Claim & Fact Register Verification (Purpose Limitation & Zero-Retention)", 45, 121);
        doc.text("• ASCI Influencer Commercial Disclosure Compliance & Cryptographic Audit Logging", 45, 129);

        // Metadata block (left)
        doc.setFont("Helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(51, 65, 85);
        doc.text("Certificate No : BW-CERT-88419-2026", 25, 155);
        doc.text("Issue Date     : 2026-10-25", 25, 162);
        doc.text("Expiry Date    : 2027-10-25", 25, 169);
        doc.text("Pipeline Ver   : v2.4 (Active Standards)", 25, 176);

        // Hash & Footer (right)
        doc.text("Cryptographic Hash:", 175, 155);
        doc.setFont("Courier", "normal");
        doc.setFontSize(8);
        doc.text("7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1f", 175, 161);

        doc.setFont("Helvetica", "bold");
        doc.setFontSize(11);
        doc.text("Authorised Signature", 215, 175);
        doc.setLineWidth(0.5);
        doc.line(190, 170, 260, 170);

        doc.setFont("Helvetica", "normal");
        doc.setFontSize(9);
        doc.setTextColor(100, 116, 139);
        doc.text("Dr. Aris Thorne, Chief Governance Officer", 215, 180, { align: "center" });

        doc.save("BW-CERT-88419-Governance-Certificate.pdf");
        setShowCertificate(false);
      }, 120);
    } catch (err: any) {
      console.error('Error generating PDF:', err);
      alert('Error generating PDF: ' + err.message);
    }
  };

  const handleRunReview = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      alert('Review pipeline complete! 4 findings detected and source-grounded.');
    }, 900);
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'advisory':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const openFindingsCount = findings.filter((f) => f.status === 'open').length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between sticky top-0 z-20 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm">
            B
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-semibold text-slate-900 tracking-tight">Brandwise</h1>
              <span className="text-[10px] bg-indigo-100 text-indigo-800 font-bold px-1.5 py-0.5 rounded uppercase tracking-wider">
                DPDP 2025 Ready
              </span>
            </div>
            <p className="text-xs text-slate-500">AI Pre-Publication Brand Governance Platform</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Tenant: <strong>DermaCare Healthcare</strong></span>
          </div>
          <button
            onClick={() => setShowCertificate(true)}
            className="text-xs bg-slate-900 hover:bg-slate-800 text-white px-3 py-1.5 rounded-lg font-medium transition"
          >
            Export Audit Certificate
          </button>
          <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
            SA
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        <aside className="w-64 bg-white border-r border-slate-200 p-4 space-y-1">
          <button
            onClick={() => setActiveTab('review')}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === 'review' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              <span>✨</span>
              <span>Content Review</span>
            </div>
            {openFindingsCount > 0 && (
              <span className="bg-rose-500 text-white text-[11px] font-bold px-2 py-0.5 rounded-full">
                {openFindingsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('knowledge')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === 'knowledge' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>📚</span>
            <span>Brand Rules & Facts</span>
          </button>

          <button
            onClick={() => setActiveTab('insights')}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === 'insights' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              <span>📈</span>
              <span>Guideline-Gap Insights</span>
            </div>
            <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-1.5 py-0.5 rounded">
              Feature #3
            </span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === 'audit' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>🛡️</span>
            <span>Audit Trail & Approvals</span>
          </button>

          <div className="pt-6 mt-6 border-t border-slate-100">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                <span>Privacy & AI Shield</span>
                <span className="text-emerald-600">Active</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Zero data retention. Content is never used to train third-party foundation models.
              </p>
            </div>
          </div>
        </aside>

        <main className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'review' && (
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold text-slate-800">Draft Content Editor</h2>
                  <div className="flex items-center space-x-3 text-xs">
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-500">Channel:</span>
                      <select
                        value={selectedChannel}
                        onChange={(e) => setSelectedChannel(e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded px-2 py-1 font-medium focus:ring-1 focus:ring-indigo-500"
                      >
                        <option>Instagram</option>
                        <option>LinkedIn</option>
                        <option>Google Ad</option>
                        <option>Blog Post</option>
                      </select>
                    </div>
                    <label className="flex items-center space-x-1.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isAiAssisted}
                        onChange={(e) => setIsAiAssisted(e.target.checked)}
                        className="rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-slate-600 font-medium">AI-Assisted Draft</span>
                    </label>
                  </div>
                </div>

                <div className="relative">
                  <textarea
                    rows={4}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="w-full p-3.5 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans leading-relaxed"
                    placeholder="Enter social post copy or marketing draft here..."
                  />
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <span>Target: <strong>WCAG 2.2 AA</strong></span>
                    <span>•</span>
                    <span>Strictness: <strong>High</strong></span>
                  </div>
                  <button
                    onClick={handleRunReview}
                    disabled={isAnalyzing}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg font-medium text-sm transition shadow-sm flex items-center space-x-2 disabled:opacity-50"
                  >
                    {isAnalyzing ? (
                      <>
                        <span className="animate-spin">🌀</span>
                        <span>Evaluating Pipeline...</span>
                      </>
                    ) : (
                      <>
                        <span>⚡</span>
                        <span>Run Governance Review</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-semibold text-slate-800">Source-Grounded Evidence Cards</h3>
                    <p className="text-xs text-slate-500">
                      Every flag cites an approved brand rule or fact record. No ungrounded opinions.
                    </p>
                  </div>
                  <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md font-medium">
                    {openFindingsCount} Unresolved Finding{openFindingsCount !== 1 ? 's' : ''}
                  </span>
                </div>

                {findings.map((finding) => (
                  <div
                    key={finding.id}
                    className={`bg-white border-l-4 rounded-r-xl border border-slate-200 shadow-sm p-5 space-y-3 transition ${
                      finding.status === 'accepted'
                        ? 'border-l-emerald-500 opacity-60'
                        : finding.status === 'rejected'
                        ? 'border-l-slate-400 opacity-50'
                        : finding.severity === 'high'
                        ? 'border-l-rose-500'
                        : 'border-l-amber-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-[11px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getSeverityBadge(
                              finding.severity
                            )}`}
                          >
                            {finding.category.toUpperCase()} • {finding.severity.toUpperCase()}
                          </span>
                          {finding.status !== 'open' && (
                            <span className="text-xs font-semibold uppercase text-slate-500">
                              [{finding.status.replace('_', ' ')}]
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-semibold text-slate-900 mt-1">
                          Violation in span: <span className="bg-amber-50 text-amber-900 px-1.5 py-0.5 rounded font-mono font-normal">"{finding.highlightedText}"</span>
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-slate-400 font-mono">
                          Confidence: {(finding.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg space-y-1.5 border border-slate-100">
                      <div>
                        <strong className="text-slate-800">Citing Source: </strong>
                        <span className="font-mono text-indigo-700">{finding.sourceRef}</span>
                      </div>
                      <div>
                        <strong className="text-slate-800">Explanation: </strong>
                        <span>{finding.explanation}</span>
                      </div>
                    </div>

                    <div className="pt-2 flex items-center justify-between border-t border-slate-100">
                      <div className="text-xs">
                        <span className="text-slate-500">Suggested Tracked Change: </span>
                        <span className="font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-200">
                          {finding.suggestedFix}
                        </span>
                      </div>

                      {finding.status === 'open' && (
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleDispute(finding.id)}
                            className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded font-medium transition"
                          >
                            Dispute Rule
                          </button>
                          <button
                            onClick={() => handleReject(finding.id)}
                            className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded font-medium transition"
                          >
                            Ignore
                          </button>
                          {finding.category === 'claim' && (
                            <button
                              onClick={() => handleRouteLegal(finding.id)}
                              className="text-xs bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 px-3 py-1.5 rounded font-medium transition"
                            >
                              Route to Legal
                            </button>
                          )}
                          <button
                            onClick={() => handleAcceptFix(finding.id, finding.highlightedText, finding.suggestedFix)}
                            className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-1.5 rounded font-medium transition shadow-sm"
                          >
                            Accept Fix
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="max-w-5xl mx-auto space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Guideline-Gap Insights & Ambiguity Detector</h2>
                <p className="text-xs text-slate-500">
                  Improvement #3: Repeated creator overrides, disputes, and recurring flags are clustered to detect ambiguous or outdated rules.
                </p>
              </div>

              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded uppercase">
                      High Override Cluster (42%)
                    </span>
                    <h3 className="font-semibold text-slate-900">Guideline Clause §2.1 (Tone & Language)</h3>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">18 Disputes This Month</span>
                </div>

                <p className="text-sm text-slate-600 leading-relaxed">
                  Creators frequently override the rule prohibiting casual greetings ("Hey guys") on Instagram and TikTok posts. Review logs demonstrate writers find the policy too formal for short-form video captions.
                </p>

                <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-lg space-y-1">
                  <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wide">
                    AI-Proposed Guideline Clarification:
                  </h4>
                  <p className="text-sm text-indigo-800">
                    "Permit warm, conversational greetings ('Hey everyone', 'Welcome back') on social and video channels, while retaining professional tone on LinkedIn and press releases."
                  </p>
                </div>

                <div className="flex justify-end space-x-2 pt-2">
                  <button className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded font-medium">
                    Dismiss
                  </button>
                  <button className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded font-medium shadow-sm">
                    Apply Rule Amendment to §2.1
                  </button>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-slate-900">Approved Facts Register — Stale Claims Nearing Expiry</h3>
                  <span className="text-xs bg-rose-100 text-rose-800 px-2 py-0.5 rounded font-medium">Action Required</span>
                </div>
                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                      <tr>
                        <th className="p-2.5">Statistic Claim</th>
                        <th className="p-2.5">Approved Value</th>
                        <th className="p-2.5">Owner</th>
                        <th className="p-2.5">Expiry Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      <tr>
                        <td className="p-2.5 font-medium">Market position claim</td>
                        <td className="p-2.5">Top 5 in category (2025 survey)</td>
                        <td className="p-2.5">Market Research</td>
                        <td className="p-2.5 text-rose-600 font-semibold">Dec 31, 2026</td>
                      </tr>
                      <tr>
                        <td className="p-2.5 font-medium">Customer satisfaction</td>
                        <td className="p-2.5">94% positive rating</td>
                        <td className="p-2.5">Product Ops</td>
                        <td className="p-2.5 text-amber-600 font-semibold">Nov 15, 2026</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'knowledge' && (
            <div className="max-w-5xl mx-auto space-y-6">
              <h2 className="text-lg font-semibold text-slate-900">Brand Knowledge Base & Atomic Rules</h2>
              <p className="text-xs text-slate-500">
                Uploaded guideline documents parsed into atomic, citable rules with vector embeddings.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
                  <h3 className="text-sm font-bold text-slate-800">Guideline Documents (Active: 2)</h3>
                  <ul className="text-xs text-slate-600 space-y-1 list-disc pl-4">
                    <li>DermaCare Global Brand Standards 2026.pdf (14 rules)</li>
                    <li>Influencer Compliance & ASCI Guidelines.docx (6 rules)</li>
                  </ul>
                </div>
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
                  <h3 className="text-sm font-bold text-slate-800">Approved Brand Terminology (38 Entries)</h3>
                  <p className="text-xs text-slate-500">
                    Banned slang, preferred clinical terms, and trademark spelling invariants.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="max-w-5xl mx-auto space-y-6">
              <h2 className="text-lg font-semibold text-slate-900">Immutable Audit Trail & Approvals</h2>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <p className="text-xs text-slate-500">
                  Every decision, approval, and override is immutably logged with timestamp and user ID.
                </p>
                <div className="text-xs space-y-2 font-mono text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div>[2026-10-25 11:22:04 UTC] USER: Shivank Atri (Creator) SUBMITTED content draft #SUB-9021</div>
                  <div>[2026-10-25 11:22:05 UTC] SYSTEM: Executed Deterministic & LLM Review (4 findings generated)</div>
                  <div>[2026-10-25 11:24:10 UTC] USER: Legal Approver ROUTED #f-2 to Regulatory Desk</div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {showCertificate && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4 border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Brandwise Review Certificate</h3>
              <button
                onClick={() => setShowCertificate(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>
            <div className="text-xs space-y-2.5 text-slate-600 font-mono bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div><strong>Certificate ID:</strong> BW-CERT-88419-2026</div>
              <div><strong>Guideline Version:</strong> v2.4 (Active)</div>
              <div><strong>Timestamp:</strong> 2026-10-25T11:45:00Z</div>
              <div><strong>Status:</strong> Approved with Documented Overrides</div>
              <div><strong>DPDP 2025 Compliance:</strong> Purpose Limitation Verified</div>
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowCertificate(false)}
                className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg font-medium"
              >
                Close
              </button>
              <button
                onClick={generatePdfCertificate}
                className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium shadow-sm cursor-pointer"
              >
                Download PDF Certificate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
