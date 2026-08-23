# JeevikaAI — Mathematical Formulation & Decision Methodology

---

## 1. Problem Formulation

Small vegetable vendors operate under strict daily resource boundaries:
- Limited liquid cash budget: $B \in \mathbb{R}^+$ (typically ₹500 to ₹5,000)
- Existing non-zero morning inventory: $I_i \ge 0$ for product $i \in \{\text{Tomato, Onion, Potato}\}$
- Uncertainty in customer demand: $\hat{D}_i$ (derived from retail demand estimation model)
- Wholesale unit cost: $c_i$ (derived from Mandi modal price model)
- Retail unit selling price: $p_i$ (derived from retail margin models)
- Perishability / spoilage penalty: $\omega_i \in [0, 1]$ (Tomato: $\omega_{\text{tomato}}=0.15$/day; Onion: $\omega_{\text{onion}}=0.02$/day; Potato: $\omega_{\text{potato}}=0.01$/day)

---

## 2. Constrained Optimization Problem

The vendor seeks to determine purchase quantities $q = [q_1, q_2, \dots, q_n]^T$ that maximize expected net profit while strictly adhering to budget and perishability safety caps:

$$\max_{q \ge 0} \quad \Phi(q) = \sum_{i=1}^{n} \Big( \text{Expected Revenue}_i(q_i) - \text{Purchase Cost}_i(q_i) - \text{Perishability Penalty}_i(q_i) \Big)$$

### Mathematical Components:

1. **Available Total Inventory**:
   $$S_i(q_i) = I_i + q_i$$

2. **Expected Sales Volume**:
   $$V_i(q_i) = \min\big(S_i(q_i), \hat{D}_i \big) = \min(I_i + q_i, \hat{D}_i)$$

3. **Expected Gross Revenue**:
   $$R(q) = \sum_{i=1}^{n} p_i \cdot V_i(q_i)$$

4. **Purchase Investment Cost**:
   $$C(q) = \sum_{i=1}^{n} c_i \cdot q_i$$

5. **Perishability Waste Penalty**:
   $$\text{Waste}_i(q_i) = \lambda_{\text{risk}} \cdot \omega_i \cdot c_i \cdot \max\big(0, S_i(q_i) - \hat{D}_i \big)$$

### Constraints:

1. **Hard Budget Cap**:
   $$\sum_{i=1}^{n} c_i \cdot q_i \le B \cdot \eta_{\text{target}}$$
   where $\eta_{\text{target}} \in [0.80, 0.98]$ reserves a liquid cash buffer.

2. **Non-negativity & Discrete Stepping**:
   $$q_i \ge 0, \quad q_i \in \{0.0, 0.5, 1.0, 1.5, \dots\} \text{ kg}$$

---

## 3. Decision-Support Risk Index Formulation

The composite Risk Score $\mathcal{R} \in [0, 100]$ is computed deterministically across four key vulnerability dimensions:

$$\mathcal{R} = w_{\text{budget}} \cdot \mathcal{S}_{\text{budget}} + w_{\text{perish}} \cdot \mathcal{S}_{\text{perish}} + w_{\text{align}} \cdot \mathcal{S}_{\text{align}} + w_{\text{weather}} \cdot \mathcal{S}_{\text{weather}}$$

| Component | Max Weight | Evaluation Logic |
| :--- | :--- | :--- |
| **Budget Depletion ($\mathcal{S}_{\text{budget}}$)** | 25 pts | Penalizes committing >95% of available cash without an emergency buffer. |
| **Perishable Exposure ($\mathcal{S}_{\text{perish}}$)** | 35 pts | Evaluates ratio of capital locked in short shelf-life items (e.g. Tomatoes, 2-3 days). |
| **Demand Mismatch ($\mathcal{S}_{\text{align}}$)** | 25 pts | Penalizes holding stock exceeding $1.15 \times$ predicted daily demand. |
| **Weather Threat ($\mathcal{S}_{\text{weather}}$)** | 15 pts | Escalates when heavy monsoon rainfall threatens street footfall and accelerates spoilage. |

### Classification Tiers:
- **LOW RISK (0 – 35)**: High cash buffer, balanced durable root vegetable allocation.
- **MEDIUM RISK (36 – 65)**: Moderate perishable commitment; aligned with normal demand.
- **HIGH RISK (66 – 100)**: Over-leveraged capital in perishables or extreme weather threat.
