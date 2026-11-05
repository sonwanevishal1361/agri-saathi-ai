# AgriSaathi AI (कृषी साथी AI) — "Digital Krishi Premium" Design Plan

**Document Version**: 2.0  
**Target Platform**: Mobile-first Indian Farmer Experience (PWA / Streamlit Web)  
**Target Viewports**: Mobile (360px - 412px, baseline 390px) & Desktop (1024px - 1440px, baseline 1280px)  
**Language Context**: Multilingual Native (Marathi default `mr`, Hindi `hi`, English `en`)  
**Design Standard**: WCAG 2.1 AA High Contrast, 56px+ Touch Targets, Three.js Procedural 3D  

---

## 1. Design Vision & Direction: "Digital Krishi Premium"

AgriSaathi AI is transformed from a utilitarian software interface into a **trusted, high-tech, and reassuring digital companion** for Indian farmers. The visual atmosphere evokes **sunrise over a lush green field in Maharashtra**—grounded in fertile earth, illuminated by warm morning sunlight, and elevated with subtle glassmorphism and real-time procedural 3D elements.

### Key Tenets
1. **Dignity & Polish**: The app feels like a world-class financial or agronomic platform (like Apple Health or a premium agritech SaaS), never a compromised "basic" or low-effort project.
2. **Numbers & Visuals Do the Talking**: High cognitive ease. Critical data points (temperatures, market prices, growth days, spray safety) are large, bold, and color-coded.
3. **True Procedural 3D (Under 40KB footprint)**: Procedural Three.js geometry without external model files or licenses. Ambient weather-reactive scene (sun by day, moon by night, rain droplets during precipitation).
4. **Zero Duplicate Navigation**: Exactly one clear navigation system: slim floating header on desktop, and a fixed bottom thumb-navigation bar with an elevated center mic button on mobile.
5. **Rigorous Multilingual Fidelity**: Zero leftover English strings on Marathi or Hindi screens. Weather conditions, units (`किमी/तास`, `मिमी`, `₹/क्विंटल`), and labels are localized through `utils/language.py`.
6. **Single Attribution**: "Architect: Vishal Sonwane" is displayed **once**, gracefully in the footer, removing duplicate clutter.

---

## 2. Design Tokens & CSS Variables

All tokens are declared in `:root` inside `ui/theme.py`:

```css
:root {
    /* --- Natural Agricultural Color System --- */
    --agri-deep-forest:   #1B5E20; /* Primary brand & dark header accents */
    --agri-leaf:          #2E7D32; /* Primary action green, spray OK */
    --agri-fresh-lime:    #8BC34A; /* Growth accents, stage progression */
    --agri-harvest-gold:  #F9A825; /* Mandi net profit highlight, podium 1st */
    --agri-sunrise-orange:#FF8F00; /* Sunlight warmth, active advisory alerts */
    --agri-soil-brown:    #6D4C41; /* Grounding earth boundaries, diary */
    --agri-sky-blue:      #4FC3F7; /* Moisture, weather diagnostics */
    --agri-cream:         #FFF8E1; /* Warm soothing card & banner background */
    --agri-ink:           #1F2A1F; /* High-contrast outdoor-readable text */

    /* --- Surfaces & Glassmorphism --- */
    --agri-bg-page:       #F8FAF8; /* Soft ambient agrarian tint */
    --agri-surface-glass: rgba(255, 255, 255, 0.88);
    --agri-glass-border:  rgba(200, 230, 213, 0.75);
    --agri-card-shadow:   0 8px 24px -4px rgba(15, 56, 34, 0.08), 0 2px 6px rgba(0,0,0,0.04);
    --agri-card-hover:    0 14px 36px -6px rgba(15, 56, 34, 0.16), 0 4px 10px rgba(0,0,0,0.06);

    /* --- Night Field Dark Theme (Optional toggle) --- */
    --agri-night-bg:      #0B1B10;
    --agri-night-surface: #122818;
    --agri-night-border:  rgba(139, 195, 74, 0.25);
    --agri-night-text:    #E8F5E9;

    /* --- Typography & Ergonomics --- */
    --agri-font-family:   'Noto Sans Devanagari', 'Poppins', -apple-system, sans-serif;
    --agri-base-size:     18px;
    --agri-touch-target:  56px;
    --agri-radius-card:   22px;
    --agri-radius-pill:   32px;
}
```

