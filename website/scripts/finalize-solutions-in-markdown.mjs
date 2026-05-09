/**
 * Shortens answers in <details><summary>תשובות סופיות</summary> to final results only.
 *
 * Rules:
 * - Split א./ב./ג./ד./ה. into sub-answers; finalize each sub-body separately.
 * - Strip chains of \\Rightarrow / \\implies / … (keep text after the last arrow).
 * - מונה / מכנה / לכן: keep after last לכן, then optional last "=" segment.
 * - Long "=" chains (≥3 segments, short text): keep last rhs.
 * - fixDollars: prepend "$" when missing (e.g. "3$" → "$3$").
 * - If a stray prefix appears before the first א–ה label, fall back to single-chunk mode.
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

/** Longest arrow tokens first (avoid matching \\Rightarrow inside \\Longrightarrow) */
const ARROWS = ['\\Longrightarrow', '\\Leftrightarrow', '\\Rightarrow', '\\implies', '\\iff']

/** @param {string} t */
function fixDollars(t) {
  const s = t.trim()
  if (!s) return s
  if (s.startsWith('$')) return s
  if (s.endsWith('$')) return `$${s}`
  return s
}

/** @param {string} s */
function afterLastArrow(s) {
  let bestIdx = -1
  let bestLen = 0
  for (const a of ARROWS) {
    const idx = s.lastIndexOf(a)
    if (idx > bestIdx) {
      bestIdx = idx
      bestLen = a.length
    }
  }
  if (bestIdx === -1) return null
  return s.slice(bestIdx + bestLen).trim().replace(/^[,;:\s]+/u, '')
}

/** @param {string} s */
function stripArrowChains(s) {
  let cur = s.trim().replace(/\s+/g, ' ')
  for (let k = 0; k < 20; k++) {
    const tail = afterLastArrow(cur)
    if (!tail || tail.length >= cur.length) break
    cur = tail.replace(/\s+/g, ' ')
  }
  return cur
}

/** @param {string} inner — תוכן מתמטי בלי מפרידי $ חיצוניים */
function collapseArrowInMath(inner) {
  let m = inner.trim()
  for (let k = 0; k < 25; k++) {
    const tail = afterLastArrow(m)
    if (!tail || tail.length >= m.length) break
    m = tail.replace(/\s+/g, ' ')
  }
  return m
}

/** האם מופיעה אות לטינית שמייצגת נעלם (לא חלק מפקודת LaTeX) */
function hasAlgebraicVariable(s) {
  const stripped = s.replace(/\\[a-zA-Z]+/g, ' ').replace(/\\[{}]/g, ' ')
  return /[a-zA-Z]/.test(stripped)
}

/**
 * קיצור שרשראות שוויון בחישוב (למשל 3×4+… = 12+6 = 18 → 18).
 * משוואות עם נעלם נשארות שלמות.
 */
function finalizeMathInner(inner) {
  let m = collapseArrowInMath(inner).trim()
  let parts = m.split(/\s*=\s*/)
  if (parts.length >= 3) {
    return parts[parts.length - 1].trim()
  }
  while (true) {
    parts = m.split(/\s*=\s*/)
    if (parts.length < 2) break
    const left = parts[0]
    if (hasAlgebraicVariable(left)) break
    m = parts.slice(1).join('=').trim()
  }
  return m
}

/**
 * טקסט מחוץ למתמטיקה: קיצור חצים.
 * תומך ב־$$…$$ (בלוק) וב־$…$ (שורה), בסדר הופעה בקובץ.
 */
