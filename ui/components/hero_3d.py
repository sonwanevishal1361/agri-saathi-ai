"""Lightweight, battery-efficient interactive 3D farm hero for Indian farmers.

Uses Three.js (pinned r128 via CDN) with procedural low-poly geometry (no external 3D files),
weather-reactive lighting, day/night cycles, swaying crops, and mobile gyroscope/touch parallax.
"""

from typing import Optional
import streamlit.components.v1 as components


def render_hero_3d_field(
    farmer_name: str,
    location_str: str,
    season_str: str,
    helper_text: str,
    crop_name: str = "Cotton",
    weather_condition: str = "Clear sky",
    is_day: bool = True,
    precipitation: float = 0.0,
    height: int = 280,
    lang: str = "mr",
    summary_chips: Optional[list] = None,
):
    """Render a full-width procedural 3D farm hero scene with glass greeting panel."""
    crop_low = (crop_name or "").lower()
    if any(k in crop_low for k in ["cotton", "kapas", "कापूस", "कपास"]):
        crop_type = "cotton"
    elif any(k in crop_low for k in ["wheat", "gehu", "गहू", "गेहूं"]):
        crop_type = "wheat"
    else:
        crop_type = "soybean"

    cond_low = (weather_condition or "").lower()
    is_raining = precipitation > 0.0 or any(k in cond_low for k in ["rain", "drizzle", "shower", "पाऊस", "बारिश"])
    is_cloudy = is_raining or any(k in cond_low for k in ["cloud", "overcast", "ढगाळ", "धुके", "बादल"])

    greeting_title = f"राम राम, {farmer_name}! 🙏" if lang == "mr" else (
        f"नमस्ते, {farmer_name}! 🙏" if lang == "hi" else f"Welcome, {farmer_name}! 🙏"
    )

    chips_html = ""
    if summary_chips:
        chips_html = '<div style="margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px;">'
        for chip in summary_chips:
            chips_html += f'<span style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.3); color: #ffffff; padding: 4px 12px; border-radius: 16px; font-size: 0.82rem; font-weight: 700;">{chip}</span>'
        chips_html += '</div>'

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                overflow: hidden;
                font-family: 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: {'linear-gradient(180deg, #87ceeb 0%, #fff8e1 70%, #d4ebd9 100%)' if is_day else 'linear-gradient(180deg, #0a1128 0%, #071e13 100%)'};
                border-radius: 24px;
                height: {height}px;
                position: relative;
                box-shadow: 0 16px 36px -6px rgba(15, 56, 34, 0.25);
                border: 1.5px solid rgba(134, 239, 172, 0.4);
            }}
            #canvas-container {{
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
                cursor: grab;
            }}
            #canvas-container:active {{ cursor: grabbing; }}
            .glass-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                padding: 24px 28px;
                background: linear-gradient(135deg, rgba(7, 30, 19, 0.85) 0%, rgba(15, 56, 34, 0.72) 45%, rgba(46, 125, 50, 0.5) 100%);
                backdrop-filter: blur(2px);
                -webkit-backdrop-filter: blur(2px);
                color: #ffffff;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                pointer-events: none;
            }}
            .badge-row {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 6px;
            }}
            .brand-pill {{
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                color: #86efac;
                text-transform: uppercase;
                background: rgba(0,0,0,0.25);
                padding: 4px 10px;
                border-radius: 12px;
                border: 1px solid rgba(134,239,172,0.3);
            }}
            .greeting-title {{
                font-size: 1.85rem;
                font-weight: 800;
                margin: 0;
                text-shadow: 0 2px 8px rgba(0,0,0,0.45);
                line-height: 1.2;
            }}
            .helper-subtitle {{
                font-size: 1.02rem;
                color: #d1fae5;
                margin-top: 4px;
                font-weight: 500;
                text-shadow: 0 1px 4px rgba(0,0,0,0.4);
                max-width: 680px;
            }}
            .context-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }}
            .glass-pill {{
                background: rgba(255, 255, 255, 0.18);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.28);
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.82rem;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 5px;
            }}
            .rot-hint {{
                position: absolute;
                bottom: 12px;
                right: 16px;
                font-size: 0.75rem;
                color: rgba(255,255,255,0.75);
                background: rgba(0,0,0,0.3);
                padding: 3px 8px;
                border-radius: 10px;
                pointer-events: none;
            }}
            /* Fallback Card if WebGL fails */
            #fallback {{
                display: none;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #071e13 0%, #1b5e20 50%, #2e7d32 100%);
                padding: 24px;
                color: #fff;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container"></div>
        <div id="fallback">
            <h2>{greeting_title}</h2>
            <p>{helper_text}</p>
        </div>
        <div class="glass-overlay">
            <div>
                <div class="badge-row">
                    <span class="brand-pill">🌱 AgriSaathi AI • डिजिटल कृषी</span>
                    <span style="font-size: 0.8rem; color: #fde047; font-weight: 700;">{'☀️ दिवस' if is_day else '🌙 रात्र'}</span>
                </div>
                <h1 class="greeting-title">{greeting_title}</h1>
                <p class="helper-subtitle">{helper_text}</p>
                <div class="context-row">
                    <span class="glass-pill">📍 {location_str}</span>
                    <span class="glass-pill">🌾 {season_str}</span>
                    <span class="glass-pill">✨ ICAR शिफारस प्रमाणित</span>
                </div>
            </div>
            {chips_html}
            <div class="rot-hint">👆 ३D फिरवून पहा (Drag to rotate)</div>
        </div>

        <script>
            (function() {{
                const container = document.getElementById('canvas-container');
                const fallback = document.getElementById('fallback');

                try {{
                    if (!window.WebGLRenderingContext) throw new Error("No WebGL");
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
                    camera.position.set(0, 4.5, 9);
                    camera.lookAt(0, 1.2, 0);

                    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true, powerPreference: "low-power" }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    container.appendChild(renderer.domElement);

                    // --- LIGHTING ---
                    const hemiLight = new THREE.HemisphereLight({'#ffffff' if is_day else '#4a6572'}, {'#2e7d32' if is_day else '#0b1b10'}, {0.9 if is_day else 0.4});
                    scene.add(hemiLight);

                    const dirLight = new THREE.DirectionalLight({'#fff8e1' if is_day else '#c5cae9'}, {1.2 if is_day else 0.6});
                    dirLight.position.set(5, 10, 5);
                    scene.add(dirLight);

                    // --- CELESTIAL (Sun / Moon) ---
                    const celestialGroup = new THREE.Group();
                    if ({'true' if is_day else 'false'}) {{
                        const sunGeo = new THREE.SphereGeometry(1.2, 16, 16);
                        const sunMat = new THREE.MeshBasicMaterial({{ color: 0xffd54f }});
                        const sun = new THREE.Mesh(sunGeo, sunMat);
                        sun.position.set(6, 6, -10);
                        celestialGroup.add(sun);
                    }} else {{
                        const moonGeo = new THREE.SphereGeometry(0.9, 14, 14);
                        const moonMat = new THREE.MeshBasicMaterial({{ color: 0xe0e0e0 }});
                        const moon = new THREE.Mesh(moonGeo, moonMat);
                        moon.position.set(6, 6, -10);
                        celestialGroup.add(moon);

                        // Sparkling stars
                        const starGeo = new THREE.BufferGeometry();
                        const starPositions = [];
                        for (let s = 0; s < 120; s++) {{
                            starPositions.push((Math.random() - 0.5) * 40, Math.random() * 15 + 2, (Math.random() - 0.5) * 20 - 10);
                        }}
                        starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
                        const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 0.12 }});
                        celestialGroup.add(new THREE.Points(starGeo, starMat));
                    }}
                    scene.add(celestialGroup);

                    // --- ROLLING GREEN FIELD TERRAIN ---
                    const fieldGeo = new THREE.PlaneGeometry(28, 20, 24, 16);
                    fieldGeo.rotateX(-Math.PI / 2.3);
                    const pos = fieldGeo.attributes.position;
                    for (let i = 0; i < pos.count; i++) {{
                        const x = pos.getX(i);
                        const y = pos.getY(i);
                        // Gentle undulating agrarian waves
                        pos.setY(i, y + Math.sin(x * 0.35) * 0.45 + Math.cos(pos.getZ(i) * 0.25) * 0.3);
                    }}
                    fieldGeo.computeVertexNormals();

                    const fieldMat = new THREE.MeshLambertMaterial({{
                        color: {'0x2e7d32' if is_day else '0x15381c'},
                        wireframe: false,
                        flatShading: true,
                    }});
                    const terrain = new THREE.Mesh(fieldGeo, fieldMat);
                    terrain.position.set(0, -0.6, 0);
                    scene.add(terrain);

                    // --- PROCEDURAL CLOUDS ---
                    const cloudGroup = new THREE.Group();
                    if ({'true' if is_cloudy else 'false'}) {{
                        const cloudMat = new THREE.MeshLambertMaterial({{ color: 0xffffff, transparent: true, opacity: 0.85 }});
                        for (let c = 0; c < 4; c++) {{
                            const singleCloud = new THREE.Group();
                            for (let p = 0; p < 4; p++) {{
                                const puff = new THREE.Mesh(new THREE.SphereGeometry(0.5 + Math.random() * 0.3, 8, 8), cloudMat);
                                puff.position.set(p * 0.45, Math.sin(p) * 0.15, 0);
                                singleCloud.add(puff);
                            }}
                            singleCloud.position.set(-8 + c * 5, 4.5 + (c % 2) * 0.8, -4 - c * 2);
                            cloudGroup.add(singleCloud);
                        }}
                    }}
                    scene.add(cloudGroup);

                    // --- RAIN PARTICLES ---
                    let rainGeo, rainSystem;
                    if ({'true' if is_raining else 'false'}) {{
                        const rainCount = 180;
                        const rainPos = [];
                        for (let r = 0; r < rainCount; r++) {{
                            rainPos.push((Math.random() - 0.5) * 20, Math.random() * 10, (Math.random() - 0.5) * 12);
                        }}
                        rainGeo = new THREE.BufferGeometry();
                        rainGeo.setAttribute('position', new THREE.Float32BufferAttribute(rainPos, 3));
                        const rainMat = new THREE.PointsMaterial({{ color: 0x4fc3f7, size: 0.08, transparent: true, opacity: 0.7 }});
                        rainSystem = new THREE.Points(rainGeo, rainMat);
                        scene.add(rainSystem);
                    }}

                    // --- PROCEDURAL CROPS ROW ---
                    const cropsGroup = new THREE.Group();
                    const cropType = "{crop_type}";
                    const stemMat = new THREE.MeshLambertMaterial({{ color: 0x33691e }});
                    const headMat = new THREE.MeshLambertMaterial({{
                        color: cropType === 'wheat' ? 0xf9a825 : (cropType === 'cotton' ? 0xffffff : 0x8bc34a)
                    }});

                    const stalkGeo = new THREE.CylinderGeometry(0.03, 0.04, 0.8, 5);
                    const headGeo = cropType === 'wheat'
                        ? new THREE.ConeGeometry(0.08, 0.35, 5)
                        : (cropType === 'cotton' ? new THREE.SphereGeometry(0.12, 6, 6) : new THREE.CylinderGeometry(0.06, 0.06, 0.3, 5));

                    const cropMeshes = [];
                    for (let row = 0; row < 3; row++) {{
                        for (let col = -5; col <= 5; col++) {{
                            const plant = new THREE.Group();
                            const stem = new THREE.Mesh(stalkGeo, stemMat);
                            stem.position.y = 0.4;
                            plant.add(stem);

                            const head = new THREE.Mesh(headGeo, headMat);
                            head.position.y = 0.85;
                            plant.add(head);

                            plant.position.set(col * 1.2 + (row % 2) * 0.4, -0.1 + row * 0.1, -row * 1.8);
                            cropsGroup.add(plant);
                            cropMeshes.push(plant);
                        }}
                    }}
                    scene.add(cropsGroup);

                    // --- LOW-POLY TRACTOR ---
                    const tractorGroup = new THREE.Group();
                    const bodyMat = new THREE.MeshLambertMaterial({{ color: 0xc62828 }});
                    const tireMat = new THREE.MeshLambertMaterial({{ color: 0x212121 }});
                    const rimMat = new THREE.MeshLambertMaterial({{ color: 0xfbc02d }});

                    const tBody = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.5, 1.2), bodyMat);
                    tBody.position.y = 0.45;
                    tractorGroup.add(tBody);

                    const cabin = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.5, 0.6), new THREE.MeshLambertMaterial({{ color: 0xffffff, transparent: true, opacity: 0.8 }}));
                    cabin.position.set(0, 0.8, -0.2);
                    tractorGroup.add(cabin);

                    // Wheels
                    const rearTireGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.25, 10);
                    rearTireGeo.rotateZ(Math.PI / 2);
                    const rW1 = new THREE.Mesh(rearTireGeo, tireMat);
                    rW1.position.set(0.5, 0.35, -0.3);
                    tractorGroup.add(rW1);
                    const rW2 = rW1.clone();
                    rW2.position.x = -0.5;
                    tractorGroup.add(rW2);

                    const frontTireGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.18, 10);
                    frontTireGeo.rotateZ(Math.PI / 2);
                    const fW1 = new THREE.Mesh(frontTireGeo, tireMat);
                    fW1.position.set(0.45, 0.22, 0.45);
                    tractorGroup.add(fW1);
                    const fW2 = fW1.clone();
                    fW2.position.x = -0.45;
                    tractorGroup.add(fW2);

                    tractorGroup.position.set(3.8, -0.2, -1.5);
                    tractorGroup.rotation.y = -0.35;
                    scene.add(tractorGroup);

                    // --- INTERACTIVITY: PARALLAX & ROTATION ---
                    let isDragging = false;
                    let prevX = 0;
                    let targetRotY = 0;

                    container.addEventListener('mousedown', (e) => {{ isDragging = true; prevX = e.clientX; }});
                    window.addEventListener('mouseup', () => {{ isDragging = false; }});
                    window.addEventListener('mousemove', (e) => {{
                        if (isDragging) {{
                            const dx = e.clientX - prevX;
                            targetRotY += dx * 0.005;
                            prevX = e.clientX;
                        }}
                    }});

                    container.addEventListener('touchstart', (e) => {{
                        if (e.touches.length === 1) {{ isDragging = true; prevX = e.touches[0].clientX; }}
                    }}, {{ passive: true }});
                    window.addEventListener('touchend', () => {{ isDragging = false; }});
                    window.addEventListener('touchmove', (e) => {{
                        if (isDragging && e.touches.length === 1) {{
                            const dx = e.touches[0].clientX - prevX;
                            targetRotY += dx * 0.008;
                            prevX = e.touches[0].clientX;
                        }}
                    }}, {{ passive: true }});

                    // Gyroscope tilt support on mobile
                    if (window.DeviceOrientationEvent) {{
                        window.addEventListener('deviceorientation', (e) => {{
                            if (e.gamma !== null) {{
                                targetRotY = (e.gamma / 90) * 0.35;
                            }}
                        }}, true);
                    }}

                    // --- 30-45 FPS CAPPED ANIMATION LOOP ---
                    let lastTime = 0;
                    let isPageVisible = true;
                    document.addEventListener('visibilitychange', () => {{
                        isPageVisible = !document.hidden;
                    }});

                    function animate(t) {{
                        requestAnimationFrame(animate);
                        if (!isPageVisible) return;

                        const delta = t - lastTime;
                        if (delta < 25) return; // Cap at ~40 FPS
                        lastTime = t;

                        const timeSec = t * 0.001;

                        // Camera easing to target rotation
                        camera.position.x += (Math.sin(targetRotY) * 6 - camera.position.x) * 0.05;
                        camera.lookAt(0, 1.2, 0);

                        // Gentle swaying crops
                        for (let i = 0; i < cropMeshes.length; i++) {{
                            cropMeshes[i].rotation.z = Math.sin(timeSec * 2.2 + cropMeshes[i].position.x) * 0.07;
                        }}

                        // Drifting clouds
                        for (let c = 0; c < cloudGroup.children.length; c++) {{
                            const cl = cloudGroup.children[c];
                            cl.position.x += 0.006;
                            if (cl.position.x > 12) cl.position.x = -12;
                        }}

                        // Falling rain
                        if (rainSystem && rainGeo) {{
                            const p = rainGeo.attributes.position.array;
                            for (let r = 1; r < p.length; r += 3) {{
                                p[r] -= 0.28;
                                if (p[r] < -0.5) p[r] = 8.5;
                            }}
                            rainGeo.attributes.position.needsUpdate = true;
                        }}

                        renderer.render(scene, camera);
                    }}
                    requestAnimationFrame(animate);

                    window.addEventListener('resize', () => {{
                        if (container.clientWidth > 0 && container.clientHeight > 0) {{
                            camera.aspect = container.clientWidth / container.clientHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize(container.clientWidth, container.clientHeight);
                        }}
                    }});
                }} catch (e) {{
                    container.style.display = 'none';
                    fallback.style.display = 'block';
                }}
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)


