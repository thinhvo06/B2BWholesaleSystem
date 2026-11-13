import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import shutil

user_uploaded_path = r'C:\Users\PC\.gemini\antigravity\brain\98bbc8b3-ca47-4a64-a148-35d3ae195ce8\.user_uploaded\media_1794541812917_13d66288.docx'
output_scratch = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\Report.docx'
output_brain = r'C:\Users\PC\.gemini\antigravity\brain\98bbc8b3-ca47-4a64-a148-35d3ae195ce8\Report.docx'
sc_dir = r'C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\screenshots'

doc = docx.Document(user_uploaded_path)

# 1. Update GitHub Repo URL in paragraphs and tables
for p in doc.paragraphs:
    if 'https://github.com/[username]' in p.text:
        p.text = p.text.replace('https://github.com/[username]/B2BWholesaleSystem', 'https://github.com/thinhvo06/B2BWholesaleSystem')

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if 'https://github.com/[username]' in cell.text:
                cell.text = cell.text.replace('https://github.com/[username]/B2BWholesaleSystem', 'https://github.com/thinhvo06/B2BWholesaleSystem')

# 2. Add ERD under 3.1 (P12)
p12 = doc.paragraphs[12]
erd_img = os.path.join(sc_dir, 'erd_diagram.png')
if os.path.exists(erd_img):
    r = p12.add_run('\n\nFigure 3.1: Relational Database ERD (Entity Framework Core Fluent API)\n')
    r.bold = True
    r.font.size = Pt(10)
    p12.add_run().add_picture(erd_img, width=Inches(5.8))

# 3. Add Responsive UI (Task 3.4) under 5.5 (P50)
p50 = doc.paragraphs[50]
desk_img = os.path.join(sc_dir, 'responsive_desktop.png')
mob_img = os.path.join(sc_dir, 'responsive_mobile.png')

if os.path.exists(desk_img):
    r = p50.add_run('\n\nFigure 5.6: Desktop View (1280px) - 3-Column Responsive Grid, Header Navigation & Live Cart Badge\n')
    r.bold = True
    r.font.size = Pt(10)
    p50.add_run().add_picture(desk_img, width=Inches(5.8))

if os.path.exists(mob_img):
    r = p50.add_run('\n\nFigure 5.7: Mobile Responsive View (375px) - Collapsed Hamburger Menu, Single-Column Cards & Adaptive Layout\n')
    r.bold = True
    r.font.size = Pt(10)
    p50.add_run().add_picture(mob_img, width=Inches(3.3))

# 4. Add Unit Test Explorer Graphic under Section 6
p53 = doc.paragraphs[53]
test_img = os.path.join(sc_dir, 'unit_test_results.png')
if os.path.exists(test_img):
    r = p53.add_run('\n\nFigure 6.1: Visual Studio Test Explorer - All 6 Core Business Logic Tests Passed (100%)\n')
    r.bold = True
    r.font.size = Pt(10)
    p53.add_run().add_picture(test_img, width=Inches(5.8))

# 5. Add Config Masked Graphic under Section 7
p56 = doc.paragraphs[56]
cfg_img = os.path.join(sc_dir, 'config_masked.png')
if os.path.exists(cfg_img):
    r = p56.add_run('\n\nFigure 7.1: Application Configuration Settings in appsettings.json and App.config\n')
    r.bold = True
    r.font.size = Pt(10)
    p56.add_run().add_picture(cfg_img, width=Inches(5.8))

# 6. Add Git Collaboration Graphic under Section 8
p58 = doc.paragraphs[58]
git_img = os.path.join(sc_dir, 'git_collaboration.png')
if os.path.exists(git_img):
    r = p58.add_run('\n\nFigure 8.1: GitFlow Commit Graph and Pull Request #1 Merge Log\n')
    r.bold = True
    r.font.size = Pt(10)
    p58.add_run().add_picture(git_img, width=Inches(5.8))

# Save
doc.save(output_scratch)
doc.save(output_brain)
print('Successfully merged and saved Report.docx!')
