# Brandwise: AI Brand-Governance Platform
## Inkloom AI Hackathon — Round 1 & Implementation Package

Brandwise is a pre-publication brand governance platform that acts as a intelligent review layer between draft and publish. It checks content against approved brand guidelines, fact registers, terminology lists, and asset libraries, providing source-grounded explanations and tracked-change suggestions while keeping humans strictly in control.

---

## 🚀 Key Features & Three Named Improvements

1. **Source-Grounded, Explainable Findings**: Every flag cites the exact rule or fact it came from, a quoted excerpt, a confidence level, and a plain-language reason. Ungrounded AI opinions are labelled "advisory".
2. **Claim and Fact Verification**: Numbers, superlatives, price/offer statements, and health/finance claims are matched against an approved-facts register with owners and expiry dates.
3. **Guideline-Gap Insights**: Repeated overrides, disputed flags, and recurring mistakes are clustered to show which guidelines are ambiguous, outdated, or in need of clarification.

---

## 📂 Project Structure

```
codex/
├── backend/
│   ├── app/
│   │   ├── api/routers.py
│   │   ├── core/config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── Dashboard.tsx
├── infra/
│   ├── Dockerfile.backend
│   └── Dockerfile.worker
├── tests/
└── docs/
```

---

## 🛠️ Quickstart

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Preview**:
   - The frontend component `frontend/Dashboard.tsx` provides a complete React + Tailwind UI featuring the submission engine, evidence cards, and guideline-gap analytics dashboard.

---

## 📜 Compliance & Ethics
- **DPDP 2025 Compliance**: Purpose limitation, data minimization, no-training API guarantees, and tenant isolation.
- **Human-in-the-Loop**: AI never publishes or overrides; humans make final decisions.
- **Transparency**: Clear AI-assisted badges and full audit logging.
