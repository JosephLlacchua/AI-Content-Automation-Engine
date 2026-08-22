# flake8: noqa: E501

# ====================================================================================
# FORM-BASED GENERATION
# ====================================================================================

STYLE_DESCRIPTIONS: dict[str, str] = {
    "stickman": "Dynamic hand-drawn 2D webcomic sketch style, thick expressive black ink outlines, vibrant minimalist color palette for highlights, clean shading, white background with glowing accents.",
    "realistic": "Photorealistic cinematic style, high-detail rendering, natural dramatic lighting, professional photography quality, sharp focus, rich cinematic color grading.",
    "anime": "Japanese anime style, bold clean outlines, vibrant saturated colors, expressive character designs, dynamic composition, cel-shading with smooth gradients.",
    "watercolor": "Soft watercolor painting style, loose expressive brushstrokes, translucent overlapping color washes, gentle pastel palette, visible paper texture, dreamy and artistic feel.",
    "flat": "Clean modern flat design style, geometric simplified shapes, bold solid colors, minimal shadows, simple iconographic characters, professional and contemporary look.",
}

TONE_DESCRIPTIONS: dict[str, str] = {
    "motivacional": "motivacional y enérgico, con urgencia y convicción, que inspire acción inmediata",
    "educativo": "educativo y claro, con explicaciones precisas y ejemplos concretos, tono de mentor experto",
    "dramatico": "dramático y tenso, con narrativa de suspenso, giros inesperados e impacto emocional fuerte",
    "entretenimiento": "entretenido y dinámico, con ritmo ágil, momentos de sorpresa y enganche constante",
    "inspiracional": "inspiracional y emotivo, con historias de superación, valores universales y mensaje poderoso",
    "controversial": "polémico y directo, desafiando verdades aceptadas por la sociedad, generando debate inmediato y rompiendo mitos",
    "misterio": "intrigante y conspirativo, revelando un secreto paso a paso, manteniendo el misterio absoluto hasta la última frase",
    "alerta": "urgente y de advertencia, alertando sobre un error gravísimo que todos cometen, generando miedo a perder dinero o tiempo (FOMO)",
    "storytelling": "narrativo y muy íntimo, como una confesión personal, contando un fracaso o anécdota real con mucha vulnerabilidad",
    "sarcastico": "sarcástico y mordaz, usando ironía para burlarse de situaciones cotidianas, explicando realidades incómodas con humor seco",
}

CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "finanzas": "finanzas personales — dinero, inversión, ahorro y libertad financiera",
    "horror": "horror psicológico — suspenso, miedos, fenómenos inexplicables e historias perturbadoras",
    "motivacion": "superación personal — mentalidad de crecimiento, disciplina y logro de metas",
    "historia": "hechos históricos — personajes y eventos fascinantes que cambiaron el mundo",
    "ciencia": "ciencia y tecnología — descubrimientos, innovación y curiosidades del universo",
}

