from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
import textwrap
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORT_MD = os.path.join(BASE, 'REPORT_FASE2.md')
OUT_PDF = os.path.join(BASE, 'REPORT_FASE2.pdf')
IMG_DIR = os.path.join(BASE, 'src', 'images')


def read_markdown_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()


def draw_text_block(c, x, y, text, max_width_mm, leading=12):
    wrapped = textwrap.wrap(text, width=100)
    for line in wrapped:
        c.drawString(x, y, line)
        y -= leading
    return y


def main():
    lines = read_markdown_lines(REPORT_MD)
    c = canvas.Canvas(OUT_PDF, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    x = margin
    y = height - margin

    c.setFont('Helvetica-Bold', 14)
    c.drawString(x, y, 'Relatório Técnico — Tech Challenge Fase 2')
    y -= 12 * mm

    c.setFont('Helvetica', 10)

    # Render markdown in a very simple way: headings and paragraphs
    for line in lines:
        if line.startswith('## '):
            c.setFont('Helvetica-Bold', 12)
            c.drawString(x, y, line.replace('## ', ''))
            y -= 8 * mm
            c.setFont('Helvetica', 10)
        elif line.startswith('### '):
            c.setFont('Helvetica-Bold', 11)
            c.drawString(x, y, line.replace('### ', ''))
            y -= 6 * mm
            c.setFont('Helvetica', 10)
        elif line.startswith('```'):
            # skip code blocks for now
            pass
        elif line.strip().startswith('!['):
            # image inline; extract path between parentheses
            start = line.find('(')
            end = line.find(')', start)
            if start != -1 and end != -1:
                img_path = line[start+1:end]
                img_full = os.path.join(BASE, img_path)
                if os.path.exists(img_full):
                    try:
                        img = ImageReader(img_full)
                        img_w, img_h = img.getSize()
                        max_w = (width - 2*margin)
                        scale = min(max_w / img_w, 150*mm / img_h)
                        draw_w = img_w * scale
                        draw_h = img_h * scale
                        if y - draw_h < margin:
                            c.showPage()
                            y = height - margin
                        c.drawImage(img, x, y - draw_h,
                                    width=draw_w, height=draw_h)
                        y -= draw_h + 6 * mm
                    except Exception as e:
                        c.drawString(x, y, f'[Erro ao inserir imagem: {e}]')
                        y -= 6 * mm
                else:
                    c.drawString(x, y, f'[Imagem não encontrada: {img_full}]')
                    y -= 6 * mm
        else:
            if line.strip() == '':
                y -= 4 * mm
            else:
                wrapped = textwrap.wrap(line, width=120)
                for wline in wrapped:
                    if y < margin:
                        c.showPage()
                        y = height - margin
                        c.setFont('Helvetica', 10)
                    c.drawString(x, y, wline)
                    y -= 5 * mm

    c.save()
    print('PDF gerado em:', OUT_PDF)


if __name__ == '__main__':
    main()
