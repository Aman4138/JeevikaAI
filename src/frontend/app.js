/**
 * JeevikaAI Frontend Application Engine
 * Handles State, Real-Time Bilingual Switching (EN/HI), Chart.js Visualizations,
 * API Integrations, What-If Simulation, and 3-Minute Demo Walkthrough.
 */

// Application State
const state = {
  lang: 'en', // 'en' or 'hi'
  currentCommodity: 'tomato',
  currentLocation: 'Delhi',
  lastRecommendation: null,
  marketChart: null,
  demoStep: 0
};

// Bilingual Localization Dictionary
const I18N = {
  en: {
    appTagline: "Constraint-Aware AI Decision Making for Indian Street & Vegetable Vendors",
    badgeNovelty: "Deterministic Bounded Optimization — Zero AI Hallucinations",
    heroTitle: "Smart Daily Purchasing & Budget Allocation Engine",
    heroDesc: "Empowering small street vendors to maximize daily profit, eliminate perishable vegetable waste, and survive wholesale price shocks.",
    txtDisclaimer: "All projections are decision-support estimates grounded in Kaggle mandi data.",
    demoBtn: "3-Min Demo Flow",
    vendorInputs: "Vendor Constraints",
    step1: "Step 1",
    budget: "Available Budget:",
    location: "Market / City Location:",
    invTitle: "Current Stock on Hand:",
    invTomato: "Tomato",
    invOnion: "Onion",
    invPotato: "Potato",
    riskPref: "Risk Preference:",
    riskCons: "Conservative",
    riskConsSub: "सुरक्षित",
    riskBal: "Balanced",
    riskBalSub: "संतुलित",
    riskAgg: "Aggressive",
    riskAggSub: "उच्च लाभ",
    btnPlan: "GENERATE PURCHASE PLAN",
    weatherContext: "Mandi Weather & Supply Signal",
    temp: "Temperature",
    precip: "Precipitation",
    kpiInvest: "Total Investment",
    kpiProfit: "Expected Profit",
    kpiRemaining: "Remaining Cash",
    kpiRisk: "Decision Risk",
    recTableTitle: "Optimized Purchase Quantities",
    recTableSubtitle: "Guaranteed within available budget • Perishability waste strictly penalized",
    thProduct: "Commodity",
    thStock: "Stock",
    thDemand: "Demand",
    thRecBuy: "Recommended Buy",
    thCost: "Cost (₹)",
    thProfit: "Exp. Profit",
    thRisk: "Perish Risk",
    whyTitle: "Why are we recommending this?",
    whySub: "Transparent mathematical reasoning grounded in vendor constraints",
    rulesTitle: "Deterministic Decision Rules Enforced:",
    whatifTitle: "What-If Scenario Simulator",
    whatifSub: "Stress-test against budget drops, wholesale price surges, and rain shocks",
    simBudget: "Simulated Budget:",
    simPrice: "Tomato Price Shock:",
    simDemand: "Market Demand Shift:",
    btnSim: "RUN SIMULATION",
    marketHubTitle: "Mandi Market Intelligence & Price History",
    marketHubSub: "Recent modal prices (₹/kg) and wholesale arrivals from Kaggle Agmarknet records",
    latestModal: "Latest Modal Price",
    priceBand: "Min - Max Band",
    retailPrice: "Estimated Retail Price",
    arrivals: "Recent Mandi Arrivals"
  },
  hi: {
    appTagline: "भारतीय सब्जी व ठेला व्यापारियों के लिए बाधा-सचेत (Constraint-Aware) AI निर्णय प्रणाली",
    badgeNovelty: "नियम-आधारित सटीक ऑप्टिमाइज़ेशन — शून्य गलतियां (No Hallucination)",
    heroTitle: "दैनिक खरीद और बजट आवंटन सहायक",
    heroDesc: "छोटे सब्जी विक्रेताओं के दैनिक मुनाफे को बढ़ाने, टमाटर जैसी सब्जियों को सड़ने से बचाने और मंडी भाव के झटकों से सुरक्षा के लिए।",
    txtDisclaimer: "सभी आंकड़े वास्तविक मंडी डेटा और आपके बजट पर आधारित निर्णय-सहायता अनुमान हैं।",
    demoBtn: "3-मिनट डेमो टूर",
    vendorInputs: "विक्रेता की स्थितियां (Constraints)",
    step1: "चरण 1",
    budget: "उपलब्ध बजट (पूंजी):",
    location: "मंडी / शहर चुनें:",
    invTitle: "दुकान में बचा हुआ स्टॉक:",
    invTomato: "टमाटर",
    invOnion: "प्याज़",
    invPotato: "आलू",
    riskPref: "जोखिम प्राथमिकता:",
    riskCons: "सुरक्षित",
    riskConsSub: "कम जोखिम",
    riskBal: "संतुलित",
    riskBalSub: "मध्यम",
    riskAgg: "उच्च लाभ",
    riskAggSub: "अधिक खरीद",
    btnPlan: "खरीद योजना तैयार करें",
    weatherContext: "मंडी का मौसम व आवक स्थिति",
    temp: "तापमान",
    precip: "वर्षा (बारिश)",
    kpiInvest: "कुल निवेश लागत",
    kpiProfit: "अनुमानित मुनाफा",
    kpiRemaining: "बचा हुआ नकद",
    kpiRisk: "जोखिम स्तर",
    recTableTitle: "सिफारिश की गई खरीद मात्रा",
    recTableSubtitle: "बजट सीमा के पूर्णतः भीतर • खराबी व नुकसान से पूर्ण सुरक्षा",
    thProduct: "सब्जी",
    thStock: "पुराना स्टॉक",
    thDemand: "मांग",
    thRecBuy: "कितना खरीदें",
    thCost: "लागत (₹)",
    thProfit: "मुनाफा",
    thRisk: "खराबी जोखिम",
    whyTitle: "यह सिफारिश क्यों की गई है? (Why This?)",
    whySub: "पारदर्शी और तर्कसंगत गणितीय कारण",
    rulesTitle: "लागू किए गए व्यापारिक नियम:",
    whatifTitle: "अगर ऐसा हुआ तो? (What-If सिम्युलेटर)",
    whatifSub: "बजट घटने, टमाटर के दाम बढ़ने या बारिश होने पर नई योजना देखें",
    simBudget: "बदला हुआ बजट:",
    simPrice: "टमाटर भाव में बदलाव:",
    simDemand: "ग्राहक मांग में बदलाव:",
    btnSim: "सिम्युलेशन चलाएं",
    marketHubTitle: "मंडी भाव और आवक विश्लेषण",
    marketHubSub: "एगमार्कनेट (Agmarknet) रिकॉर्ड से दैनिक थोक भाव और आवक",
    latestModal: "ताजा थोक भाव",
    priceBand: "न्यूनतम - अधिकतम",
    retailPrice: "खुदरा बिक्री दर",
    arrivals: "मंडी में ताजा आवक"
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  setupEventListeners();
  fetchMarketData(state.currentCommodity, state.currentLocation);
  generateRecommendation(); // Initial load
});

