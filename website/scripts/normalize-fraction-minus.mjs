/**
 * Normalizes negative rationals: unary minus before the fraction, not inside the numerator
 * (e.g. \frac{-3}{4} → -\frac{3}{4}). Leaves \frac{-b \pm ...} (quadratic formula) unchanged.
 */
import { readFile, writeFile, readdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, '..', '..')

const chapterFolders = [
  '1 - טכניקה אלגברית',
  '2 - חזקות ושורשים, מידות, המרות וכתיבה מדעית',
  '3 - קריאת והבנת מידע מגרפים מסיפורי מעשה',
  '4 - משוואות ממעלה ראשונה ושנייה, מערכת משוואות',
  '5 - שינוי נושא הנוסחה',
  '6 - מבוא להנדסה',
  '7 - הנדסה אנליטית',
  '8 - הפונקציה הריבועית והפרבולה',
  '9 - שאלות מילוליות',
  '10 - טריגונומטריה',
]

const MARKER = '\uE000FRAC_MINUS_B\uE001'

/** @param {string} s */
function transform(s) {
  // --- Protect quadratic formula numerator (-b ± ...)
  s = s.replace(/\\frac\{-b(\s*\\pm)/g, `${MARKER}$1`)

  // --- -\frac{a}{-b} → \frac{a}{b} (no unary minus on denominator typographically)
  s = s.replace(/-\\frac\{(\d+)\}\{-(\d+)\}/g, '\\frac{$1}{$2}')

  // --- -\frac{-n}{...} → \frac{n}{...} (vertex formula algebra steps)
  s = s.replace(/-\\frac\{-(\d+)\}\{/g, '\\frac{$1}{')

  // --- \frac{-Aa}{-Bb} → \frac{Aa}{Bb}
  s = s.replace(
    /\\frac\{-(\d+)([a-zA-Z][^}]*)\}\{-(\d+)([a-zA-Z][^}]*)\}/g,
    '\\frac{$1$2}{$3$4}',
  )

  // --- \frac{-Aa}{...} → -\frac{Aa}{...} (algebraic monomial numerator)
  s = s.replace(/\\frac\{-(\d+)([a-zA-Z][^}]*)\}\{/g, '-\\frac{$1$2}{')

  // --- Pure numeric \frac{-n}{-m}
  s = s.replace(/\\frac\{-(\d+)\}\{-(\d+)\}/g, '\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+\.\d+)\}\{-(\d+)\}/g, '\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+)\}\{-(\d+\.\d+)\}/g, '\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+\.\d+)\}\{-(\d+\.\d+)\}/g, '\\frac{$1}{$2}')

  // --- Known multi-part expressions (must run before pure-numeric single-\frac rules)
  const specials = [
    [
      '\\frac{-8 \\pm \\sqrt{20}}{-2} = \\frac{-8 \\pm 2\\sqrt{5}}{-2}',
      '\\frac{8 \\mp \\sqrt{20}}{2} = \\frac{8 \\mp 2\\sqrt{5}}{2}',
    ],
    ['\\frac{-8 \\pm \\sqrt{20}}{-2}', '\\frac{8 \\mp \\sqrt{20}}{2}'],
    ['\\frac{-6 \\pm \\sqrt{20}}{-2}', '\\frac{6 \\mp \\sqrt{20}}{2}'],
    ['\\frac{-11 \\pm 5}{-2}', '\\frac{11 \\mp 5}{2}'],
    ['\\frac{-8\\pm\\sqrt{28}}{-2}', '\\frac{8\\mp\\sqrt{28}}{2}'],
    ['\\frac{-5}{2 \\cdot (-\\frac{1}{2})}', '-\\frac{5}{2 \\cdot (-\\frac{1}{2})}'],
    [
      'x=\\frac{-5\\pm\\sqrt{25+732}}{6}=\\frac{-5+\\sqrt{757}}{6}',
      'x=-\\frac{5\\mp\\sqrt{25+732}}{6}=-\\frac{5-\\sqrt{757}}{6}',
    ],
    ['a=\\frac{-1+\\sqrt{1+696}}{4}', 'a=-\\frac{1-\\sqrt{1+696}}{4}'],
    [
      'w=\\frac{-3+\\sqrt{9+352}}{2}=\\frac{-3+19}{2}',
      'w=-\\frac{3-\\sqrt{9+352}}{2}=\\frac{16}{2}',
    ],
    [
      'x = \\frac{-9 + \\sqrt{81 + 656}}{2} = \\frac{-9 + \\sqrt{737}}{2}',
      'x = -\\frac{9 - \\sqrt{81 + 656}}{2} = -\\frac{9 - \\sqrt{737}}{2}',
    ],
    ['\\frac{-3+5}{2}', '\\frac{5-3}{2}'],
    ['\\frac{-2+5}{2}', '\\frac{5-2}{2}'],
    ['\\frac{-6+2}{2} = \\frac{-4}{2}', '\\frac{2-6}{2} = -\\frac{4}{2}'],
    ['\\frac{-1+2}{2}', '\\frac{2-1}{2}'],
    ['-\\frac{-4}{2}=2', '\\frac{4}{2}=2'],
  ]

  for (const [from, to] of specials) {
    s = s.split(from).join(to)
  }

  // --- Pure numeric \frac{-n}{m}, m > 0 literal in denominator
  s = s.replace(/\\frac\{-(\d+)\}\{(\d+)\}/g, '-\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+\.\d+)\}\{(\d+)\}/g, '-\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+)\}\{(\d+\.\d+)\}/g, '-\\frac{$1}{$2}')
  s = s.replace(/\\frac\{-(\d+\.\d+)\}\{(\d+\.\d+)\}/g, '-\\frac{$1}{$2}')

  // Restore protected quadratic formula
  s = s.replace(new RegExp(MARKER, 'g'), '\\frac{-b')

  return s
}

async function* walkMarkdown(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) {
      yield* walkMarkdown(full)
    } else if (e.name.endsWith('.md')) {
      yield full
    }
  }
}

let changedFiles = 0
for (const folder of chapterFolders) {
  const dir = path.join(repoRoot, folder)
  try {
    for await (const filePath of walkMarkdown(dir)) {
      const raw = await readFile(filePath, 'utf8')
      const next = transform(raw)
      if (next !== raw) {
        await writeFile(filePath, next, 'utf8')
        changedFiles++
        console.log('updated:', path.relative(repoRoot, filePath))
      }
    }
  } catch {
    // skip missing folders
  }
}

console.log(`Done. ${changedFiles} file(s) modified.`)
