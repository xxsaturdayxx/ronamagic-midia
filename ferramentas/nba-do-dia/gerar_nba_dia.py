"""Short diário "NBA em 1 minuto" da RonaMagic (1080x1920, ~15-20 s), com a voz do Rod.

Uso (da raiz do clone do ronamagic-midia):
  python3 ferramentas/nba-do-dia/gerar_nba_dia.py dados.json pasta-de-saida

Sem foto nenhuma: o conteúdo fala da liga inteira, e as fotos oficiais do Magic só servem para
promover o Magic. Sem logo de time, sem foto de jogador, sem trecho de transmissão.
Fundo: quadra desenhada em linhas, na identidade da marca.

dados.json (ver exemplo.json): "data", "quadros" (lista de 2 a 4; o último é a chamada final,
gerada sozinha), "narracao" (mp3, opcional), "narracao_texto" (uma frase por quadro, incluindo
a chamada final), "cortes" opcional.
Cada quadro: {"etiqueta": "...", "titulo": ["linha", "linha"], "numero": "41", "numero_legenda": "pontos", "linhas": ["..."]}
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(AQUI, "..", "chamada", "assets")
W, H = 1080, 1920
AZUL, AZUL2, AMBAR, BRANCO, PRATA = (11, 31, 75), (18, 44, 100), (245, 166, 35), (255, 255, 255), (196, 206, 212)
SORA = os.path.join(A, "Sora-ExtraBold.ttf")
CAVEAT = os.path.join(A, "CaveatBrush.ttf")
IB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
IS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
CAUDA = 0.7


def f(p, s):
    return ImageFont.truetype(p, s)


def bola(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBAR)
    w = max(2, r // 7)
    d.line([cx - r, cy, cx + r, cy], fill=AZUL, width=w)
    d.line([cx, cy - r, cx, cy + r], fill=AZUL, width=w)


def logo(d, x, y):
    fr, fm = f(CAVEAT, 92), f(SORA, 60)
    d.text((x, y), "Rona", font=fr, fill=AMBAR, anchor="ls")
    x2 = x + d.textlength("Rona", font=fr) + 20
    bola(d, int(x2 + 20), int(y - 22), 20)
    d.text((x2 + 62, y), "Magic", font=fm, fill=BRANCO, anchor="ls")


def fundo(data, selo):
    im = Image.new("RGB", (W, H), AZUL)
    d = ImageDraw.Draw(im)
    for yy in range(H):
        t = yy / H
        d.line([(0, yy), (W, yy)], fill=tuple(int(AZUL[i] + (AZUL2[i] - AZUL[i]) * (1 - abs(t - 0.5) * 2)) for i in range(3)))
    linha = (34, 62, 125)
    d.ellipse([W // 2 - 230, 1500, W // 2 + 230, 1960], outline=linha, width=6)
    d.rectangle([W // 2 - 250, 1500, W // 2 + 250, 1960], outline=linha, width=6)
    d.arc([-200, 1100, W + 200, 2500], 180, 360, fill=linha, width=6)
    d.line([0, 1500, W, 1500], fill=linha, width=4)
    d.rectangle([0, 0, W, 14], fill=AMBAR)
    logo(d, 80, 170)
    d.rounded_rectangle([80, 220, 80 + 420, 284], 32, fill=AMBAR)
    d.text((110, 252), "NBA EM 1 MINUTO", font=f(IB, 34), fill=AZUL, anchor="lm")
    d.text((W - 80, 252), data, font=f(IS, 34), fill=PRATA, anchor="rm")
    if selo:
        d.text((80, H - 70), "Voz de Rod gerada por IA", font=f(IR, 28), fill=PRATA)
    return im, d


def quadro(q, data, selo):
    im, d = fundo(data, selo)
    y = 520
    if q.get("etiqueta"):
        d.text((80, y), q["etiqueta"].upper(), font=f(IB, 40), fill=AMBAR, anchor="lt"); y += 80
    for t in q.get("titulo", []):
        d.text((80, y), t, font=f(SORA, 76), fill=BRANCO, anchor="lt"); y += 100
    if q.get("numero"):
        y += 40
        fn = f(SORA, 230)
        d.text((80, y), q["numero"], font=fn, fill=AMBAR, anchor="lt")
        if q.get("numero_legenda"):
            d.text((80 + d.textlength(q["numero"], font=fn) + 30, y + 160), q["numero_legenda"], font=f(IS, 48), fill=BRANCO, anchor="lt")
        y += 290
    for t in q.get("linhas", []):
        d.text((80, y), t, font=f(IR, 44), fill=PRATA, anchor="lt"); y += 64
    return im


def final(data, selo):
    im, d = fundo(data, selo)
    d.text((80, 620), "NBA todo dia,", font=f(SORA, 84), fill=BRANCO, anchor="lt")
    d.text((80, 730), "em português.", font=f(SORA, 84), fill=AMBAR, anchor="lt")
    d.rounded_rectangle([80, 900, W - 80, 1080], 28, fill=AMBAR)
    d.text((124, 990), "Siga @ronamagic", font=f(SORA, 64), fill=AZUL, anchor="lm")
    d.text((80, 1160), "Vai a Orlando? Ingressos do Orlando Magic", font=f(IR, 40), fill=PRATA, anchor="lt")
    d.text((80, 1218), "com atendimento em português.", font=f(IR, 40), fill=PRATA, anchor="lt")
    d.text((80, 1300), "WhatsApp +1 (407) 409-6253", font=f(IB, 44), fill=BRANCO, anchor="lt")
    return im


def duracao_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def silencios(p):
    r = subprocess.run(["ffmpeg", "-i", p, "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(a + b) / 2 for a, b in zip(ini, fim)]


def calcular_cortes(dados, total_audio):
    if dados.get("cortes"):
        return [float(x) for x in dados["cortes"]]
    tam = [len(t) for t in dados["narracao_texto"]]
    alvo, soma = [], 0
    for t in tam[:-1]:
        soma += t
        alvo.append(total_audio * soma / sum(tam))
    meios, cortes, ultimo = silencios(dados["narracao"]), [], 0.0
    for a in alvo:
        cand = [m for m in meios if m > ultimo + 1.0 and abs(m - a) < 2.5]
        corte = min(cand, key=lambda m: abs(m - a)) if cand else a
        cortes.append(corte); ultimo = corte
    return cortes


def gerar(dados, out):
    os.makedirs(out, exist_ok=True)
    narr = dados.get("narracao")
    q = [quadro(x, dados["data"], bool(narr)) for x in dados["quadros"]] + [final(dados["data"], bool(narr))]
    for i, im in enumerate(q, 1):
        im.save(os.path.join(out, f"quadro-{i}.jpg"), quality=92)
    n = len(q)
    folha = Image.new("RGB", (n * 360 + (n + 1) * 20, 680), (30, 34, 44))
    for i, im in enumerate(q):
        folha.paste(im.resize((360, 640)), (20 + i * 380, 20))
    folha.save(os.path.join(out, "quadros.jpg"), quality=90)
    if narr:
        total = duracao_audio(narr) + CAUDA
        cortes = calcular_cortes(dados, total - CAUDA)
        marcas = [0.0] + cortes + [total]
        dur = [round(b - a, 3) for a, b in zip(marcas, marcas[1:])]
    else:
        dur = [5] * (n - 1) + [4]; total = float(sum(dur)); cortes = []
    with open(os.path.join(out, "cortes.txt"), "w") as fh:
        fh.write(f"cortes={cortes}\nduracoes={dur}\ntotal={total:.2f}\n")
    lista = os.path.join(out, "lista.txt")
    with open(lista, "w") as fh:
        for i, s in enumerate(dur, 1):
            fh.write(f"file 'quadro-{i}.jpg'\nduration {s}\n")
        fh.write(f"file 'quadro-{n}.jpg'\n")
    entrada = ["-i", narr, "-af", "apad"] if narr else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, *entrada,
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-t", f"{total:.2f}",
                    "-movflags", "+faststart", os.path.join(out, "nba-do-dia.mp4")], check=True)


if __name__ == "__main__":
    gerar(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