// Setup Event Listeners
function setupEventListeners() {
  // Language switcher
  document.getElementById('lang-en').addEventListener('click', () => setLanguage('en'));
  document.getElementById('lang-hi').addEventListener('click', () => setLanguage('hi'));

  // Quick budget chips
  document.querySelectorAll('.btn-chip').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.btn-chip').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      const val = e.target.getAttribute('data-budget');
      document.getElementById('input-budget').value = val;
      document.getElementById('val-budget-disp').innerText = `₹${parseInt(val).toLocaleString()}`;
    });
  });

  document.getElementById('input-budget').addEventListener('input', (e) => {
    const val = e.target.value || 0;
    document.getElementById('val-budget-disp').innerText = `₹${parseInt(val).toLocaleString()}`;
  });

  // Location selector change
  document.getElementById('select-location').addEventListener('change', (e) => {
    state.currentLocation = e.target.value;
    fetchMarketData(state.currentCommodity, state.currentLocation);
    generateRecommendation();
  });

  // Primary action button
  document.getElementById('btn-generate-plan').addEventListener('click', () => {
    generateRecommendation();
  });

  // What-if sliders
  const simBudget = document.getElementById('slider-sim-budget');
  simBudget.addEventListener('input', (e) => {
    document.getElementById('val-sim-budget').innerText = `₹${parseInt(e.target.value).toLocaleString()}`;
  });

  const simPrice = document.getElementById('slider-sim-price');
  simPrice.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    document.getElementById('val-sim-price').innerText = `${val >= 0 ? '+' : ''}${val}%`;
  });

  const simDemand = document.getElementById('slider-sim-demand');
  simDemand.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    document.getElementById('val-sim-demand').innerText = `${val >= 0 ? '+' : ''}${val}%`;
  });

  // Preset Scenario Buttons
  document.getElementById('btn-scen-budget-drop').addEventListener('click', () => {
    simBudget.value = 1500;
    document.getElementById('val-sim-budget').innerText = '₹1,500';
    simPrice.value = 0;
    document.getElementById('val-sim-price').innerText = '+0%';
    simDemand.value = 0;
    document.getElementById('val-sim-demand').innerText = '0%';
    runWhatIfSimulation("Budget Drop to ₹1,500");
  });

  document.getElementById('btn-scen-tomato-surge').addEventListener('click', () => {
    simBudget.value = 2000;
    document.getElementById('val-sim-budget').innerText = '₹2,000';
    simPrice.value = 20;
    document.getElementById('val-sim-price').innerText = '+20%';
    simDemand.value = 0;
    document.getElementById('val-sim-demand').innerText = '0%';
    runWhatIfSimulation("Tomato Price Surge (+20%)");
  });

  document.getElementById('btn-scen-rain-slump').addEventListener('click', () => {
    simBudget.value = 2000;
    document.getElementById('val-sim-budget').innerText = '₹2,000';
    simPrice.value = 0;
    document.getElementById('val-sim-price').innerText = '+0%';
    simDemand.value = -20;
    document.getElementById('val-sim-demand').innerText = '-20%';
    runWhatIfSimulation("Monsoon Rain Slump (-20% Demand)");
  });

  document.getElementById('btn-run-simulation').addEventListener('click', () => {
    runWhatIfSimulation("Custom Scenario");
  });

  // Commodity Tabs
  document.querySelectorAll('.tab-comm').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-comm').forEach(b => b.classList.remove('active'));
      const target = e.currentTarget;
      target.classList.add('active');
      state.currentCommodity = target.getAttribute('data-comm');
      fetchMarketData(state.currentCommodity, state.currentLocation);
    });
  });

  // ML Metrics Modal
  const modal = document.getElementById('modal-metrics');
  document.getElementById('btn-metrics-modal').addEventListener('click', () => {
    fetchMetrics();
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  });
  document.getElementById('btn-close-metrics').addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  });
  document.getElementById('btn-close-metrics-footer').addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  });

  // Demo flow walkthrough
  document.getElementById('btn-quick-demo').addEventListener('click', startDemoTour);
  document.getElementById('btn-close-demo').addEventListener('click', () => {
    document.getElementById('demo-guide-toast').classList.add('hidden');
  });
  document.getElementById('btn-next-demo').addEventListener('click', advanceDemoStep);
}

