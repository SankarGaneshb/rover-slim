# 🎬 Rover-Slim: 30-Second Demo Recording Script

Use this step-by-step checklist to record a smooth, high-impact 30-second silent screen recording (or GIF) of the Rover-Slim Docker Desktop Extension in action.

---

## 🛠️ Recording Setup Checklist
- **Screen Resolution:** 1920x1080 (1080p) or window zoomed to 100% or 110% for crisp readability.
- **Recording Tool:** OBS Studio, Windows Snipping Tool (Record mode: `Win + Shift + R`), or Loom.
- **Docker Desktop State:**
  - Docker Desktop open on screen.
  - Dark mode or Rover Neon theme active.
  - Have at least one fat/unoptimized container in local images (e.g., standard Python app, ~1.2 GB).

---

## ⏱️ Second-by-Second Action Timeline (30s Total)

| Timestamp | Screen Focus | Exact Action to Perform | Key Visual Detail on Screen |
|---|---|---|---|
| **00:00 – 00:05** | **The Pain Point (Bloat)** | Start on **Docker Desktop -> Images** tab. Hover over an unoptimized image (e.g., `1.2 GB`). | Shows the developer problem: huge image size and disk waste. |
| **00:05 – 00:10** | **Open Rover-Slim** | Click **Rover Slim** in the left sidebar navigation. | The Rover-Slim Dashboard opens with **"Eco-Score: 90/100"** and the local image library. |
| **00:10 – 00:15** | **Diagnose & Scan** | Click **"Audit & Slim ➔"** on the target image (or select project repository). | The engine instantly runs AST analysis. KPI cards update showing **Layer Waste** & **Wasted MB**. |
| **00:15 – 00:20** | **Dependency Segregation** | Scroll slightly down to the **Dependency Matrix**. Drag one tool (e.g., `pytest` or `ruff`) into the "Development" column. | Shows the interactive, visual nature: separating dev bloat from prod in real time. |
| **00:20 – 00:25** | **Diff & GoA Sentinel** | Glance at the **Monaco Diff Inspector** and click **"Verify GoA & Apply"**. | The ephemeral test container boots, passes health check, and flashes **Green** (Zero Breakage). |
| **00:25 – 00:30** | **The Big Win** | Show the final KPI gauge: **214 MB (Lean) — 82.6% Size Reduction**. Pause cursor over the green tag. | Clear, dramatic before-and-after proof. |

---

## 💡 Tips for Maximum Conversion
1. **No audio needed:** Silent with smooth, steady mouse movements converts best for GitHub READMEs, Reddit, and X/LinkedIn.
2. **Smooth Mouse Movement:** Avoid fast, jerky cursor moves; move deliberately between buttons.
3. **Export Settings:**
   - Export as **MP4** (H.264, 30 fps, ~1080p).
   - If generating a GIF: keep file size under 15 MB (15–20 fps, 720p or 1080p compressed) so it loads instantly on GitHub and mobile.