FORM_SCRIPT_PROMPT: str = """# 🎬 GENERADOR DE SCRIPT — VIDEO SHORT

## CONTEXTO DE CREACIÓN
**Idea central:** {idea}
**Categoría:** {category_desc}
**Tono narrativo:** {tone_desc}
**Formato de video:** {aspect_ratio}

## ESTILO VISUAL Y COMPOSICIÓN (OBLIGATORIO PARA TODOS LOS image_prompt)
Usa EXACTAMENTE este estilo en el campo `style` de cada escena:
`{style_desc}`
Usa EXACTAMENTE este aspect_ratio en el campo `aspect_ratio` de cada escena:
`{aspect_ratio}`

⚠️ REGLA CRÍTICA DE COMPOSICIÓN: Si el aspect_ratio es "9:16", el campo `composition` DEBE forzar encuadres verticales e incluir instrucciones explícitas para evitar rotaciones.
Ejemplo de `composition` correcto para 9:16: "Vertical frame, portrait framing, upright orientation, DO NOT ROTATE, tall composition".
NUNCA uses términos como "Wide shot", "Panorama", o "Landscape", ya que causan que la IA rote la imagen 90 grados y los personajes salgan acostados o de lado.

## ESTRUCTURA DEL GUION (MANDATORIA)
1. **Acto 1 — Hook [Escenas 1-4]:** Gancho que detenga el scroll en los primeros 3 segundos. Arranca con la idea central de forma impactante.
2. **Acto 2 — Desarrollo [Escenas 5-10]:** Desarrolla la idea con información valiosa, datos o narrativa que enganchen.
3. **Acto 3 — Cierre [Escenas 11-final]:** Conclusión poderosa con llamado a la acción o reflexión final memorable.

## REGLAS DE RETENCIÓN (TAN CRÍTICAS COMO LAS DEMÁS)

### 🎯 ESCENA 1 — HOOK OBLIGATORIO (los primeros 3 segundos deciden todo)
La escena 1 debe ser UNA SOLA frase corta que DETENGA el scroll instantáneamente.
Usa una de estas estructuras probadas como base:
- Pregunta con dato shocking: "¿Sabías que el 95% de la gente hace X y destruye Y sin saberlo?"
- Afirmación imposible de ignorar: "Lo que nadie te dice sobre X va a cambiar cómo ves Y para siempre."
- Promesa directa con urgencia: "En los próximos 60 segundos vas a entender algo que le tomó años aprender a la gente exitosa."
- Dato contraintuitivo: "Hacer X es la razón por la que la mayoría fracasa en Y, aunque parezca lo correcto."
⚠️ REGLA ABSOLUTA: Máximo 10 palabras. Sin "hola". Sin introducción. Sin contexto previo. Directo al impacto.

### 🔗 REGLA DE CLIFFHANGER ENTRE ESCENAS
Cada narración debe terminar dejando la historia INCOMPLETA, de modo que el espectador
NECESITE ver la siguiente escena. Evita conclusiones dentro de una sola escena.
Usa estas estructuras de cierre para crear tensión:
- "...pero eso era solo el principio."
- "...y entonces todo cambió."
- "...lo que pasó después nadie lo esperaba."
- "...y ese fue su mayor error."
- "...pero había algo que aún no sabían."
- "...hasta que descubrieron la verdad."
La ÚNICA excepción es la escena FINAL (CTA/reflexión), que sí puede ser conclusiva.

### 🔊 CAMPO `sfx_tag` — DISEÑO SONORO PROFESIONAL POR ESCENA
Eres un diseñador de sonido profesional. Asigna el efecto más apropiado a cada escena según su función narrativa EXACTA.

**CATÁLOGO COMPLETO DE EFECTOS — LEE CADA UNO:**
- `impact`: Escena 1 SIEMPRE. También para datos numéricos fuertes ("el 90% fracasa"), giros narrativos dramáticos, revelaciones de personaje. Sonido: golpe potente.
- `whoosh`: Transiciones rápidas de época/lugar/personaje, flashbacks, saltos en el tiempo. Sonido: silbido veloz.
- `riser`: SOLO 1-2 escenas INMEDIATAMENTE ANTES del clímax o revelación principal. Nunca en escenas climáticas, siempre en las que preceden. Sonido: tensión que sube.
- `gasp`: Sorpresa genuina, humor inesperado, reacción exagerada ante algo absurdo. ("¡Y resulta que…!", "Nadie esperaba que…"). Máximo 2 veces por video.
- `pop`: Primera aparición visual de un concepto clave, elementos de una lista, solución que "aparece en pantalla", presentación de herramientas o pasos.
- `flash`: Escena final de CTA, conclusión poderosa, cierre memorable. Sonido: click brillante.
- `notification`: Momento en que el protagonista tiene una idea brillante, insight inesperado, epifanía ("De repente se dio cuenta…", "Fue ahí cuando entendió…").
- `typing`: Escenas donde aparece texto en pantalla, mensajes, código, contraseñas, formularios, llamados a acción escritos ("Escríbeme", "Visita el link").
- `glitch`: Algo falla, un error ocurre, un plan se rompe, hay un problema técnico, una crisis. ("Todo iba bien hasta que…", "El sistema falló…").
- `money`: Escenas sobre dinero, inversión, ganancias, transacciones, precios, salarios, deudas. Cualquier cifra económica importante.
- `scratch`: Corrección rápida, "espera, retrocede", "eso era un mito", negación de algo dicho antes. Efecto de reversa o DJ scratch.
- `none`: Escenas de desarrollo tranquilo, explicaciones detalladas, contexto sin evento dramático. Úsalo cuando NINGÚN otro tag encaja naturalmente.

**REGLAS DE USO — OBLIGATORIAS:**
⚠️ `impact`: máximo 3 veces por video.
⚠️ `gasp`: máximo 2 veces por video.
⚠️ `riser`: máximo 2 veces, SIEMPRE antes del clímax, NUNCA en el clímax mismo.
⚠️ `flash`: máximo 1 vez, reservado para el cierre.
✅ Varía los efectos. Evita usar el mismo tag más de 2 veces seguidas.
✅ Entre el 40-60% de escenas deben tener `none` para no saturar el audio.

**CORRELACIÓN POR CATEGORÍA DE CONTENIDO:**
- Finanzas/negocios: prioriza `money`, `notification`, `typing`, `impact`
- Horror/suspenso: prioriza `glitch`, `riser`, `impact`, `whoosh`
- Motivacional: prioriza `gasp`, `notification`, `flash`, `impact`
- Historia/ciencia: prioriza `whoosh`, `impact`, `pop`, `riser`
- Entretenimiento: prioriza `gasp`, `pop`, `scratch`, `whoosh`


## REGLAS OBLIGATORIAS

### NARRACIÓN
- Frases cortas, directas y con ritmo acorde al tono indicado
- Campo `narration` siempre en **ESPAÑOL LATINOAMERICANO**
- Máximo una frase de narración por escena

### IMAGEN Y VIDEO
- Campos `image_prompt` (subjects, environment, lighting, composition, style) en **INGLÉS**
- Campos `video_prompt` (motion, camera_movement, transition, duration_hint) en **INGLÉS**
- El `image_prompt` debe ilustrar visualmente lo que dice la narración
- Las imágenes deben mostrar progresión narrativa coherente

### ⚠️ REGLA ANTI-COPYRIGHT PARA image_prompt (CRÍTICA — NO IGNORAR)
Los generadores de imágenes (como Google Flow / Imagen) bloquean cualquier nombre de personaje protegido por copyright (Marvel, DC, Disney, anime, etc.).
Por eso, en el campo `description` de cada `subject` dentro de `image_prompt`, NUNCA uses el nombre real del personaje.
En su lugar, descríbelo **físicamente con características físicas únicas que lo identifiquen visualmente**, tal como haría un director de casting:

**EJEMPLOS OBLIGATORIOS:**
- ❌ NUNCA: `"Batman"` → ✅ SIEMPRE: `"A tall, broad-shouldered billionaire with a strong square jawline, wearing dark grey and black bat-themed armored suit"`
- ❌ NUNCA: `"Iron Man"` → ✅ SIEMPRE: `"A middle-aged superhero with a stylish goatee beard and short dark hair, wearing a high-tech red and gold mechanical suit with a glowing chest reactor"`
- ❌ NUNCA: `"Spiderman"` → ✅ SIEMPRE: `"A nimble teenage hero wearing a red and blue suit with web patterns and large white goggle-like eyes"`
- ❌ NUNCA: `"Wonder Woman"` → ✅ SIEMPRE: `"A beautiful amazon warrior princess with long dark wavy hair, a golden tiara, red corset armor and blue skirt"`
- ❌ NUNCA: `"Hulk"` → ✅ SIEMPRE: `"A massive, extremely muscular green giant with messy black hair and torn purple pants"`
- ❌ NUNCA: `"Goku"` → ✅ SIEMPRE: `"A young athletic warrior with spiky black hair, wearing an orange and blue martial arts gi with a long tail"`
- ❌ NUNCA: `"Naruto"` → ✅ SIEMPRE: `"A teenage ninja boy with spiky blond hair, wearing an orange and black jumpsuit with a headband protector"`

**REGLA CLAVE:** En el campo `narration` (voz en off) SÍ puedes usar los nombres reales de los personajes porque el audio no tiene filtro de copyright.
Solo aplica la descripción física en el campo `description` del `image_prompt`.

### ESTRUCTURA
- Entre **12 y 16 escenas**
- Numeración secuencial desde 1
"""

