/**
 * Repair answer lines where math lost its opening $ (e.g. "3$" → "$3$").
 * Only touches lines inside <details> … תשובות סופיות … </details>.
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

const START = '<summary>תשובות סופיות</summary>'
const END = '</details>'

/** @param {string} body */
function fixLineBody(body) {
  let t = body.trim()
  if (!t) return t
  // תיקון עיוות: $ לפני עברית בתחילת שורה (נוצר מעטיפה מוטעת)
  t = t.replace(/^\$([\u0590-\u05FF])/u, '$1')
  t = t.replace(/\$(א\.|ב\.|ג\.|ד\.|ה\.)\$/gu, (_, L) => `${L} `)
  if (t.startsWith('$')) return t
  if (t.endsWith('$')) {
    if (/^(א\.|ב\.|ג\.|ד\.|ה\.)/u.test(t)) return t
    // אל תוסיף $ לפני שורה שכבר מכילה עברית (תווית + מתמטיקה באותה שורה)
    if (/[\u0590-\u05FF]/.test(t)) return t
    return `$${t}`
  }
  return t
}

/** @param {string} block */
function repairBlock(block) {
  let blockNorm = block.replace(/\$(א\.|ב\.|ג\.|ד\.|ה\.)\$/gu, (_, L) => `${L} `)
  const lines = blockNorm.split('\n').map((line) =>
    line.replace(/^(\s*)\$([\u0590-\u05FF])/u, '$1$2')
  )
  const out = []
  for (const line of lines) {
    const trim = line.trim()
    const mb = trim.match(/^\*\*(\d+)\.\*\*\s*(.*)$/u)
    const mp = trim.match(/^(\d+)\.\s*(.*)$/u)
    const mex = trim.match(/^\*\*תרגיל\s+(\d+)\s*:\*\*\s*(.*)$/u)
    const m = mb || mp || mex
    if (m) {
      if (mb) {
        out.push(`**${m[1]}.** ${fixLineBody(m[2])}`.trimEnd())
      } else if (mex) {
        out.push(`**תרגיל ${m[1]}:** ${fixLineBody(m[2])}`.trimEnd())
      } else {
        out.push(`${m[1]}. ${fixLineBody(m[2])}`)
      }
    } else {
      out.push(line)
    }
  }
  return out.join('\n')
}

/** @param {string} fileContent */
function processFile(fileContent) {
  const startIdx = fileContent.indexOf(START)
  if (startIdx === -1) return fileContent

  const innerStart = startIdx + START.length
  const endIdx = fileContent.indexOf(END, innerStart)
  if (endIdx === -1) return fileContent

  const before = fileContent.slice(0, innerStart)
  const block = fileContent.slice(innerStart, endIdx)
  const after = fileContent.slice(endIdx)

  return `${before}\n${repairBlock(block)}\n${after}`
}

async function* walkMarkdown(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) yield* walkMarkdown(full)
    else if (e.name.endsWith('.md')) yield full
  }
}

let n = 0
for (const folder of chapterFolders) {
  const dir = path.join(repoRoot, folder)
  try {
    for await (const filePath of walkMarkdown(dir)) {
      const raw = await readFile(filePath, 'utf8')
      if (!raw.includes(START)) continue
      const next = processFile(raw)
      if (next !== raw) {
        await writeFile(filePath, next, 'utf8')
        n++
      }
    }
  } catch {
    /* skip */
  }
}

console.log(`Repaired opening $ in ${n} files.`)