// Switch Language (English <-> Hindi)
function setLanguage(lang) {
  state.lang = lang;
  if (lang === 'en') {
    document.getElementById('lang-en').className = "px-2.5 py-1 rounded font-semibold bg-emerald-500 text-slate-950 transition";
    document.getElementById('lang-hi').className = "px-2.5 py-1 rounded font-semibold text-slate-400 hover:text-white transition";
  } else {
    document.getElementById('lang-hi').className = "px-2.5 py-1 rounded font-semibold bg-emerald-500 text-slate-950 transition";
    document.getElementById('lang-en').className = "px-2.5 py-1 rounded font-semibold text-slate-400 hover:text-white transition";
  }

  const dict = I18N[lang];
  document.getElementById('app-tagline').innerText = dict.appTagline;
  document.getElementById('badge-novelty').innerText = dict.badgeNovelty;
  document.getElementById('hero-title').innerText = dict.heroTitle;
  document.getElementById('hero-desc').innerText = dict.heroDesc;
  document.getElementById('txt-disclaimer').innerText = dict.txtDisclaimer;
  document.getElementById('txt-demo-btn').innerText = dict.demoBtn;
  document.getElementById('lbl-vendor-inputs').innerText = dict.vendorInputs;
  document.getElementById('lbl-step1').innerText = dict.step1;
  document.getElementById('lbl-budget').innerText = dict.budget;
  document.getElementById('lbl-location').innerText = dict.location;
  document.getElementById('lbl-inventory-title').innerText = dict.invTitle;
  document.getElementById('lbl-inv-tomato').innerText = dict.invTomato;
  document.getElementById('lbl-inv-onion').innerText = dict.invOnion;
  document.getElementById('lbl-inv-potato').innerText = dict.invPotato;
  document.getElementById('lbl-risk-pref').innerText = dict.riskPref;
  document.getElementById('opt-risk-cons').innerText = dict.riskCons;
  document.getElementById('opt-risk-cons-sub').innerText = dict.riskConsSub;
  document.getElementById('opt-risk-bal').innerText = dict.riskBal;
  document.getElementById('opt-risk-bal-sub').innerText = dict.riskBalSub;
  document.getElementById('opt-risk-agg').innerText = dict.riskAgg;
  document.getElementById('opt-risk-agg-sub').innerText = dict.riskAggSub;
  document.getElementById('btn-plan-text').innerText = dict.btnPlan;
  document.getElementById('lbl-weather-context').innerText = dict.weatherContext;
  document.getElementById('lbl-temp').innerText = dict.temp;
  document.getElementById('lbl-precip').innerText = dict.precip;
  document.getElementById('kpi-lbl-invest').innerText = dict.kpiInvest;
  document.getElementById('kpi-lbl-profit').innerText = dict.kpiProfit;
  document.getElementById('kpi-lbl-remaining').innerText = dict.kpiRemaining;
  document.getElementById('kpi-lbl-risk').innerText = dict.kpiRisk;
  document.getElementById('lbl-rec-table-title').innerText = dict.recTableTitle;
  document.getElementById('lbl-rec-table-subtitle').innerText = dict.recTableSubtitle;
  document.getElementById('th-product').innerText = dict.thProduct;
  document.getElementById('th-curr-stock').innerText = dict.thStock;
  document.getElementById('th-exp-demand').innerText = dict.thDemand;
  document.getElementById('th-rec-buy').innerText = dict.thRecBuy;
  document.getElementById('th-cost').innerText = dict.thCost;
  document.getElementById('th-profit').innerText = dict.thProfit;
  document.getElementById('th-item-risk').innerText = dict.thRisk;
  document.getElementById('lbl-why-title').innerText = dict.whyTitle;
  document.getElementById('lbl-why-sub').innerText = dict.whySub;
  document.getElementById('lbl-rules-title').innerText = dict.rulesTitle;
  document.getElementById('lbl-whatif-title').innerText = dict.whatifTitle;
  document.getElementById('lbl-whatif-sub').innerText = dict.whatifSub;
  document.getElementById('lbl-sim-budget').innerText = dict.simBudget;
  document.getElementById('lbl-sim-price').innerText = dict.simPrice;
  document.getElementById('lbl-sim-demand').innerText = dict.simDemand;
  document.getElementById('btn-sim-text').innerText = dict.btnSim;
  document.getElementById('lbl-market-hub-title').innerText = dict.marketHubTitle;
  document.getElementById('lbl-market-hub-sub').innerText = dict.marketHubSub;
  document.getElementById('lbl-latest-modal').innerText = dict.latestModal;
  document.getElementById('lbl-price-band').innerText = dict.priceBand;
  document.getElementById('lbl-retail-price').innerText = dict.retailPrice;
  document.getElementById('lbl-arrivals').innerText = dict.arrivals;

  // If a recommendation exists, re-render explanation in new language
  if (state.lastRecommendation) {
    renderRecommendation(state.lastRecommendation);
  }
}

