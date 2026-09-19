import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import html as html_lib
import os
import zipfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from docx.text.paragraph import Paragraph
from jinja2 import Template


# Footnote entries with these types are Word's internal separator lines, not real notes.
SKIPPED_FOOTNOTE_TYPES = {"separator", "continuationSeparator", "continuationNotice"}


class DocxToHtmlConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DOCX to HTML Converter")
        self.root.geometry("700x750")

        # Variables
        self.input_path = tk.StringVar()
        self.template_path = tk.StringVar(value="template.html")
        self.post_number = tk.StringVar()
        self.image_width = tk.StringVar(value="554")
        self.image_height = tk.StringVar(value="335")
        self.art_credit = tk.StringVar()
        self.art_credit_link = tk.StringVar()

        # Music recommendation (optional)
        self.music_title = tk.StringVar()
        self.music_musician = tk.StringVar()

        # Footnote bookkeeping, reset on every conversion
        self.footnote_texts = {}      # docx footnote id -> html text
        self.footnote_order = []      # docx footnote ids, in order of first reference

        self.create_widgets()

    def create_widgets(self):
        # Input File
        tk.Label(self.root, text="Input DOCX File:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.input_path, width=50).grid(
            row=0, column=1, padx=10, pady=5
        )
        tk.Button(self.root, text="Browse", command=self.browse_input).grid(
            row=0, column=2, padx=10, pady=5
        )

        # Template File
        tk.Label(self.root, text="Template HTML File:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.template_path, width=50).grid(
            row=1, column=1, padx=10, pady=5
        )
        tk.Button(self.root, text="Browse", command=self.browse_template).grid(
            row=1, column=2, padx=10, pady=5
        )

        # Post Number
        tk.Label(self.root, text="Post Number:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.post_number, width=20).grid(
            row=2, column=1, sticky="w", padx=10, pady=5
        )
        tk.Label(self.root, text="(Output: ../posts/[number].html, Image: ../img/img-[number].jpg, Audio: ../audio/[number].mp3)",
                 font=("Arial", 8), fg="gray").grid(
            row=3, column=0, columnspan=3, sticky="w", padx=10
        )

        # Separator
        tk.Frame(self.root, height=2, bg="gray").grid(
            row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=10
        )

        # Music Recommendation (Optional)
        tk.Label(self.root, text="Music Recommendation (Optional)",
                 font=("Arial", 10, "bold")).grid(
            row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5)
        )

        tk.Label(self.root, text="Song Title:", font=("Arial", 10)).grid(
            row=7, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.music_title, width=50).grid(
            row=7, column=1, padx=10, pady=5
        )

        tk.Label(self.root, text="Musician:", font=("Arial", 10)).grid(
            row=8, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.music_musician, width=50).grid(
            row=8, column=1, padx=10, pady=5
        )

        # Separator
        tk.Frame(self.root, height=2, bg="gray").grid(
            row=9, column=0, columnspan=3, sticky="ew", padx=10, pady=10
        )

        # Image settings
        tk.Label(self.root, text="Image Width:", font=("Arial", 10)).grid(
            row=10, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.image_width, width=20).grid(
            row=10, column=1, sticky="w", padx=10, pady=5
        )

        tk.Label(self.root, text="Image Height:", font=("Arial", 10)).grid(
            row=11, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.image_height, width=20).grid(
            row=11, column=1, sticky="w", padx=10, pady=5
        )

        tk.Label(self.root, text="Art Credit", font=("Arial", 10)).grid(
            row=12, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.art_credit, width=20).grid(
            row=12, column=1, sticky="w", padx=10, pady=5
        )

        tk.Label(self.root, text="Art Credit Link", font=("Arial", 10)).grid(
            row=13, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.art_credit_link, width=20).grid(
            row=13, column=1, sticky="w", padx=10, pady=5
        )

        # Convert Button
        tk.Button(
            self.root, text="Convert", command=self.convert,
            bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
            width=20, height=2
        ).grid(row=14, column=0, columnspan=3, pady=20)

        # Log/Status Area
        tk.Label(self.root, text="Status Log:", font=("Arial", 10, "bold")).grid(
            row=15, column=0, sticky="w", padx=10, pady=5
        )
        self.log_text = scrolledtext.ScrolledText(
            self.root, height=10, width=80, state="disabled"
        )
        self.log_text.grid(row=16, column=0, columnspan=3, padx=10, pady=5)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Input DOCX File",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            self.log(f"Input file selected: {filename}")

    def browse_template(self):
        filename = filedialog.askopenfilename(
            title="Select Template HTML File",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )
        if filename:
            self.template_path.set(filename)
            self.log(f"Template file selected: {filename}")

    def browse_output(self):
        # No longer needed - removed
        pass

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    # ------------------------------------------------------------------
    # Run / paragraph formatting
    # ------------------------------------------------------------------

    def _run_flag(self, run, name):
        """True/False for bold or italic, falling back to the run's character style.

        run.bold is None when the run inherits the property from its style
        (e.g. a word marked with Word's built-in "Emphasis" style), so a plain
        `if run.bold` misses those.
        """
        value = getattr(run, name)
        if value is None:
            try:
                value = getattr(run.style.font, name)
            except Exception:
                value = None
        return bool(value)

    def run_to_html(self, run, suppress_bold=False):
        text = run.text
        if not text:
            return ""
        # Escape first so stray &, < or > in the document don't break the page.
        text = html_lib.escape(text)
        if self._run_flag(run, "italic"):
            text = f"<em>{text}</em>"
        if self._run_flag(run, "bold") and not suppress_bold:
            text = f"<strong>{text}</strong>"
        return text

    def _get_alignment(self, para):
        """'center', 'right', or None - checked on the paragraph, then its
        style and base styles, since alignment is often set via style rather
        than direct formatting."""
        alignment = para.paragraph_format.alignment
        style = para.style
        depth = 0
        while alignment is None and style is not None and depth < 10:
            try:
                alignment = style.paragraph_format.alignment
                style = style.base_style
            except Exception:
                break
            depth += 1
        if alignment == WD_ALIGN_PARAGRAPH.CENTER:
            return "center"
        if alignment == WD_ALIGN_PARAGRAPH.RIGHT:
            return "right"
        return None

    def _is_all_bold(self, para):
        """True when every run with visible text in this paragraph is bold.

        Used to treat a fully-bolded paragraph as a section title/subtitle.
        A paragraph with only some bold words (emphasis inside a normal
        sentence) is left as inline <strong> instead.
        """
        runs = [r for r in para.runs if r.text and r.text.strip()]
        if not runs:
            return False
        return all(self._run_flag(r, "bold") for r in runs)

    def paragraph_to_html(self, para, collect_footnotes=True, suppress_bold=False):
        """Convert one paragraph's runs to HTML, inserting footnote markers."""
        parts = []
        for run in para.runs:
            parts.append(self.run_to_html(run, suppress_bold=suppress_bold))
            if not collect_footnotes:
                continue
            for ref in run._element.findall(qn('w:footnoteReference')):
                marker = self._footnote_marker(ref.get(qn('w:id')))
                if marker:
                    parts.append(marker)
        return "".join(parts)

    # ------------------------------------------------------------------
    # Footnotes
    # ------------------------------------------------------------------

    def load_footnotes(self, docx_path, doc):
        """Read word/footnotes.xml. python-docx has no footnote API, so go to the ZIP."""
        self.footnote_texts = {}
        self.footnote_order = []

        with zipfile.ZipFile(docx_path) as archive:
            if 'word/footnotes.xml' not in archive.namelist():
                return
            xml_bytes = archive.read('word/footnotes.xml')

        # parse_xml (not lxml directly) so w:p elements get python-docx's
        # own element classes and Paragraph can wrap them.
        root = parse_xml(xml_bytes)
        for footnote in root.findall(qn('w:footnote')):
            if footnote.get(qn('w:type')) in SKIPPED_FOOTNOTE_TYPES:
                continue
            note_id = footnote.get(qn('w:id'))
            lines = []
            for p_element in footnote.findall(qn('w:p')):
                # Wrap the raw element so the same run formatting code applies.
                # doc.part as parent keeps run.style resolvable.
                para = Paragraph(p_element, doc.part)
                line = self.paragraph_to_html(para, collect_footnotes=False).strip()
                if line:
                    lines.append(line)
            self.footnote_texts[note_id] = "<br>".join(lines)

    def _footnote_marker(self, note_id):
        """Superscript marker, numbered by order of appearance in the document."""
        if note_id is None or note_id not in self.footnote_texts:
            return ""
        if note_id not in self.footnote_order:
            self.footnote_order.append(note_id)
        number = self.footnote_order.index(note_id) + 1
        return (f'<sup class="footnote-ref" id="fnref-{number}">'
                f'<a href="#fn-{number}">{number}</a></sup>')

    def build_footnotes_html(self, inline_safe=False):
        """The footnote list for the end of the article.

        inline_safe=True returns a version built only from <span>s, which is
        valid HTML even when it ends up inside the template's <p>{{ content }}</p>.
        The default returns proper <hr>/<ol> markup for a {{ footnotes }} slot.
        """
        if not self.footnote_order:
            return ""

        items = []
        for number, note_id in enumerate(self.footnote_order, start=1):
            text = self.footnote_texts.get(note_id, "")
            back = (f'<a href="#fnref-{number}" class="footnote-back" '
                    f'title="Back to text">&#8617;</a>')
            if inline_safe:
                items.append(
                    f'  <span class="footnote" id="fn-{number}" style="display:block;">'
                    f'<sup>{number}</sup> {text} {back}</span>'
                )
            else:
                items.append(f'    <li id="fn-{number}">{text} {back}</li>')

        if inline_safe:
            return (
                '<span class="footnotes" style="display:block;margin-top:2em;'
                'padding-top:1em;border-top:1px solid #ccc;font-size:0.85em;">\n'
                + "\n".join(items) + '\n</span>'
            )
        return (
            '<hr class="footnotes-sep">\n'
            '<section class="footnotes">\n'
            '  <ol>\n' + "\n".join(items) + '\n  </ol>\n'
            '</section>'
        )

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def convert(self):
        # Validate inputs
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input DOCX file")
            return
        if not self.template_path.get():
            messagebox.showerror("Error", "Please select a template HTML file")
            return
        if not self.post_number.get():
            messagebox.showerror("Error", "Please enter a post number")
            return

        # Construct output paths
        post_num = self.post_number.get()
        output_path = f"../posts/{post_num}.html"
        image_path = f"../img/img-{post_num}.jpg"
        audio_path = f"../audio/{post_num}.mp3"

        try:
            self.log("\n--- Starting Conversion ---")
            self.log(f"Post number: {post_num}")
            self.log(f"Output will be saved to: {output_path}")
            self.log(f"Image path will be: {image_path}")

            # Extract from DOCX
            self.log("Reading DOCX file...")
            doc = Document(self.input_path.get())

            # Footnotes must be loaded before the body is walked
            self.load_footnotes(self.input_path.get(), doc)
            if self.footnote_texts:
                self.log(f"Found {len(self.footnote_texts)} footnote(s) in the document")

            # Get title (first paragraph)
            title = doc.paragraphs[0].text if doc.paragraphs else "Untitled"
            self.log(f"Title extracted: {title}")

            # Get main content
            self.log("Extracting content...")
            blocks = []        # finished chunks of HTML, joined with <br><br>
            buffer = []        # consecutive normal paragraphs
            paragraph_count = 0
            centered_count = 0
            right_count = 0
            heading_count = 0

            def flush_buffer():
                if buffer:
                    blocks.append("<br><br>".join(buffer))
                    buffer.clear()

            for para in doc.paragraphs[1:]:
                alignment = self._get_alignment(para)   # 'center' / 'right' / None
                is_heading = self._is_all_bold(para)     # fully-bold paragraph = section title

                # A fully-bold paragraph with no explicit alignment of its own
                # defaults to centered, since that's how a section title/subtitle
                # normally reads. An explicit right/center alignment on a bold
                # paragraph is still respected as the author set it.
                if is_heading and alignment is None:
                    alignment = "center"

                # Headings get their bold from the CSS class instead of an
                # inline <strong> per run, so multiple runs don't produce
                # redundant nested tags.
                para_html = self.paragraph_to_html(para, suppress_bold=is_heading)
                if not para_html.strip():  # Only add non-empty paragraphs
                    continue
                paragraph_count += 1

                if is_heading or alignment:
                    flush_buffer()
                    classes = []
                    styles = ["display:block"]
                    if alignment == "center":
                        classes.append("centered")
                        styles.append("text-align:center")
                        centered_count += 1
                    elif alignment == "right":
                        classes.append("right-aligned")
                        styles.append("text-align:right")
                        right_count += 1
                    if is_heading:
                        classes.append("section-title")
                        # Inline fallback in case the template's CSS hasn't
                        # been updated with a .section-title rule yet.
                        styles.append("font-weight:bold")
                        heading_count += 1
                    class_attr = " ".join(classes)
                    style_attr = ";".join(styles)
                    blocks.append(
                        f'<span class="{class_attr}" style="{style_attr};">{para_html}</span>'
                    )
                else:
                    buffer.append(para_html)
            flush_buffer()

            content = "<br><br>".join(blocks)
            self.log(
                f"Extracted {paragraph_count} paragraphs "
                f"({centered_count} centered, {right_count} right-aligned, {heading_count} section titles)"
            )

            footnotes_html = self.build_footnotes_html()
            if self.footnote_order:
                self.log(f"Rendered {len(self.footnote_order)} referenced footnote(s)")
            unused = len(self.footnote_texts) - len(self.footnote_order)
            if unused > 0:
                self.log(f"Note: {unused} footnote(s) in the file were never referenced and were skipped")

            # Load template
            self.log("Loading template...")
            with open(self.template_path.get(), 'r', encoding='utf-8') as f:
                template_source = f.read()
            template = Template(template_source)

            # If the template doesn't place {{ footnotes }} itself, append the
            # footnote section to the end of the content instead.
            if footnotes_html and "footnotes" not in template_source:
                content = f"{content}\n{self.build_footnotes_html(inline_safe=True)}"
                self.log("Template has no {{ footnotes }} slot - appended footnotes to the end of the content")

            # Render template
            self.log("Rendering HTML...")

            # Check if music recommendation is provided
            has_music = bool(self.music_title.get() and self.music_musician.get())

            html_output = template.render(
                title=title,
                content=content,
                footnotes=footnotes_html,
                has_footnotes=bool(footnotes_html),
                image_path=image_path,
                image_width=self.image_width.get(),
                image_height=self.image_height.get(),
                has_music=has_music,
                music_path=audio_path if has_music else None,
                music_title=self.music_title.get() if has_music else None,
                music_musician=self.music_musician.get() if has_music else None,
                art_credit=self.art_credit.get(),
                art_credit_link=self.art_credit_link.get(),
                docx_path=os.path.relpath(self.input_path.get())
            )

            # Create output directory if it doesn't exist
            os.makedirs("../posts", exist_ok=True)

            # Save output
            self.log("Saving output file...")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

            self.log(f"✓ Conversion complete! File saved to: {output_path}")
            messagebox.showinfo("Success", f"Conversion completed successfully!\n\nOutput: {output_path}\nImage path: {image_path}")

        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DocxToHtmlConverter(root)
    root.mainloop()