---

## 3. 3D Procedural Scene Architecture (`ui/components/hero_3d.py`)

### Specifications
- **Technology**: Three.js r128 loaded via CDN inside `st.components.v1.html`.
- **Constraint**: Strict maximum of **ONE** WebGL canvas per screen.
- **Resource Footprint**: Zero external asset downloads (`.gltf`, `.bin`, `.png`). 100% procedural low-poly geometry created from primitives (`CylinderGeometry`, `SphereGeometry`, `PlaneGeometry`).
- **Performance Budget**:
  - FPS throttled to **30-45 FPS** via `requestAnimationFrame` delta tracking.
  - `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` to prevent overheating on budget 4K displays.
  - Paused when page visibility is hidden (`visibilitychange` listener).
  - Canvas height: **240px** on desktop, **200px** on mobile.

### Scene Composition & Dynamic Data Binding
1. **Rolling Green Terrain**: Procedural undulating vertex plane with soft pasture green gradient (`#2e7d32` to `#388e3c`).
2. **Atmospheric Lighting**:
   - Day Mode (Sun): Warm directional light (`#fff8e1`, intensity 1.2) + soft hemisphere light. Golden ambient sun disk with glow shaders.
   - Night Mode (Moon & Stars): Deep indigo ambient light + silver moon sphere + sparkling particulate stars.
3. **Weather Reaction**:
   - Rain conditions: Particle system of 200 falling translucent rain streaks with ground ripples.
   - Cloudy conditions: 4 procedural fluffy white low-poly cloud clusters drifting across the field.
4. **Crops & Tractor**:
   - Procedural swaying plants matching active crop (Cotton white puffs, Soybean leafy clusters, Golden wheat ears) using subtle sine-wave vertex sway (`Math.sin(time + x)`).
   - Low-poly red & black agricultural tractor with turning wheels.
5. **Interactive Controls & Fallbacks**:
   - Touch drag / mouse parallax rotates the field gently.
   - Low-end fallback: If WebGL context fails, automatically switches to a high-res CSS scenic gradient card with static SVG illustration.

---

## 4. Reusable Component Catalog (`ui/components/`)

| File | Component | Description & Interactions |
| :--- | :--- | :--- |
| `theme.py` | `inject_custom_theme()` | Global CSS design tokens, Streamlit decoration cleanups, 56px touch target rules, Devanagari typography, and glassmorphism styling. |
| `hero_3d.py` | `render_hero_3d_field()` | Procedural 3D farm scene with real-time day/night lighting, weather particles, and floating farmer greeting glass card. |
| `weather_card.py` | `render_weather_widget()` | Giant animated weather condition visual, large temperature number, 3-metric chips (wind, humidity, rain), big spray advisory status pill, TTS speech button, and 5-day forecast strip. |
| `action_tile.py` | `render_action_grid()` | 6 distinct glassmorphism action tiles with themed icons, live telemetry badges, and direct navigation buttons. |
| `crop_card.py` | `render_crop_tracker_card()` | 6-stage lifecycle progress ring (sowing to harvest), days-to-harvest counter, acreage tag, and next agronomic action badge with 3D lift. |
| `bottom_nav.py` | `render_bottom_nav()` | Mobile-only fixed bottom navigation bar with 5 thumb destinations and an elevated center voice mic button. |
| `voice_button.py` | `render_voice_mic_button()` | Big Web Speech API speech-to-text dictation button (`mr-IN`, `hi-IN`, `en-IN`) with audio wave ripple indicator. |
| `podium_card.py` | `render_mandi_podium()` | 🥇 1st (Gold), 🥈 2nd (Silver), 🥉 3rd (Bronze) APMC market cards highlighting highest net transport return and freshness. |
| `chat_bubble.py` | `render_chat_bubble()` | WhatsApp-style chat bubbles with farmer/advisor avatars, typing indicator animation, and audio speech readout button. |
| `skeleton.py` | `render_skeleton_card()` | Shimmering placeholder skeletons while asynchronous services compute forecasts and mandi prices. |
| `empty_state.py` | `render_empty_state()` | Friendly agricultural sprout illustration with encouraging multilingual copy and a large primary action button. |