// Generate Recommendation API Call
async function generateRecommendation() {
  const budget = parseFloat(document.getElementById('input-budget').value) || 2000.0;
  const invTomato = parseFloat(document.getElementById('inv-tomato').value) || 0.0;
  const invOnion = parseFloat(document.getElementById('inv-onion').value) || 0.0;
  const invPotato = parseFloat(document.getElementById('inv-potato').value) || 0.0;
  
  const riskRadio = document.querySelector('input[name="risk_pref"]:checked');
  const riskProfile = riskRadio ? riskRadio.value : 'balanced';

  const payload = {
    budget: budget,
    inventory: {
      tomato: invTomato,
      onion: invOnion,
      potato: invPotato
    },
    location: state.currentLocation,
    risk_profile: riskProfile,
    language: state.lang
  };

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    const data = await res.json();
    state.lastRecommendation = data;
    renderRecommendation(data);
  } catch (err) {
    console.error("Recommendation Error:", err);
  }
}

// Render Recommendation on UI
function renderRecommendation(data) {
  // Update KPIs
  document.getElementById('kpi-invest').innerText = `₹${data.total_investment.toLocaleString()}`;
  document.getElementById('kpi-profit').innerText = `₹${data.total_expected_profit.toLocaleString()}`;
  document.getElementById('kpi-roi').innerText = `ROI: ${data.roi_pct}%`;
  document.getElementById('kpi-remaining').innerText = `₹${data.remaining_cash.toLocaleString()}`;
  
  const riskTxt = state.lang === 'hi' ? data.risk_level_hi : data.risk_level;
  document.getElementById('kpi-risk-text').innerText = riskTxt;
  document.getElementById('kpi-risk-text').style.color = data.badge_color;
  document.getElementById('kpi-risk-score').innerText = `${data.risk_score}/100`;

  // Render Table Rows
  const tbody = document.getElementById('recommendation-tbody');
  tbody.innerHTML = '';

  data.recommendations.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = "hover:bg-slate-800/40 transition border-b border-slate-800/40";
    
    const displayName = state.lang === 'hi' && item.hindi_name ? item.hindi_name : item.display_name;
    const itemRiskBadge = item.item_risk === 'LOW' 
      ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">LOW</span>`
      : (item.item_risk === 'MEDIUM' 
          ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800">MED</span>`
          : `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800">HIGH</span>`);

    const costLabel = state.lang === 'hi' 
      ? `₹${item.wholesale_cost_per_kg}/किलो (थोक) • ₹${item.retail_selling_price_per_kg}/किलो (बिक्री दर)`
      : `₹${item.wholesale_cost_per_kg}/kg (Wholesale) • ₹${item.retail_selling_price_per_kg}/kg (Est. Retail)`;

    tr.innerHTML = `
      <td class="py-3 px-3">
        <div class="flex items-center gap-2">
          <span class="text-xl">${item.icon}</span>
          <div>
            <div class="font-bold text-white">${displayName}</div>
            <div class="text-[11px] text-slate-400">${costLabel}</div>
          </div>
        </div>
      </td>
      <td class="py-3 px-2 text-center text-slate-300 font-semibold">${item.current_stock_kg} kg</td>
      <td class="py-3 px-2 text-center text-slate-300 font-semibold">${item.estimated_demand_kg} kg</td>
      <td class="py-3 px-3 text-center">
        <span class="inline-block bg-emerald-950 text-emerald-300 border border-emerald-500/40 px-3 py-1 rounded-xl font-extrabold text-sm sm:text-base">
          ${item.recommended_purchase_kg} kg
        </span>
      </td>
      <td class="py-3 px-2 text-right font-bold text-white">₹${item.estimated_purchase_cost.toLocaleString()}</td>
      <td class="py-3 px-2 text-right font-bold text-emerald-400">+₹${item.expected_profit.toLocaleString()}</td>
      <td class="py-3 px-3 text-center">${itemRiskBadge}</td>
    `;
    tbody.appendChild(tr);
  });

  // Render Explanation
  const exp = data.explanation;
  const summaryText = state.lang === 'hi' ? exp.summary_hi : exp.summary_en;
  document.getElementById('txt-explanation-summary').innerText = summaryText;

  const reasonsContainer = document.getElementById('list-product-reasons');
  reasonsContainer.innerHTML = '';
  const reasonsList = state.lang === 'hi' ? exp.product_reasons_hi : exp.product_reasons_en;
  reasonsList.forEach(r => {
    const div = document.createElement('div');
    div.className = "text-xs text-slate-300 pl-3 border-l-2 border-emerald-500/60 leading-relaxed";
    div.innerHTML = r.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
    reasonsContainer.appendChild(div);
  });

  const rulesContainer = document.getElementById('list-decision-rules');
  rulesContainer.innerHTML = '';
  const rulesList = state.lang === 'hi' ? exp.decision_rules_hi : exp.decision_rules_en;
  rulesList.forEach(rule => {
    const li = document.createElement('li');
    li.innerHTML = rule.replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-200">$1</strong>');
    rulesContainer.appendChild(li);
  });

  if (window.lucide) lucide.createIcons();
}