def render_hero_3d_plant(
    crop_name: str = "Cotton",
    growth_stage: str = "Flowering",
    height: int = 240,
    lang: str = "mr",
):
    """Render an interactive, slowly rotating 3D plant model with automatic low-end device fallback."""
    crop_low = (crop_name or "").lower()

    if any(k in crop_low for k in ["cotton", "kapas", "कापूस", "कपास"]):
        crop_type = "cotton"
        badge_text = "⚪ कापूस (Cotton)" if lang == "mr" else ("⚪ कपास (Cotton)" if lang == "hi" else "⚪ Cotton")
        stem_color = "#558b2f"
    elif any(k in crop_low for k in ["wheat", "gehu", "गहू", "गेहूं"]):
        crop_type = "wheat"
        badge_text = "🌾 गहू (Wheat)" if lang == "mr" else ("🌾 गेहूं (Wheat)" if lang == "hi" else "🌾 Wheat")
        stem_color = "#c0ca33"
    elif any(k in crop_low for k in ["onion", "kanda", "कांदा", "प्याज"]):
        crop_type = "onion"
        badge_text = "🧅 कांदा (Onion)" if lang == "mr" else ("🧅 प्याज (Onion)" if lang == "hi" else "🧅 Onion")
        stem_color = "#43a047"
    else:
        crop_type = "soybean"
        badge_text = "🌱 सोयाबीन (Soybean)" if lang == "mr" else ("🌱 सोयाबीन (Soybean)" if lang == "hi" else "🌱 Soybean")
        stem_color = "#33691e"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: radial-gradient(circle at 50% 25%, #ffffff 0%, #f4fbf5 55%, #e6f5eb 100%);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                border-radius: 22px;
                border: 1.5px solid rgba(183, 223, 195, 0.85);
                box-sizing: border-box;
                height: {height}px;
                display: flex;
                position: relative;
                box-shadow: 0 10px 26px -6px rgba(15, 56, 34, 0.09), inset 0 1px 0 rgba(255, 255, 255, 0.95);
            }}
            #canvas-container {{
                width: 100%;
                height: 100%;
                cursor: grab;
            }}
            #canvas-container:active {{
                cursor: grabbing;
            }}
            .badge-overlay {{
                position: absolute;
                top: 12px;
                left: 14px;
                background: rgba(255, 255, 255, 0.92);
                backdrop-filter: blur(8px);
                border: 1px solid #b7dfc3;
                color: #0f3822;
                padding: 5px 14px;
                border-radius: 18px;
                font-size: 13px;
                font-weight: 800;
                box-shadow: 0 4px 10px rgba(15, 56, 34, 0.06);
                pointer-events: none;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .stage-overlay {{
                position: absolute;
                bottom: 12px;
                right: 14px;
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                color: #ffffff;
                padding: 5px 12px;
                border-radius: 14px;
                font-size: 12px;
                font-weight: 800;
                box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
                pointer-events: none;
            }}
            .hint-overlay {{
                position: absolute;
                bottom: 12px;
                left: 14px;
                color: #4b5563;
                font-size: 11px;
                font-weight: 600;
                background: rgba(255, 255, 255, 0.8);
                padding: 3px 8px;
                border-radius: 10px;
                pointer-events: none;
            }}
            #fallback {{
                display: none;
                width: 100%;
                height: 100%;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                background: #f0fdf4;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container"></div>
        <div class="badge-overlay">{badge_text}</div>
        <div class="stage-overlay">🌿 {growth_stage}</div>
        <div class="hint-overlay">👆 फिरवा (Drag to rotate)</div>
        <div id="fallback">
            <div style="font-size: 3.5rem;">🌱</div>
            <div style="font-weight: 800; color: #166534; margin-top: 8px;">{badge_text}</div>
            <div style="font-size: 0.9rem; color: #4b5563;">{growth_stage}</div>
        </div>

        <script>
            (function() {{
                const container = document.getElementById('canvas-container');
                const fallback = document.getElementById('fallback');
                try {{
                    if (!window.WebGLRenderingContext) throw new Error("No WebGL");
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
                    camera.position.set(0, 1.2, 3.8);

                    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true, powerPreference: "low-power" }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    container.appendChild(renderer.domElement);

                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
                    scene.add(ambientLight);
                    const dirLight = new THREE.DirectionalLight(0xfff8e1, 0.8);
                    dirLight.position.set(3, 5, 4);
                    scene.add(dirLight);

                    const potGeo = new THREE.CylinderGeometry(0.7, 0.5, 0.6, 16);
                    const potMat = new THREE.MeshLambertMaterial({{ color: 0x8d6e63 }});
                    const pot = new THREE.Mesh(potGeo, potMat);
                    pot.position.y = -0.55;
                    scene.add(pot);

                    const plantGroup = new THREE.Group();
                    scene.add(plantGroup);

                    const cropType = "{crop_type}";
                    const stemCurve = new THREE.CatmullRomCurve3([
                        new THREE.Vector3(0, -0.3, 0),
                        new THREE.Vector3(0.06, 0.4, 0.03),
                        new THREE.Vector3(-0.04, 0.9, -0.02),
                        new THREE.Vector3(0.02, 1.4, 0)
                    ]);
                    const stemGeo = new THREE.TubeGeometry(stemCurve, 20, 0.04, 8, false);
                    const stemMat = new THREE.MeshLambertMaterial({{ color: "{stem_color}" }});
                    const stemMesh = new THREE.Mesh(stemGeo, stemMat);
                    plantGroup.add(stemMesh);

                    const leafMat = new THREE.MeshLambertMaterial({{ color: 0x4caf50, side: THREE.DoubleSide }});
                    function createLeaf(x, y, z, rx, ry, rz, scale) {{
                        const leafShape = new THREE.Shape();
                        leafShape.moveTo(0, 0);
                        leafShape.quadraticCurveTo(0.2, 0.25, 0, 0.6);
                        leafShape.quadraticCurveTo(-0.2, 0.25, 0, 0);
                        const leafGeo = new THREE.ShapeGeometry(leafShape);
                        const leaf = new THREE.Mesh(leafGeo, leafMat);
                        leaf.position.set(x, y, z);
                        leaf.rotation.set(rx, ry, rz);
                        leaf.scale.set(scale, scale, scale);
                        plantGroup.add(leaf);
                    }}
                    createLeaf(0, -0.1, 0, 0.4, 0.8, -0.3, 0.9);
                    createLeaf(0, 0.2, 0, 0.3, -1.2, 0.4, 1.0);
                    createLeaf(0, 0.6, 0, -0.4, 1.5, -0.2, 0.8);

                    if (cropType === 'cotton') {{
                        const bollMat = new THREE.MeshLambertMaterial({{ color: 0xffffff }});
                        function addCottonBoll(x, y, z) {{
                            const bg = new THREE.Group();
                            for (let i = 0; i < 4; i++) {{
                                const puff = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 10), bollMat);
                                puff.position.set(Math.cos(i * 1.57) * 0.07, Math.sin(i * 1.57) * 0.07, 0);
                                bg.add(puff);
                            }}
                            bg.position.set(x, y, z);
                            plantGroup.add(bg);
                        }}
                        addCottonBoll(0.12, 0.85, 0.08);
                        addCottonBoll(-0.15, 0.45, 0.1);
                        addCottonBoll(0.05, 1.15, 0);
                    }} else if (cropType === 'wheat') {{
                        const wheatMat = new THREE.MeshLambertMaterial({{ color: 0xf9a825 }});
                        for (let k = 0; k < 12; k++) {{
                            const grain = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.2, 6), wheatMat);
                            grain.position.set((k % 2 === 0 ? 0.06 : -0.06), 0.7 + k * 0.07, 0);
                            grain.rotation.z = (k % 2 === 0 ? 0.4 : -0.4);
                            plantGroup.add(grain);
                        }}
                    }} else {{
                        const podMat = new THREE.MeshLambertMaterial({{ color: 0x8bc34a }});
                        for (let p = 0; p < 5; p++) {{
                            const pod = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.25, 8), podMat);
                            pod.position.set((p % 2 === 0 ? 0.14 : -0.14), 0.1 + p * 0.2, 0.05);
                            pod.rotation.z = (p % 2 === 0 ? 0.6 : -0.6);
                            plantGroup.add(pod);
                        }}
                    }}

                    let isDragging = false;
                    let prevX = 0;
                    container.addEventListener('mousedown', (e) => {{ isDragging = true; prevX = e.clientX; }});
                    window.addEventListener('mouseup', () => {{ isDragging = false; }});
                    window.addEventListener('mousemove', (e) => {{
                        if (isDragging) {{
                            const delta = e.clientX - prevX;
                            plantGroup.rotation.y += delta * 0.012;
                            prevX = e.clientX;
                        }}
                    }});

                    container.addEventListener('touchstart', (e) => {{
                        if (e.touches.length === 1) {{ isDragging = true; prevX = e.touches[0].clientX; }}
                    }}, {{ passive: true }});
                    window.addEventListener('touchend', () => {{ isDragging = false; }});
                    window.addEventListener('touchmove', (e) => {{
                        if (isDragging && e.touches.length === 1) {{
                            const delta = e.touches[0].clientX - prevX;
                            plantGroup.rotation.y += delta * 0.015;
                            prevX = e.touches[0].clientX;
                        }}
                    }}, {{ passive: true }});

                    let lastTime = 0;
                    let isVisible = true;
                    document.addEventListener('visibilitychange', () => {{ isVisible = !document.hidden; }});

                    function animate(t) {{
                        requestAnimationFrame(animate);
                        if (!isVisible) return;
                        if (t - lastTime < 25) return; // ~40 FPS cap
                        lastTime = t;
                        if (!isDragging) {{ plantGroup.rotation.y += 0.008; }}
                        renderer.render(scene, camera);
                    }}
                    requestAnimationFrame(animate);

                    window.addEventListener('resize', () => {{
                        if (container.clientWidth > 0 && container.clientHeight > 0) {{
                            camera.aspect = container.clientWidth / container.clientHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize(container.clientWidth, container.clientHeight);
                        }}
                    }});
                }} catch (err) {{
                    container.style.display = 'none';
                    fallback.style.display = 'flex';
                }}
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)
