# Overall goal is to create a PDF from single sided scans of a double sided document

import pathlib
import os

FN1 = "interleave1.tif"
FN2 = "interleave2.tif"
OUT_DIR = "Output"
PDF_W = 210
PDF_H = 297


def count_pages(fn: str) -> int:
    import PIL.Image

    """Count the pages in a TIF"""
    im = PIL.Image.open(fn)
    pages = 0
    while pages < 100:
        try:
            im.seek(pages)
            pages += 1
        except EOFError:
            break
    im.close()
    return pages


def tif_to_jpegs(tif_filename: str, out_filename: str, reverse_count: bool = False, count_by_two: bool = False):
    """
    Convert a TIF file into a bunch of jpegs.
    :param tif_filename: Input TIF file name
    :param out_filename: Path and file name prefix. eg out_filename="p/n" will yield "p/n00.jpeg"
    :param reverse_count: If true, images will come out with reversed index count, so last image will have index 0
    :param count_by_two: If true, image index will increment by 2 (or decrement by 2 if reverse_count is used)
    :return:
    """
    import PIL.Image

    # first, create a folder of JPEGs of the pages, correctly ordered
    # Make sure the output dir is set
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)

    # Load in the first set, which has pages 1, 3, 5, etc
    f_len = count_pages(tif_filename)
    f_im = PIL.Image.open(tif_filename)
    inc = 1
    if count_by_two:
        inc = 2
    index = 0
    if reverse_count:
        index = f_len * inc - (inc-1)
        inc = -inc
    for counter in range(f_len):
        f_im.seek(counter)
        f_im.save(f"{out_filename}{index:02d}.jpeg")
        print(f"pg{index}")
        index += inc
    f_im.close()


def make_interleaved_pdf():
    # first, create a folder of JPEGs of the pages, correctly ordered
    # Make sure the output dir is set
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    filename = f"{OUT_DIR}\\Taxes"
    tif_to_jpegs(FN1, filename, count_by_two=True)
    tif_to_jpegs(FN2, filename, count_by_two=True, reverse_count=True)
    jpegs_to_pdf(filename)


def jpegs_to_pdf(jpeg_prefix: str, output_filename: str = ""):
    import fpdf
    pdf = fpdf.FPDF()
    # remove the margins
    pdf.set_margins(0, 0, 0)
    pdf.set_auto_page_break(0)
    search_string = jpeg_prefix
    if not pathlib.os.path.splitext(search_string)[1]:
        search_string += "*.jpeg"
    files = pathlib.Path('').glob(search_string)
    for file in files:
        pdf.add_page()
        pdf.image(f"{file}", w=PDF_W, h=PDF_H)
    if not output_filename:
        output_filename = jpeg_prefix + ".pdf"
    pdf.output(output_filename, "F")


def merge_pdfs(target_path: str, outfile: str = "output.pdf"):
    import PyPDF2

    path = pathlib.Path(target_path)
    merger = PyPDF2.PdfFileMerger()
    for file in path.glob("*.pdf"):
        merger.append(PyPDF2.PdfFileReader(f"{file}"), import_bookmarks=False)
    merger.write(outfile)


def tif_to_pdf(filename: str):
    fn_prefix = filename.split(".")[0]
    out_filename = f"{OUT_DIR}\\{fn_prefix}"
    tif_to_jpegs(filename, out_filename)
    jpegs_to_pdf(out_filename)


tifs = ["tif1.tif"]
for fn in tifs:
    tif_to_pdf(fn)