// What-If Simulation API Call
async function runWhatIfSimulation(scenarioLabel) {
  const baseBudget = parseFloat(document.getElementById('input-budget').value) || 2000.0;
  const invTomato = parseFloat(document.getElementById('inv-tomato').value) || 0.0;
  const invOnion = parseFloat(document.getElementById('inv-onion').value) || 0.0;
  const invPotato = parseFloat(document.getElementById('inv-potato').value) || 0.0;
  
  const simBudgetVal = parseFloat(document.getElementById('slider-sim-budget').value) || baseBudget;
  const simPriceVal = parseFloat(document.getElementById('slider-sim-price').value) || 0.0;
  const simDemandVal = parseFloat(document.getElementById('slider-sim-demand').value) || 0.0;

  const payload = {
    base_request: {
      budget: baseBudget,
      inventory: { tomato: invTomato, onion: invOnion, potato: invPotato },
      location: state.currentLocation,
      risk_profile: "balanced",
      language: state.lang
    },
    scenario_name: scenarioLabel,
    scenario_budget: simBudgetVal,
    price_multipliers: {
      tomato: 1.0 + (simPriceVal / 100.0)
    },
    demand_multipliers: {
      all: 1.0 + (simDemandVal / 100.0)
    }
  };

  try {
    const res = await fetch('/api/what-if', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`What-If error: ${res.status}`);
    const data = await res.json();
    renderWhatIfResults(data);
  } catch (err) {
    console.error("What-If Simulation Error:", err);
  }
}