---

## 5. Screen-by-Screen Redesign Specifications

### 1. Home Dashboard (`ui/dashboard.py`)
- **Hero 3D Field Vitrine**: Dynamic 3D landscape with rolling terrain, swaying crop, and glass greeting banner (`राम राम, रमेश पाटील! 🙏`).
- **Live Weather & Spray Advisory**: Current temperature in 40px bold text, animated weather icon, wind/rain/humidity chips, giant spray pill (`✅ फवारणीस अनुकूल`), and speaker audio button.
- **5-Day Mini Forecast Strip**: Visual day-by-day temperature highs/lows and rain likelihood badges.
- **AI Farming Advisor Entry**: Dedicated search bar + big microphone button + 4 contextual suggestion chips.
- **Quick Action Grid**: 6 distinct tiles (`🤖 AI सल्ला`, `🌾 माझी शेती`, `📈 बाजारभाव`, `🌦️ हवामान`, `📒 शेती हिशोब`, `🏛️ शासकीय योजना`).
- **Active Crops Tracker**: Real farmer crops with 6-stage growth pipeline, days-to-harvest badge, and actionable ICAR care advice.
- **Mandi Rates Podium**: Top 3 APMC markets for cotton/soybean with distance in km and net return after transport deductions.
- **Farm Financial Telemetry**: Total expenses, harvest sales, and net profit metric cards with trend indicators.

### 2. AI Chat Advisor (`ui/chat_page.py`)
- WhatsApp-style chat layout.
- AI Advisor avatar with friendly green sprout branding.
- Quick-tap suggestion chips for zero-typing interaction.
- Real-time speech input (Web Speech API) in Marathi, Hindi, and English.
- Speaker icon next to each assistant answer for TTS audio readout in the farmer's native dialect.
- Streaming typing indicator animation.

### 3. Mandi Market Rates (`ui/market_page.py`)
- Commodity dropdown with Devanagari names.
- Top 3 APMC markets as an olympic-style podium (Gold, Silver, Bronze) with net transport profit prominently highlighted.
- Interactive chart comparing prices across nearby districts.
- Direct distance calculation from farmer's village.

### 4. My Crops & Crop Detail (`ui/crops_page.py`, `ui/crop_detail.py`)
- Active crop cards with circular progress ring indicating days to harvest.
- 6-stage visual pipeline with glowing active stage indicator.
- Actionable ICAR university-recommended care tips for current stage.
- One-tap "➕ नवीन पीक जोडा" action.

### 5. Farm Diary & Expenses (`ui/diary_page.py`, `ui/expenses_page.py`)
- Clear categorized cards for Seed, Fertilizer, Pesticide, Labor, and Irrigation costs.
- Big touch-friendly number inputs.
- Simplified activity logging with date badges.

### 6. Government Schemes (`ui/schemes_page.py`)
- Visual subsidy cards with benefit amounts (e.g. `₹६,००० / वर्ष` for PM-Kisan).
- Clear eligibility checklist and direct link to official portals (Mahadbt, PMFBY).

---

## 6. Streamlit DOM & CSS Hardening

To ensure a seamless, native app feel rather than a default Streamlit dashboard:
1. **Hide Streamlit Clutter**:
   - `header { visibility: hidden; }`
   - `#MainMenu { visibility: hidden; }`
   - `footer { visibility: hidden; }`
   - `[data-testid="stDecoration"] { display: none; }`
   - `[data-testid="stToolbar"] { display: none; }`
   - `[data-testid="stStatusWidget"] { display: none; }`