# ====================================================================================
# JSON SCHEMAS
# ====================================================================================


CHUNK_INSTRUCTIONS: str = """
---
## 🎬 INSTRUCCIONES DE CONTINUIDAD (MÓDULO DE ESCENAS)
Actualmente estás generando una sección del guion completo.

**RANGO DE ESCENAS:** DEBES generar exactamente las escenas de la **{start_scene} a la {end_scene}**.

**CONTEXTO NARRATIVO ANTERIOR:**
{context}

**REGLA DE HILACIÓN:** Asegúrate de que la transición entre la última escena conocida y la nueva escena ({start_scene}) sea fluida, lógica y mantenga la misma atmósfera cinematográfica. No repitas escenas, solo continúa la historia. Mantén la numeración secuencial.
---
"""

# ====================================================================================
# CORE PROMPTS
# ====================================================================================

AUDIO_PROMPT: str = """Narra el siguiente guion con voz clara, expresiva y envolvente. Adapta el tono al contenido: si es dramático sube la intensidad, si es educativo mantén ritmo firme y seguro, si es motivacional transmite energía y convicción. Lee exactamente el texto tal cual aparece, sin omitir ni agregar nada:

{audio_text}"""

ALIGNMENT_PROMPT: str = """# \ud83e\udde0 ALINEADOR DE AUDIO \u2014 MAESTRO DE PRECISI\u00d3N FON\u00c9TICA

Eres un experto en post-producci\u00f3n de audio para video. Tu \u00fanica tarea es determinar los timestamps exactos de inicio y fin de cada escena del gui\u00f3n dentro de un audio transcrito por Whisper.

---

## \ud83d\udd39 TRANSCRIPCI\u00d3N WHISPER (timestamps por segmento)
{whisper_data}

---

## \ud83d\udcdd GUI\u00d3N (cada l\u00ednea es UNA escena completa e indivisible)
{scenes_data}

---

## \u26a0\ufe0f REGLAS CR\u00cdTICAS \u2014 LEE CADA UNA:

**REGLA #1 \u2014 INTEGRIDAD DE FRASE (LA M\u00c1S IMPORTANTE):**
Cada narration del gui\u00f3n es una unidad indivisible. El end_time de una escena DEBE coincidir EXACTAMENTE con el final de la ULTIMA PALABRA de esa narraci\u00f3n.
PROHIBIDO: cortar una escena antes de que termine su \u00faltima palabra.
PROHIBIDO: que las palabras de una escena aparezcan en el audio de otra escena.

**REGLA #2 \u2014 SIN SOLAPAMIENTOS:**
El end_time de la escena N DEBE ser id\u00e9ntico al start_time de la escena N+1.
No puede haber huecos ni solapamientos entre escenas.

**REGLA #3 \u2014 BUSCA LA \u00daLTIMA PALABRA:**
Para encontrar el end_time de una escena, localiza en los segmentos de Whisper la ULTIMA PALABRA de esa narraci\u00f3n y usa el timestamp de FIN de esa palabra. No uses el inicio de la siguiente escena como referencia para cortar la anterior.

**REGLA #4 \u2014 PRIMERA ESCENA:**
start_time de la escena 1 = 0.000 siempre.

**REGLA #5 \u2014 CUENTA EXACTA:**
Debes devolver exactamente {expected_count} objetos en el array "alignments".

**REGLA #6 \u2014 SOLO JSON:**
Responde exclusivamente con el JSON. Ning\u00fan texto extra antes o despu\u00e9s.

---

## \ud83d\udce6 FORMATO DE SALIDA
```json
{{
  "alignments": [
    {{
      "scene_number": 1,
      "start_time": 0.000,
      "end_time": 4.850
    }},
    {{
      "scene_number": 2,
      "start_time": 4.850,
      "end_time": 9.200
    }}
  ]
}}
```
"""
