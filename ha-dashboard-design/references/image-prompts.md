# Image Generation Prompts

Structured prompts for generating background images and mockup visualizations
that match each dashboard style. Use with Midjourney, DALL-E 3, Stable Diffusion,
or Flux.

---

## How to Use

Each prompt below is ready to paste into an image generator. Replace the
`[ROOM]` placeholder with your actual room (e.g., living room, bedroom, kitchen).

For **background images**: use the "Background" prompt → save as `/config/www/backgrounds/`
For **mockup visualization**: use the "Mockup" prompt to visualize how the dashboard looks

---

## Glassmorphism

**Background image:**
```
Dark cinematic interior of a [ROOM], moody atmospheric lighting, deep blue and purple
gradient, bokeh window light, photographic, ultra sharp, 8k resolution,
no text, no UI elements, wide landscape aspect ratio
```

**Dashboard mockup:**
```
Smart home control panel UI, glassmorphism design, frosted glass cards with blur effect,
dark navy gradient background with bokeh lights, semi-transparent white panels with subtle
border glow, floating cards showing temperature 21°C, weather icons, music controls,
purple accent colors #7c6bff, Inter font, modern minimal HUD aesthetic,
professional UI design, 16:9 landscape, ultra detailed
```

---

## Dark Minimal

**Background image:**
```
Pure black seamless texture, very subtle grain, no gradients, perfectly flat,
professional photography backdrop, 8k resolution, no text
```

**Dashboard mockup:**
```
Minimalist smart home dashboard UI, pure black background #000000, razor thin white
border cards, clean typography Inter font, no decorations, sensor readings in large
thin-weight numbers, temperature 21°C humidity 45%, monochrome white-on-black palette,
inspired by Linear app and Vercel dashboard, ultra minimal modern design,
professional UI screenshot, 16:9 landscape
```

---

## Material You

**Background image:**
```
Soft light contemporary living room, natural daylight through large windows,
warm neutral tones, minimal Scandinavian interior, blurred background,
professional interior photography, 8k resolution, no text
```

**Dashboard mockup:**
```
Google Material Design 3 smart home app UI, dynamic color theming deep purple #6750A4,
large rounded corners 28px border-radius, tonal surface cards in soft lavender,
familiar Android aesthetic, temperature widgets, media player, light controls,
"Google Sans" typography, Material You design language, clean and friendly,
professional mobile UI screenshot, 16:9 landscape
```

---

## Nordic

**Background image:**
```
Bright airy Scandinavian living room interior, white walls, natural wood,
minimal furniture, soft morning daylight, hygge atmosphere, IKEA aesthetic,
professional interior photography, wide angle, no people, 8k resolution
```

**Dashboard mockup:**
```
Nordic Scandinavian smart home dashboard UI, pure white cards with very subtle
soft shadow, light grey #f5f5f0 background, blue accent color #4a7c9e,
generous whitespace, thin clean typography Inter font, sensor readings,
weather widget, minimal and airy design language, inspired by IKEA and Muuto,
professional UI screenshot, 16:9 landscape, bright and clean
```

---

## Neon / Cyberpunk

**Background image:**
```
Dark cyberpunk city at night, rain reflections on wet asphalt, neon lights
electric blue and magenta, cinematic wide shot, blade runner aesthetic,
no people in foreground, ultra detailed, 8k resolution, high contrast
```

**Dashboard mockup:**
```
Cyberpunk futuristic smart home control UI, dark near-black background #050508,
vivid neon cyan #00f5ff and magenta #ff00ff accent colors, glowing border effects,
scan lines overlay, Orbitron sci-fi font, neon glow text shadows, animated pulse effects,
temperature displays in glowing numbers, sector labels, HUD aesthetic,
Blade Runner UI inspiration, professional UI screenshot, 16:9 landscape
```

---

## Warm Home

**Background image:**
```
Cozy living room at golden hour, warm candlelight ambiance, terracotta and amber tones,
hygge interior, soft cushions and wooden furniture, fire in fireplace,
bokeh background, professional interior photography, no people, 8k resolution
```

**Dashboard mockup:**
```
Warm cozy smart home dashboard UI, cream #faf7f2 background, terracotta and amber accent
colors #c47a3a, warm gradients from cream to soft gold, Lora serif typography,
rounded 18px corners, subtle warm shadows, temperature widgets, light control sliders,
scene buttons with candle and coffee icons, Mediterranean and Scandinavian hygge aesthetic,
professional UI design, 16:9 landscape
```

---

## Soft Pastel

**Background image:**
```
Bright cheerful children's room or family living room, soft pastel colors,
pink lilac and mint accents, modern friendly interior, natural daylight,
plush toys and books visible, warm and welcoming atmosphere,
professional interior photography, 8k resolution, no text
```

**Dashboard mockup:**
```
Soft pastel smart home app UI, gentle pink #fce4ec and lilac #f3e5f5 gradient cards,
mint green accents #a0c8b0, sky blue highlights, Nunito rounded font,
large rounded corners 22px, playful and friendly aesthetic, temperature sensors,
scene buttons with sun and star icons, subtle soft box shadows,
family-friendly approachable design, professional UI screenshot, 16:9 landscape
```

---

## Luxury Gold

**Background image:**
```
Ultra luxury penthouse interior at night, deep navy and black tones,
gold and brass fixtures, marble surfaces, floor-to-ceiling city views,
dramatic accent lighting, Architectural Digest editorial photography,
no people, 8k resolution, premium aesthetic
```

**Dashboard mockup:**
```
Premium luxury smart home control panel UI, deep navy #0d0f18 background,
gold accent color #c9a84c throughout, Cormorant Garamond elegant serif typography,
sharp 4px corners, subtle gold gradient borders, gold glowing line dividers,
temperature in large elegant numerals, scene buttons labeled in uppercase serif,
opulent sophisticated aesthetic inspired by private aviation and yacht interiors,
professional UI design, 16:9 landscape
```

---

## Retro Terminal

**Background image:**
```
Old CRT computer monitor phosphor green on black, scan lines visible,
1980s mainframe terminal texture, monochrome green glow,
flat background for UI overlay, professional photography, 8k resolution
```

**Dashboard mockup:**
```
1980s retro computer terminal smart home UI, pure black background,
phosphor green #00cc44 text and borders, Share Tech Mono monospace font,
CRT scan line overlay effect, sharp 0px corner radius, glowing green text shadows,
terminal-style labels like TEMP, HUM%, SECTOR_01, command prompt aesthetic,
sensor readings like a mainframe status display, animated blinking cursor,
Fallout terminal UI aesthetic, professional UI screenshot, 16:9 landscape
```

---

## Tips for Best Results

**Midjourney:** Append `--ar 16:9 --v 6 --style raw` to background prompts
**DALL-E 3:** These prompts work as-is. Add "no watermark, no signature" at end
**Stable Diffusion:** Add `masterpiece, best quality` at start; negative: `text, watermark, blurry`
**Flux:** Works best with descriptive prompts - no special parameters needed

**Background sizing for HA:**
- Dashboard: 1920×1080 or 2560×1440
- Save to `/config/www/backgrounds/`
- Reference in dashboard YAML: `background: "center/cover url('/local/backgrounds/your-image.jpg')"`

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
