from PIL import Image
from rich.text import Text
import os

# Paleta de cores "Sunset" do OpenClaude
SUNSET_GRADIENT = [
    (255, 180, 100),
    (240, 140, 80),
    (217, 119, 87),
    (193, 95, 60),
    (160, 75, 55),
    (130, 60, 50),
]

def lerp_rgb(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def get_gradient_color(stops, t):
    t = max(0, min(1, t))
    s = t * (len(stops) - 1)
    i = int(s)
    if i >= len(stops) - 1:
        return stops[-1]

    fraction = s - i
    return lerp_rgb(stops[i], stops[i + 1], fraction)

def render_logo_to_text(path: str, width: int = 80, alpha_threshold: int = 30, use_gradient: bool = True) -> Text:
    """
    Converte uma imagem para caracteres half-block do Rich.
    Se use_gradient=True, aplica o gradiente estilo OpenClaude.
    """
    if not os.path.exists(path):
        return Text("Mark2TeX", style="bold #03656b")

    try:
        img = Image.open(path).convert("RGBA")
        aspect = img.height / img.width
        h = int(width * aspect * 0.5)
        img = img.resize((width, h * 2), Image.LANCZOS)

        out = Text()
        for y in range(0, h * 2, 2):
            # t_line para o gradiente vertical
            t_line = y / (h * 2 if h * 2 > 0 else 1)

            for x in range(width):
                r1, g1, b1, a1 = img.getpixel((x, y))
                if y + 1 < img.height:
                    r2, g2, b2, a2 = img.getpixel((x, y + 1))
                else:
                    r2, g2, b2, a2 = r1, g1, b1, a1

                top_ok = a1 >= alpha_threshold
                bot_ok = a2 >= alpha_threshold

                if not top_ok and not bot_ok:
                    out.append(" ")
                    continue

                # Determinar cores
                if use_gradient:
                    # t combina posição vertical e horizontal para um efeito dinâmico
                    t_char = t_line * 0.5 + (x / (width if width > 0 else 1)) * 0.5
                    color_top = get_gradient_color(SUNSET_GRADIENT, t_char)
                    # Leve deslocamento para a cor de baixo para dar profundidade
                    color_bot = get_gradient_color(SUNSET_GRADIENT, t_char + 0.05)

                    c1 = f"rgb({color_top[0]},{color_top[1]},{color_top[2]})"
                    c2 = f"rgb({color_bot[0]},{color_bot[1]},{color_bot[2]})"
                else:
                    c1 = f"rgb({r1},{g1},{b1})"
                    c2 = f"rgb({r2},{g2},{b2})"

                if not top_ok:
                    out.append("▄", style=c2)
                elif not bot_ok:
                    out.append("▀", style=c1)
                else:
                    out.append("▀", style=f"{c1} on {c2}")
            out.append("\n")
        return out
    except Exception as e:
        return Text(f"Erro ao carregar logo: {e}", style="red")
