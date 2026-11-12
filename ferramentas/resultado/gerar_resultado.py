"""Gera o Reel "Resultado do jogo" da RonaMagic, versão 3 (12/11/2026).

Uso: python3 gerar_resultado.py dados.json pasta-de-saida

Versão 3 (pedido do Rod, 12/11/2026): 5 quadros, ~20 s, abre pelo placar, narração
com a voz clonada do Rod sincronizada com os quadros, selo de voz por IA.

dados.json: ver exemplo-utah.json ao lado. Campos novos em relação à v2:
- "narracao": caminho do mp3/wav da narração (opcional; sem ele o vídeo sai mudo, 20 s).
- "narracao_texto": lista de 5 frases, uma por quadro, na ordem (a mesma usada na voz,
  sem IPA). Serve para achar onde cortar cada quadro.
- "cortes": opcional, 4 instantes em segundos para forçar os cortes (sobrepõe a detecção).
"fotos" precisa de 5 entradas. "fotos_dir" aponta para material-oficial/fotos deste repositório.

Saída: quadro-1..5.jpg, quadros.jpg (folha de contato), cortes.txt e resultado.mp4.
Só fotos do material oficial de parceiro; o crédito "Foto: Orlando Magic" vai em todo quadro com foto.
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
BLUE, WHITE, SILVER = (0, 119, 192), (255, 255, 255), (210, 218, 224)
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DUR_MUDO = [3, 4, 4, 4, 5]
CAUDA = 0.7


def f(p, s):
    return ImageFont.truetype(p, s)


def fundo(fotos_dir, nome, foco, selo):
    im = Image.new("RGB", (W, H), (11, 15, 25))
    if nome:
        foto = ImageOps.exif_transpose(Image.open(os.path.join(fotos_dir, nome))).convert("RGB")
        foto = ImageOps.fit(foto, (W, H), Image.LANCZOS, centering=(foco, 0.5))
        im = Image.blend(foto, Image.new("RGB", (W, H), (8, 12, 22)), 0.55)
        painel = Image.new("L", (W, H), 0)
        ImageDraw.Draw(painel).rounded_rectangle([50, 420, W - 50, 1580], 36, fill=190)
        im = Image.composite(Image.new("RGB", (W, H), (6, 9, 18)), im, painel)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=BLUE)
    d.text((60, 70), "RONAMAGIC", font=f(B, 40), fill=WHITE)
    d.text((60, 125), "Resultado do jogo", font=f(R, 30), fill=SILVER)
    if nome:
        d.text((W - 60, H - 70), "Foto: Orlando Magic", font=f(R, 28), fill=SILVER, anchor="ra")
    if selo:
        d.text((60, H - 70), "Voz de Rod gerada por IA", font=f(R, 28), fill=SILVER)
    return im, d


def c(d, y, txt, font, fill=WHITE):
    d.text((W // 2, y), txt, font=font, fill=fill, anchor="mm")


def quadros(dados, selo):
    fd, fotos = dados["fotos_dir"], dados["fotos"]
    q = []

    im, d = fundo(fd, *fotos[0], selo)
    c(d, 700, dados["titulo1"], f(B, 120)); c(d, 840, dados["titulo2"], f(B, 104), BLUE)
    c(d, 1060, dados["placar"], f(B, 84)); c(d, 1180, dados["data"], f(R, 44), SILVER)
    q.append(im)

    im, d = fundo(fd, *fotos[1], selo)
    c(d, 700, "QUEM DECIDIU", f(B, 64), BLUE); c(d, 840, dados["destaque"], f(B, 104))
    for i, t in enumerate(dados["destaque_linhas"]):
        c(d, 980 + i * 80, t, f(R, 56), SILVER)
    for i, t in enumerate(dados.get("destaque_extra", [])):
        c(d, 1230 + i * 80, t, f(B, 64))
    q.append(im)

    im, d = fundo(fd, *fotos[2], selo)
    c(d, 680, "COMO O JOGO VIROU", f(B, 64), BLUE)
    y = 840
    for t in dados["virada"]:
        c(d, y, t, f(B, 58)); y += 95
    q.append(im)

    im, d = fundo(fd, *fotos[3], selo)
    c(d, 520, "CLASSIFICAÇÃO DO LESTE", f(B, 64), BLUE)
    y = 680
    for pos, t, r in dados["top3"]:
        d.text((140, y), pos, font=f(B, 58), fill=SILVER); d.text((270, y), t, font=f(B, 58), fill=WHITE)
        d.text((W - 140, y), r, font=f(B, 58), fill=WHITE, anchor="ra"); y += 120
    if dados.get("top3_nota"):
        c(d, y - 25, dados["top3_nota"], f(R, 30), SILVER)
    y += 60
    c(d, y + 20, "· · ·", f(B, 58), SILVER); y += 130
    pos, t, r = dados["magic"]
    d.rounded_rectangle([90, y - 25, W - 90, y + 95], 18, fill=BLUE)
    d.text((140, y), pos, font=f(B, 58), fill=WHITE); d.text((270, y), t, font=f(B, 58), fill=WHITE)
    d.text((W - 140, y), r, font=f(B, 58), fill=WHITE, anchor="ra")
    if dados.get("magic_nota"):
        c(d, y + 170, dados["magic_nota"], f(R, 32), SILVER)
    c(d, y + 230, dados["fonte_classificacao"], f(R, 28), SILVER)
    q.append(im)

    im, d = fundo(fd, *fotos[4], selo)
    c(d, 560, "PRÓXIMO JOGO EM ORLANDO", f(B, 58), BLUE)
    c(d, 690, dados["proximo"], f(B, 92)); c(d, 810, dados["proximo_data"], f(R, 52), SILVER)
    c(d, 890, dados["proximo_hora"], f(R, 52), SILVER)
    if dados.get("preco"):
        c(d, 1030, dados["preco"], f(B, 62))
    c(d, 1190, "WhatsApp +1 (407) 409-6253", f(B, 56), BLUE)
    for i, t in enumerate(["RonaMagic é um serviço da Ronatrip,", "parceira de turismo e Authorized Ticket Seller", "do Orlando Magic"]):
        c(d, 1320 + i * 52, t, f(R, 34), SILVER)
    q.append(im)
    return q


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
    textos = dados["narracao_texto"]
    tam = [len(t) for t in textos]
    alvo, soma = [], 0
    for t in tam[:-1]:
        soma += t
        alvo.append(total_audio * soma / sum(tam))
    meios = silencios(dados["narracao"])
    cortes, ultimo = [], 0.0
    for a in alvo:
        cand = [m for m in meios if m > ultimo + 1.0 and abs(m - a) < 2.5]
        corte = min(cand, key=lambda m: abs(m - a)) if cand else a
        cortes.append(corte); ultimo = corte
    return cortes


def gerar(dados, out):
    os.makedirs(out, exist_ok=True)
    narr = dados.get("narracao")
    q = quadros(dados, bool(narr))
    for i, im in enumerate(q, 1):
        im.save(os.path.join(out, f"quadro-{i}.jpg"), quality=92)
    folha = Image.new("RGB", (5 * 360 + 6 * 20, 680), (30, 34, 44))
    for i, im in enumerate(q):
        folha.paste(im.resize((360, 640)), (20 + i * 380, 20))
    folha.save(os.path.join(out, "quadros.jpg"), quality=90)

    if narr:
        audio = duracao_audio(narr)
        cortes = calcular_cortes(dados, audio)
        total = audio + CAUDA
        marcas = [0.0] + cortes + [total]
        dur = [round(b - a, 3) for a, b in zip(marcas, marcas[1:])]
    else:
        dur, total, cortes = DUR_MUDO, float(sum(DUR_MUDO)), []
    with open(os.path.join(out, "cortes.txt"), "w") as fh:
        fh.write(f"cortes={cortes}\nduracoes={dur}\ntotal={total:.2f}\n")

    lista = os.path.join(out, "lista.txt")
    with open(lista, "w") as fh:
        for i, s in enumerate(dur, 1):
            fh.write(f"file 'quadro-{i}.jpg'\nduration {s}\n")
        fh.write(f"file 'quadro-{len(dur)}.jpg'\n")
    entrada_audio = ["-i", narr] if narr else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    filtro_audio = ["-af", "apad"] if narr else []
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                    *entrada_audio, *filtro_audio,
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-t", f"{total:.2f}", "-movflags", "+faststart",
                    os.path.join(out, "resultado.mp4")], check=True)


if __name__ == "__main__":
    gerar(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