2. **Layout Boundaries**:
   - Max width capped at `1280px` for optimal reading comfort on wide monitors.
   - Desktop padding normalized to `1rem 1.5rem 6rem 1.5rem`.
   - Mobile padding tightened to `0.5rem 0.75rem 6.5rem 0.75rem` to prevent horizontal scrolling.
3. **Form Controls & Touch Targets**:
   - All `st.button`, `st.selectbox`, `st.text_input` enforced at minimum `56px` height.
   - Border radius set to `16px-20px`.
   - Focus rings styled with deep emerald `--agri-leaf`.

---

## 7. Multilingual i18n Strategy

All strings must resolve through `utils/language.py` (`t(key, lang)`):
- **Units**:
  - `km/h` -> Marathi `किमी/तास`, Hindi `किमी/घंटा`, English `km/h`
  - `mm` -> Marathi `मिमी`, Hindi `मिमी`, English `mm`
  - `Acres` -> Marathi `एकर`, Hindi `एकड़`, English `Acres`
  - `Quintal` -> Marathi `क्विंटल`, Hindi `क्विंटल`, English `Quintal`
- **Weather Conditions**:
  - `Clear sky` -> Marathi `निरभ्र आकाश`, Hindi `साफ आसमान`
  - `Partly cloudy` -> Marathi `अंशतः ढगाळ`, Hindi `आंशिक बादल`
  - `Cloudy / Overcast` -> Marathi `ढगाळ हवामान`, Hindi `घने बादल`
  - `Rain / Showers` -> Marathi `पाऊस / सरी`, Hindi `बारिश / बौछारें`
  - `Thunderstorm` -> Marathi `वादळी पाऊस`, Hindi `तूफानी बारिश`
  - `Fog / Mist` -> Marathi `धुके`, Hindi `कोहरा`
- **Spray Advisories**:
  - Spray OK: `फवारणीस अनुकूल हवामान` / `छिड़काव के लिए अनुकूल मौसम`
  - Spray Warning: `आज फवारणी टाळा` / `आज छिड़काव न करें`

---

## 8. Implementation Phases & Quality Checklist

### Phases
1. **Phase 1: Design Plan & i18n Dictionary Expansion**:
   - Write `DESIGN_PLAN.md`.
   - Expand `utils/language.py` with weather condition translations, localized units, and forecast labels.
2. **Phase 2: Core Design Tokens & Component Library**:
   - Refactor `ui/theme.py` with the complete "Digital Krishi Premium" palette and Streamlit cleanup rules.
   - Build 3D procedural field hero in `ui/components/hero_3d.py`.
   - Create and upgrade components (`weather_card.py`, `action_tile.py`, `crop_card.py`, `podium_card.py`, `chat_bubble.py`, `skeleton.py`, `empty_state.py`, `bottom_nav.py`, `voice_button.py`).
3. **Phase 3: Screen Modernization**:
   - Upgrade `ui/dashboard.py`, `ui/chat_page.py`, `ui/market_page.py`, `ui/crops_page.py`, `ui/diary_page.py`, `ui/expenses_page.py`, `ui/weather_page.py`, `ui/schemes_page.py`, `ui/profile_page.py`, and `app.py`.
4. **Phase 4: Visual Acceptance & Iterative Critique**:
   - Run Streamlit in headless mode.
   - Capture Playwright screenshots at **390px (Mobile)** and **1280px (Desktop)**.
   - Honestly critique against the quality checklist and iterate.
5. **Phase 5: Automated Testing & Verification**:
   - Run `pytest -v` (all 127 tests must pass).
   - Run `ruff check .` (0 errors).
   - Produce final delivery report.

### Quality Checklist
- [x] First screen has a clear focal point and looks premium in under 2 seconds.
- [x] Touch targets $\ge 56\text{px}$; text contrast meets WCAG AA; readable in bright sunlight.
- [x] No horizontal scroll at 360px, 390px, 412px.
- [x] Only one navigation system visible; no duplicated links.
- [x] No untranslated strings in any language.
- [x] 3D scene falls back gracefully; page stays smooth on a low-end phone.
- [x] No console errors; all tests and ruff pass.
