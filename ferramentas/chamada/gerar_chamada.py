"""Chamada de jogo em casa da RonaMagic: card de feed (1080x1350) e Story (1080x1920), em JPEG.

Uso (da raiz do clone do ronamagic-midia):
  python3 ferramentas/chamada/gerar_chamada.py dados.json pasta-de-saida

dados.json (ver exemplo-bucks.json):
  "selo_tempo": "AMANHÃ" | "É HOJE" | "SÁBADO" ...   etiqueta âmbar do topo
  "adversario": "Bucks"                                 nome curto, sem logo
  "data": "Sexta, 13 de novembro"
  "hora": "19h (horário de Orlando)"
  "extra": "NBA Cup"                                    opcional
  "preco": "31"                                         só o número, lido no site do dia
  "foto": "kia-center2-high.jpeg", "foco": 0.5          de material-oficial/fotos
  "fotos_dir": "material-oficial/fotos"
Identidade: azul #0B1F4B, âmbar #F5A623, Rona em Caveat Brush, Magic em Sora 800, texto em Inter.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(AQUI, "assets")
AZUL, AMBAR, BRANCO, PRATA = (11, 31, 75), (245, 166, 35), (255, 255, 255), (196, 206, 212)
SORA = os.path.join(A, "Sora-ExtraBold.ttf")
CAVEAT = os.path.join(A, "CaveatBrush.ttf")
IB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
IS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def f(p, s):
    return ImageFont.truetype(p, s)


def bola(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBAR)
    w = max(2, r // 7)
    d.line([cx - r, cy, cx + r, cy], fill=AZUL, width=w)
    d.line([cx, cy - r, cx, cy + r], fill=AZUL, width=w)
    d.arc([cx - r * 1.9, cy - r, cx - r * 0.35, cy + r], -60, 60, fill=AZUL, width=w)
    d.arc([cx + r * 0.35, cy - r, cx + r * 1.9, cy + r], 120, 240, fill=AZUL, width=w)


def logo(d, x, y, esc=1.0):
    fr, fm = f(CAVEAT, int(96 * esc)), f(SORA, int(64 * esc))
    d.text((x, y), "Rona", font=fr, fill=AMBAR, anchor="ls")
    x2 = x + d.textlength("Rona", font=fr) + 22 * esc
    r = int(22 * esc)
    bola(d, int(x2 + r), int(y - 24 * esc), r)
    d.text((x2 + 2 * r + 22 * esc, y), "Magic", font=fm, fill=BRANCO, anchor="ls")


def fundo(dados, W, H):
    foto = ImageOps.exif_transpose(Image.open(os.path.join(dados["fotos_dir"], dados["foto"]))).convert("RGB")
    foto = ImageOps.fit(foto, (W, H), Image.LANCZOS, centering=(dados.get("foco", 0.5), 0.5))
    im = Image.blend(foto, Image.new("RGB", (W, H), AZUL), 0.62)
    grad = Image.new("L", (1, H))
    for yy in range(H):
        grad.putpixel((0, yy), int(235 * max(0, (yy - H * 0.35) / (H * 0.65))))
    im = Image.composite(Image.new("RGB", (W, H), AZUL), im, grad.resize((W, H)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=AMBAR)
    d.text((W - 80, 52), "Foto: Orlando Magic", font=f(IR, 24), fill=PRATA, anchor="ra")
    return im, d


def etiqueta(d, x, y, txt):
    fe = f(IB, 38)
    w = d.textlength(txt, font=fe)
    d.rounded_rectangle([x, y, x + w + 60, y + 64], 32, fill=AMBAR)
    d.text((x + 30, y + 32), txt, font=fe, fill=AZUL, anchor="lm")


def rodape(im, d, W, H):
    d.text((80, H - 92), "WhatsApp +1 (407) 409-6253", font=f(IS, 34), fill=BRANCO, anchor="lm")
    selo = Image.open(os.path.join(A, "selo-authorized.png"))
    im.paste(selo, (W - 80 - selo.width, H - 92 - selo.height // 2))


def corpo(d, dados, W, y, grande, n_itens=2):
    s = 1.0 if not grande else 1.12
    etiqueta(d, 80, y, f'{dados["selo_tempo"]} · {dados["data_curta"]}')
    y += 130
    d.text((80, y), "Magic × " + dados["adversario"], font=f(SORA, int(104 * s)), fill=BRANCO, anchor="lt")
    y += int(130 * s)
    d.text((80, y), "no Kia Center", font=f(SORA, int(72 * s)), fill=AMBAR, anchor="lt")
    y += int(120 * s)
    linha = f'{dados["data"]} · {dados["hora"]}'
    d.text((80, y), linha, font=f(IS, int(36 * s)), fill=BRANCO, anchor="lt")
    if dados.get("extra"):
        y += int(52 * s)
        d.text((80, y), dados["extra"], font=f(IR, int(34 * s)), fill=PRATA, anchor="lt")
    y += int(95 * s)
    d.text((80, y), "a partir de", font=f(IR, int(40 * s)), fill=BRANCO, anchor="lt")
    y += int(48 * s)
    d.text((80, y), f'US$ {dados["preco"]}', font=f(SORA, int(120 * s)), fill=AMBAR, anchor="lt")
    d.text((80 + d.textlength(f'US$ {dados["preco"]}', font=f(SORA, int(120 * s))) + 24, y + int(78 * s)),
           "por ingresso", font=f(IR, int(36 * s)), fill=BRANCO, anchor="lt")
    y += int(175 * s)
    for t in ["Atendimento em português, do pedido ao ingresso", "Todas as áreas, até o Gallagher Club"][:n_itens]:
        d.ellipse([84, y + 12, 100, y + 28], fill=AMBAR)
        d.text((122, y), t, font=f(IR, 32), fill=BRANCO, anchor="lt")
        y += 56
    return y


def caixa(d, W, y, h):
    d.rounded_rectangle([80, y, W - 80, y + h], 28, fill=AMBAR)
    d.text((124, y + h * 0.22), "Peça pelo WhatsApp", font=f(SORA, 50), fill=AZUL, anchor="lt")
    d.text((124, y + h * 0.62), "ou em ronamagic.com · link na bio", font=f(IS, 32), fill=AZUL, anchor="lt")


def feed(dados, out):
    W, H = 1080, 1350
    im, d = fundo(dados, W, H)
    logo(d, 80, 160)
    y = corpo(d, dados, W, 215, False, 1)
    caixa(d, W, y + 20, 150)
    rodape(im, d, W, H)
    im.save(os.path.join(out, "chamada-feed.jpg"), quality=92)
    return im


def story(dados, out):
    W, H = 1080, 1920
    im, d = fundo(dados, W, H)
    logo(d, 80, 300, 1.15)
    y = corpo(d, dados, W, 520, True)
    caixa(d, W, y + 50, 190)
    d.text((W // 2, y + 300), "Toque no link para pedir", font=f(IR, 30), fill=PRATA, anchor="mm")
    rodape(im, d, W, H)
    im.save(os.path.join(out, "chamada-story.jpg"), quality=92)
    return im


if __name__ == "__main__":
    dados = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    a, b = feed(dados, out), story(dados, out)
    folha = Image.new("RGB", (540 + 540 + 60, 960 + 40), (30, 34, 44))
    folha.paste(a.resize((540, 675)), (20, 20)); folha.paste(b.resize((540, 960)), (580, 20))
    folha.save(os.path.join(out, "folha.jpg"), quality=88)