function transformMathDelimiters(s) {
  let out = ''
  let i = 0
  while (i < s.length) {
    if (s.startsWith('$$', i)) {
      const end = s.indexOf('$$', i + 2)
      if (end === -1) {
        out += stripArrowChains(s.slice(i))
        break
      }
      const inner = finalizeMathInner(s.slice(i + 2, end))
      out += `$$${inner}$$`
      i = end + 2
      continue
    }
    const open = s.indexOf('$', i)
    if (open === -1) {
      out += stripArrowChains(s.slice(i))
      break
    }
    if (open > i) out += stripArrowChains(s.slice(i, open))
    const close = s.indexOf('$', open + 1)
    if (close === -1) {
      out += s.slice(open)
      break
    }
    const inner = finalizeMathInner(s.slice(open + 1, close))
    out += `$${inner}$`
    i = close + 1
  }
  let r = out.replace(/\s+/g, ' ').trim()
  r = r.replace(/\$\$\s*\$\$/g, '$$ $$')
  return r
}

/** כל בלוק $$…$$ מקוצר שוב (מניעת פספוס אחרי טקסט עברית וכו') */
function polishAllDoubleDollar(s) {
  return s.replace(/\$\$([\s\S]*?)\$\$/g, (_, inner) => `$$${finalizeMathInner(inner.trim())}$$`)
}

/** @param {string} original */
function finalizeSingleChunk(original) {
  let s = original.trim().replace(/\s+/g, ' ')
  if (!s) return s

  s = s.replace(/רגע\s*[:–-]\s*/gu, '').trim()

  if (s.includes('נקודות:')) {
    const key = 'נקודות:'
    let tail = s.slice(s.lastIndexOf(key) + key.length).trim()
    tail = tail.replace(/–\s*שתי נקודות חיתוך\s*$/u, '').trim()
    tail = tail.replace(/\s+/g, ' ')
    return fixDollars(tail)
  }

  if (s.includes('מכפלה:') && (s.includes('שבר') || s.includes('שבר ראשון'))) {
    const m = s.match(/מכפלה:\s*(\$[^$]+\$|[\d.]+)\s*$/u)
    if (m) return fixDollars(m[1])
  }

  const hasMN = s.includes('מונה:') || s.includes('מכנה:')
  const hasLK = s.includes('לכן')

  if (hasMN || hasLK) {
    let t = s
    const lk = 'לכן'
    if (t.includes(lk)) {
      const i = t.lastIndexOf(lk)
      t = t.slice(i + lk.length).trim().replace(/^[,;:\s]+/u, '')
    }
    t = t
      .replace(/מונה:\s*/gu, '')
      .replace(/,\s*מכנה:\s*/gu, ' ')
      .replace(/מכנה:\s*/gu, '')
      .replace(/\s+/g, ' ')
      .trim()
    t = t.replace(/^[,;]\s*/u, '').trim()
    t = transformMathDelimiters(t)

    const parts = t.split(/\s*=\s*/)
    if (parts.length >= 2) {
      const last = parts[parts.length - 1].trim()
      if (last.length > 0 && last.length < 500) return fixDollars(last)
    }
    return fixDollars(t)
  }

  s = transformMathDelimiters(s)
  s = polishAllDoubleDollar(s)

  const dollarCount = (s.match(/\$/g) || []).length
  const eqSplits = s.split(/\s*=\s*/)
  if (
    dollarCount <= 2 &&
    eqSplits.length >= 3 &&
    s.length < 800 &&
    !/כי|למשל|ניתן|הסבר/u.test(s)
  ) {
    const last = eqSplits[eqSplits.length - 1].trim()
    if (last.length > 0 && last.length < 500) return fixDollars(last)
  }

  // חצים שנשארו מחוץ לבלוקי $ או אחרי עיבוד
  if (/\\Rightarrow|\\Longrightarrow|\\implies|\\iff|\\Leftrightarrow/u.test(s)) {
    s = stripArrowChains(s)
  }

  return fixDollars(s)
}

const LABEL_RE = /(?:^|\s)(א\.|ב\.|ג\.|ד\.|ה\.)\s+/gu

