# The Nativity: A Coloring Story Book

The first story-arc book in this series. Twelve scenes, in order, tell the birth of Jesus for ages about 3–12. The pictures are reverent and gentle: bold outlines, open shapes for crayons, and the same cartoon-realistic line-art look as the other volumes.

Mary, Joseph, and the angel keep the same faces and clothes from page to page. The “no room” page and the manger page share Luke 2:7, and they are different pictures: the couple turned toward a stable, then the baby laid in the manger.

## Print

- Paper: US Letter (8.5×11 in), portrait, **actual size / 100%**.
- Files: `pages/nativity/`, **2550×3300 pixels at 300 dpi**, pure black and white (two levels).
- Books: `pdf/nativity-letter.pdf` is US Letter, 14 pages. `pdf/nativity-a4.pdf` fits each page inside A4 and centers it, with no cropping.
- Footer on every page: `STEWARDOFTHEKING · BSB`.
- PDF title and author: Steward of the King.

Read the Bible line under the picture, then color. Little kids color the big shapes. Older kids can add flowers, stars, wings, and robes.

## Pages

| File | Page |
| --- | --- |
| `pages/nativity/01-cover.png` | Cover — The Nativity: A Coloring Story Book |
| `pages/nativity/02-gabriel-mary.png` | Gabriel appears to Mary |
| `pages/nativity/03-mary-says-yes.png` | Mary says yes |
| `pages/nativity/04-mary-visits-elizabeth.png` | Mary visits Elizabeth |
| `pages/nativity/05-joseph-dream.png` | An angel speaks to Joseph in a dream |
| `pages/nativity/06-caesars-decree.png` | Caesar’s decree |
| `pages/nativity/07-journey-to-bethlehem.png` | The journey to Bethlehem |
| `pages/nativity/08-no-room-at-the-inn.png` | No room at the inn |
| `pages/nativity/09-baby-in-the-manger.png` | Jesus born and laid in a manger |
| `pages/nativity/10-angels-and-shepherds.png` | Angels appear to the shepherds |
| `pages/nativity/11-shepherds-visit.png` | The shepherds visit |
| `pages/nativity/12-shepherds-tell-everyone.png` | The shepherds tell everyone |
| `pages/nativity/13-mary-treasures.png` | Mary treasures these things |
| `pages/nativity/14-parent-note.png` | For parents and Sunday school |

Every scene caption is exact Berean Standard Bible wording, with the reference under the line. The words and the Bible Hub page they were copied from are listed in `CAPTIONS.md`.

## Personal use

Print these for your home, classroom, or Sunday school. Please don’t resell the files or the prints. Stories inspired by the Berean Standard Bible (public domain).

## Rebuild

From the repo root, with Pillow and img2pdf installed:

```bash
python3 nativity/build_pages.py
```

The script reads `nativity/art/`, sets the captions and footer, writes `pages/nativity/*.png`, refreshes `CAPTIONS.md`, and builds both PDFs. If `tesseract` is on the PATH it also checks that each caption band still reads as the verse. Fonts under `nativity/fonts/` are SIL Open Font License; see `fonts/NOTICE.md`.
