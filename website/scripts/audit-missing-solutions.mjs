/**
 * סיכום תרגילים שחסר להם פתרון בקובצי Markdown (לפי אותה לוגיקה כמו sync-content.mjs).
 * הרצה: node website/scripts/audit-missing-solutions.mjs
 */
import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, '..', '..')

const chaptersRoot = [
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

const exercisePattern = /^(?:\*\*)?(\d+)\.(?:\*\*)?\s*(.*)$/u
const answerHeadingPattern = /^\*\*תרגיל\s+(\d+):\*\*\s*(.*)$/u

const splitMergedAnswerFragments = (line) => {
  const trimmed = line.trim()
  if (!trimmed) {
    return []
  }

  const splitOnce = (text, delimiterWithNumCapture) => {
    if (!delimiterWithNumCapture.test(text)) {
      return [text]
    }
    delimiterWithNumCapture.lastIndex = 0
    const parts = text.split(delimiterWithNumCapture)
    const out = []
    const head = parts[0]?.trim() ?? ''
    if (head.length > 0) {
      out.push(head)
    }
    for (let i = 1; i < parts.length; i += 2) {
      const num = parts[i]
      const rest = parts[i + 1]?.trim() ?? ''
      out.push(`${num}. ${rest}`)
    }
    return out
  }

  const primary = /\$(\d+)\.\$/u
  const secondary = /(?<=[^\d$])(\d{1,2})\.\$(?=\S)/u
  const tertiary = /(?<=\$)(\d{1,2})\./u

  let chunks = splitOnce(trimmed, primary)
  chunks = chunks.flatMap((chunk) => splitOnce(chunk, secondary))
  chunks = chunks.flatMap((chunk) => splitOnce(chunk, tertiary))
  return chunks
}

const parseSolutionsMap = (lines) => {
  let inAnswers = false
  let currentAnswerNumber = null
  let currentAnswerLines = []
  const solutionsMap = {}

  const flushAnswer = () => {
    if (currentAnswerNumber === null) {
      return
    }
    const linesFiltered = currentAnswerLines.filter((line) => line.trim().length > 0)
    solutionsMap[currentAnswerNumber] =
      linesFiltered.length === 0 ? null : linesFiltered.join('\n').trim()
    currentAnswerNumber = null
    currentAnswerLines = []
  }

  for (const line of lines) {
    const l = line.trim()
    if (l.startsWith('<summary>תשובות סופיות</summary>')) {
      inAnswers = true
      continue
    }
    if (l.startsWith('</details>')) {
      flushAnswer()
      inAnswers = false
      continue
    }
    if (!inAnswers) {
      continue
    }

    const headingMatch = l.match(answerHeadingPattern)
    if (headingMatch) {
      flushAnswer()
      currentAnswerNumber = Number(headingMatch[1])
      const rest = headingMatch[2]?.trim() ?? ''
      currentAnswerLines = rest ? [rest] : []
      continue
    }

    const fragments = splitMergedAnswerFragments(line)
    for (const fragment of fragments) {
      const match = fragment.match(exercisePattern)
      if (match) {
        flushAnswer()
        currentAnswerNumber = Number(match[1])
        const rest = match[2]?.trim() ?? ''
        currentAnswerLines = rest ? [rest] : []
      } else if (currentAnswerNumber !== null) {
        currentAnswerLines.push(fragment)
      }
    }
  }

  return solutionsMap
}

const exerciseNumbersInPrompts = (lines) => {
  const nums = new Set()
  let inAnswers = false
  for (const line of lines) {
    const t = line.trim()
    if (t.startsWith('<summary>תשובות סופיות</summary>')) {
      inAnswers = true
      continue
    }
    if (t.startsWith('</details>')) {
      inAnswers = false
      continue
    }
    if (inAnswers) {
      continue
    }
    const m = t.match(exercisePattern)
    if (m && !t.startsWith('##')) {
      nums.add(Number(m[1]))
    }
  }
  return nums
}

let totalMissing = 0
const rows = []

for (const ch of chaptersRoot) {
  const chapterDir = path.join(repoRoot, ch)
  let files = []
  try {
    files = (await readdir(chapterDir)).filter((n) => n.endsWith('.md'))
  } catch {
    continue
  }

  for (const fileName of files) {
    const raw = await readFile(path.join(chapterDir, fileName), 'utf8')
    const lines = raw.split(/\r?\n/u)
    const want = exerciseNumbersInPrompts(lines)
    const solutionsMap = parseSolutionsMap(lines)

    const missing = [...want].filter((id) => solutionsMap[id] == null || solutionsMap[id] === '').sort((a, b) => a - b)
    if (missing.length === 0) {
      continue
    }

    totalMissing += missing.length
    const rel = path.join(ch, fileName)
    for (const id of missing) {
      rows.push(`${rel}\t${id}`)
    }
  }
}

console.log(`סה״כ תרגילים ללא פתרון מזוהה בקבצים: ${totalMissing}`)
console.log(rows.join('\n'))