// Render What-If Comparison Cards
function renderWhatIfResults(data) {
  const container = document.getElementById('what-if-results-container');
  const d = data.deltas;
  const scen = data.scenario;
  const base = data.baseline;

  const profitDeltaColor = d.delta_profit >= 0 ? "text-emerald-400" : "text-rose-400";
  const profitSign = d.delta_profit >= 0 ? "+" : "";

  container.innerHTML = `
    <div class="bg-slate-950 p-4 rounded-xl border border-amber-500/30 space-y-3">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
          <i data-lucide="git-compare" class="w-4 h-4"></i>
          <span>Scenario Comparison: <strong>${data.scenario_name}</strong></span>
        </span>
        <span class="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
          Risk: ${base.risk_level} ➔ <strong class="text-amber-400">${scen.risk_level}</strong>
        </span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-500 text-[10px]">Simulated Investment</span>
          <div class="font-bold text-white text-sm">₹${scen.total_investment}</div>
          <div class="text-[10px] text-slate-400">Δ: ₹${d.delta_investment >= 0 ? '+' : ''}${d.delta_investment}</div>
        </div>
        <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-500 text-[10px]">Simulated Profit</span>
          <div class="font-bold ${profitDeltaColor} text-sm">₹${scen.total_expected_profit}</div>
          <div class="text-[10px] ${profitDeltaColor}">Δ: ${profitSign}₹${d.delta_profit}</div>
        </div>
        <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-500 text-[10px]">Remaining Buffer</span>
          <div class="font-bold text-amber-300 text-sm">₹${scen.remaining_cash}</div>
          <div class="text-[10px] text-slate-400">Δ: ₹${d.delta_remaining_cash >= 0 ? '+' : ''}${d.delta_remaining_cash}</div>
        </div>
        <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
          <span class="text-slate-500 text-[10px]">Tomato Recommended</span>
          <div class="font-bold text-white text-sm">
            ${d.product_comparisons[0].scenario_purchase_kg} kg
          </div>
          <div class="text-[10px] text-slate-400">Base: ${d.product_comparisons[0].base_purchase_kg} kg</div>
        </div>
      </div>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
}

// Fetch Market Data & Render Timeseries Chart
async function fetchMarketData(commodity, city) {
  try {
    const res = await fetch(`/api/market-data?commodity=${commodity}&city=${city}`);
    if (!res.ok) throw new Error(`Market data error: ${res.status}`);
    const data = await res.json();

    document.getElementById('val-mkt-modal').innerText = `₹${data.latest_modal_price_rs_kg} / kg`;
    document.getElementById('val-mkt-band').innerText = `₹${data.min_price_rs_kg} - ₹${data.max_price_rs_kg}`;
    document.getElementById('val-mkt-retail').innerText = `₹${data.estimated_retail_price_rs_kg} / kg`;
    document.getElementById('val-mkt-arrivals').innerText = `${data.recent_arrivals_tonnes} Tonnes`;
    
    const sign = data.price_trend_pct_7d >= 0 ? '+' : '';
    document.getElementById('val-mkt-trend').innerText = `${sign}${data.price_trend_pct_7d}% (7-day)`;
    document.getElementById('val-mkt-trend').className = data.price_trend_pct_7d >= 0 
      ? "text-[10px] text-emerald-400 font-semibold" 
      : "text-[10px] text-rose-400 font-semibold";

    // Weather widget update
    if (data.weather) {
      document.getElementById('val-temp').innerText = `${data.weather.temperature_c} °C`;
      document.getElementById('val-precip').innerText = `${data.weather.precipitation_mm} mm`;
      document.getElementById('val-supply-msg').innerText = data.supply_signal;
    }

    renderMarketChart(data.timeseries_14d);
  } catch (err) {
    console.error("Market Data Error:", err);
  }
}

// Chart.js 14-Day Dual Axis Chart (Price ₹/kg vs Arrivals Tonnes)
function renderMarketChart(timeseries) {
  if (!timeseries || timeseries.length === 0) return;

  const ctx = document.getElementById('marketChart').getContext('2d');
  const labels = timeseries.map(d => d.date);
  const modalPrices = timeseries.map(d => d.modal_price);
  const arrivals = timeseries.map(d => d.arrivals);

  if (state.marketChart) {
    state.marketChart.destroy();
  }

  state.marketChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Wholesale Modal Price (₹/kg)',
          data: modalPrices,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.3,
          yAxisID: 'y'
        },
        {
          label: 'Mandi Arrivals (Tonnes)',
          data: arrivals,
          borderColor: '#38bdf8',
          borderDash: [5, 5],
          backgroundColor: 'transparent',
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { size: 11 } }
        }
      },
      scales: {
        x: {
          grid: { color: '#1e293b' },
          ticks: { color: '#64748b', font: { size: 10 } }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: '#1e293b' },
          ticks: { color: '#10b981', font: { size: 10 } },
          title: { display: true, text: 'Price (₹/kg)', color: '#10b981', font: { size: 10 } }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#38bdf8', font: { size: 10 } },
          title: { display: true, text: 'Arrivals (T)', color: '#38bdf8', font: { size: 10 } }
        }
      }
    }
  });
}

// Fetch & Render ML Benchmark Metrics Modal
async function fetchMetrics() {
  try {
    const res = await fetch('/api/model-metrics');
    const data = await res.json();

    const priceTbody = document.getElementById('metrics-price-tbody');
    priceTbody.innerHTML = `
      <tr>
        <td class="p-2 font-medium text-slate-300">${data.price_prediction_model.baseline.algorithm} (Baseline)</td>
        <td class="p-2 text-slate-300 font-bold">${data.price_prediction_model.baseline.r2}</td>
        <td class="p-2 text-slate-300">₹${data.price_prediction_model.baseline.mae}</td>
        <td class="p-2 text-slate-300">₹${data.price_prediction_model.baseline.rmse}</td>
        <td class="p-2 text-slate-300">${data.price_prediction_model.baseline.mape_pct}%</td>
      </tr>
      <tr class="bg-emerald-950/30 font-bold">
        <td class="p-2 text-emerald-400">${data.price_prediction_model.improved.algorithm} (Improved)</td>
        <td class="p-2 text-emerald-400 font-extrabold">${data.price_prediction_model.improved.r2}</td>
        <td class="p-2 text-emerald-400">₹${data.price_prediction_model.improved.mae}</td>
        <td class="p-2 text-emerald-400">₹${data.price_prediction_model.improved.rmse}</td>
        <td class="p-2 text-emerald-400">${data.price_prediction_model.improved.mape_pct}%</td>
      </tr>
    `;

    const demandTbody = document.getElementById('metrics-demand-tbody');
    demandTbody.innerHTML = `
      <tr>
        <td class="p-2 font-medium text-slate-300">${data.demand_estimation_model.baseline.algorithm}</td>
        <td class="p-2 text-slate-300 font-bold">${data.demand_estimation_model.baseline.r2}</td>
        <td class="p-2 text-slate-300">${data.demand_estimation_model.baseline.mae} kg</td>
        <td class="p-2 text-slate-300">${data.demand_estimation_model.baseline.rmse} kg</td>
        <td class="p-2 text-slate-300">${data.demand_estimation_model.baseline.mape_pct}%</td>
      </tr>
      <tr class="bg-purple-950/30 font-bold">
        <td class="p-2 text-purple-400">${data.demand_estimation_model.improved.algorithm}</td>
        <td class="p-2 text-purple-400 font-extrabold">${data.demand_estimation_model.improved.r2}</td>
        <td class="p-2 text-purple-400">${data.demand_estimation_model.improved.mae} kg</td>
        <td class="p-2 text-purple-400">${data.demand_estimation_model.improved.rmse} kg</td>
        <td class="p-2 text-purple-400">${data.demand_estimation_model.improved.mape_pct}%</td>
      </tr>
    `;
  } catch (err) {
    console.error("Metrics fetch error:", err);
  }
}

// 3-Minute Hackathon Demo Tour Guide
function startDemoTour() {
  state.demoStep = 1;
  const toast = document.getElementById('demo-guide-toast');
  toast.classList.remove('hidden');
  renderDemoStep();
}

function advanceDemoStep() {
  state.demoStep = (state.demoStep % 3) + 1;
  renderDemoStep();
}

function renderDemoStep() {
  const badge = document.getElementById('demo-step-badge');
  const text = document.getElementById('demo-step-text');
  const btn = document.getElementById('btn-next-demo');

  badge.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i> Step ${state.demoStep} of 3`;

  if (state.demoStep === 1) {
    text.innerText = "Step 1: Baseline Scenario — Vendor starts with ₹2,000 budget & 5kg Tomato in stock. System calculates optimized buy quantities avoiding tomato rotting.";
    btn.innerText = "Next: What if budget drops to ₹1,500? →";
    document.getElementById('input-budget').value = 2000;
    document.getElementById('inv-tomato').value = 5.0;
    document.getElementById('inv-onion').value = 3.0;
    document.getElementById('inv-potato').value = 8.0;
    generateRecommendation();
  } else if (state.demoStep === 2) {
    text.innerText = "Step 2: What-If Budget Drop — Budget drops from ₹2,000 to ₹1,500. System automatically rebalances, maintaining durable items and scaling down perishables.";
    btn.innerText = "Next: What if Tomato price jumps +20%? →";
    document.getElementById('slider-sim-budget').value = 1500;
    document.getElementById('val-sim-budget').innerText = '₹1,500';
    document.getElementById('slider-sim-price').value = 0;
    document.getElementById('val-sim-price').innerText = '+0%';
    runWhatIfSimulation("Budget Drop to ₹1,500");
  } else if (state.demoStep === 3) {
    text.innerText = "Step 3: What-If Price Surge — Wholesale Tomato jumps +20%. System reallocates capital into high-margin Onions and Potatos.";
    btn.innerText = "Finish Demo Tour ✓";
    document.getElementById('slider-sim-price').value = 20;
    document.getElementById('val-sim-price').innerText = '+20%';
    runWhatIfSimulation("Tomato Price Surge (+20%)");
  }
  if (window.lucide) lucide.createIcons();
}