/** @param {string} raw */
function finalizeAnswerBody(raw) {
  const original = raw.trim()
  if (!original) return original

  const matches = [...original.matchAll(LABEL_RE)]

  if (matches.length >= 2 && matches[0].index > 0) {
    return finalizeSingleChunk(original)
  }

  if (matches.length === 1 && matches[0].index > 0) {
    return finalizeSingleChunk(original)
  }

  if (matches.length === 0) {
    return finalizeSingleChunk(original)
  }

  if (matches.length === 1) {
    const m = matches[0]
    const label = m[1]
    const body = original.slice(m.index + m[0].length).trim()
    return `${label} ${finalizeSingleChunk(body)}`
  }

  const pieces = []
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i]
    const label = m[1]
    const start = m.index + m[0].length
    const end = i + 1 < matches.length ? matches[i + 1].index : original.length
    const body = original.slice(start, end).trim()
    pieces.push(`${label} ${finalizeSingleChunk(body)}`)
  }
  return pieces.join(' ')
}

function isNumberedAnswerLine(trimmed) {
  return (
    /^(\d+)\.\s/u.test(trimmed) ||
    /^\*\*\d+\.\*\*/u.test(trimmed) ||
    /^\*\*תרגיל\s+\d+\s*:\*\*/u.test(trimmed)
  )
}

/** @param {string} block */
function processAnswerBlock(block) {
  const lines = block.split('\n')
  const out = []
  let i = 0
  const numRePlain = /^(\d+)\.\s*(.*)$/u
  const numReBold = /^\*\*(\d+)\.\*\*\s*(.*)$/u
  const numReExercise = /^\*\*תרגיל\s+(\d+)\s*:\*\*\s*(.*)$/u

  while (i < lines.length) {
    const line = lines[i]
    const trimmed = line.trim()
    const mb = trimmed.match(numReBold)
    const mp = trimmed.match(numRePlain)
    const mex = trimmed.match(numReExercise)
    const m = mb || mp || mex
    const bold = Boolean(mb)
    const exercise = Boolean(mex)

    if (m) {
      const n = m[1]
      const parts = [m[2] ?? '']
      i += 1
      while (i < lines.length) {
        const next = lines[i]
        if (isNumberedAnswerLine(next.trim())) break
        parts.push(lines[i])
        i += 1
      }
      let rawBody = parts.join('\n').trim()
      rawBody = stripDerivationNoise(rawBody)
      const finalized = finalizeAnswerBody(rawBody)
      if (exercise) {
        out.push(`**תרגיל ${n}:**`)
        if (finalized) out.push('', finalized)
      } else if (bold) {
        out.push(`**${n}.**`)
        if (finalized) out.push('', finalized)
      } else {
        out.push(`${n}. ${finalized}`)
      }
      continue
    }
    out.push(line)
    i += 1
  }

  return out.join('\n')
}

/** הסרת טקסטי ביניים (הערות בדיקה וכו') מתוך גוף תשובה לפני קיצור מתמטי */
function stripDerivationNoise(text) {
  let t = text
  if (/התשובה המדויקת\s*:/u.test(t)) {
    t = t.replace(/הערה\s*:[\s\S]*?התשובה המדויקת\s*:/u, '')
  }
  t = t.replace(/בדיקה\s*:[\s\S]*?(?=\n\s*ה\.|\n\s*\*\*|$)/u, '')
  return t.trim()
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

  return `${before}\n${processAnswerBlock(block)}\n${after}`
}

async function* walkMarkdown(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) yield* walkMarkdown(full)
    else if (e.name.endsWith('.md')) yield full
  }
}

let scanned = 0
let changed = 0

for (const folder of chapterFolders) {
  const dir = path.join(repoRoot, folder)
  try {
    for await (const filePath of walkMarkdown(dir)) {
      const raw = await readFile(filePath, 'utf8')
      if (!raw.includes(START)) continue
      scanned++
      const next = processFile(raw)
      if (next !== raw) {
        await writeFile(filePath, next, 'utf8')
        changed++
        console.log(path.relative(repoRoot, filePath))
      }
    }
  } catch {
    /* skip */
  }
}

console.log(`\nScanned ${scanned} files with תשובות סופיות. Updated ${changed} files.`)
