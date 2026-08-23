# JeevikaAI — 3 to 5 Minute Hackathon Presentation & Live Demo Script

Use this script during live jury evaluation to deliver a compelling, high-impact demonstration.

---

## 🎯 The Pitch (60 Seconds)

> *"Judges, imagine you are an Indian vegetable vendor in Azadpur or Vashi with ₹2,000 in your pocket. Every morning at 5 AM, you face a critical dilemma: What should I buy? How much can I afford? What if tomato prices surged 20% overnight? What if it rains and my tomatoes rot by afternoon?*
>
> *Existing AI chatbots give generic, dangerous advice without knowing wholesale prices or budget limits. **JeevikaAI** is the first **Constraint-Aware AI Decision Engine** for street vendors. It maximizes daily profit while enforcing a hard budget cap, penalizing perishability waste, and explaining every single rupee allocated in simple Hindi and English."*

---

## 🚀 Live Demo Flow (3 Minutes)

### Step 1: Baseline Recommendation (30s)
1. Show the **Vendor Constraints Panel**:
   - Budget: `₹2,000`
   - Stock on hand: `5 kg Tomato`, `3 kg Onion`, `8 kg Potato`
   - Location: `Delhi (Azadpur Mandi)`
2. Click **`GENERATE PURCHASE PLAN`** (or the top **`3-Min Demo Flow`** button).
3. Point out the results:
   - **Total Investment**: Strictly within ₹2,000 (e.g. ₹1,680) with a healthy emergency cash buffer (₹320).
   - **Expected Profit**: ~₹550 with ROI +32%.
   - **Tomato Buy**: System buys *only* enough to meet today's expected demand because Tomato rots in 2 days.
   - **Risk Score**: `LOW` with transparent breakdown.

### Step 2: What-If Scenario A — Budget Drop (30s)
1. Ask the judge: *"What if the vendor only has ₹1,500 today?"*
2. Click the preset chip **`₹1,500 Budget`** in the **What-If Simulator**.
3. Point out the instant delta:
   - System automatically protects durable root vegetables (Onion, Potato) while scaling down perishable risk.
   - Total spending never exceeds ₹1,500.

### Step 3: What-If Scenario B — Price Shock (30s)
1. Ask the judge: *"What if Mandi Tomato wholesale price surges +20% due to monsoon supply disruption?"*
2. Click the preset chip **`+20% Tomato Price`**.
3. Point out how the optimizer dynamically reallocates capital to high-margin Onions, safeguarding vendor profits from sudden market spikes.

### Step 4: Explainability & Language Inclusivity (30s)
1. Click the language toggle to **`हिंदी (Hindi)`**.
2. Scroll to **`यह सिफारिश क्यों की गई है? (Why This?)`**.
3. Show the grounded, zero-hallucination explanation in plain Hindi that street vendors can actually understand.
4. Show the **Market Intelligence Hub** with 14-day Mandi Price and Arrival charts.

---

## 💡 Key Architectural Takeaways for Judges
1. **Mathematical Optimization, Not LLM Hallucination**: Purchasing quantities are derived deterministically using bounded profit optimization under linear budget constraints.
2. **Kaggle-Grounded Multi-Signal Pipeline**: Combines supply-side Mandi arrivals, retail demand velocity, and meteorological rainfall dampeners without false 1-to-1 joins.
3. **Inclusive, Mobile-First UX**: Bilingual English & Hindi interface with large touch targets.
