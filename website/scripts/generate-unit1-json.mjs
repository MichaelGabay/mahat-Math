import { readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const sourceDir = path.resolve(__dirname, '../../1 - טכניקה אלגברית')
const outputPath = path.resolve(__dirname, '../src/data/unit1-exercises.json')

const sectionMap = {
  '## רמה 1': 'רמה 1: בניית ביטחון',
  '## רמה 2': 'רמה 2: תרגול שוטף ומשולב',
  '## רמה 3': 'רמה 3: רמת בחינת מה"ט',
}

const parseFile = async (fileName) => {
  const fullPath = path.join(sourceDir, fileName)
  const raw = await readFile(fullPath, 'utf8')
  const lines = raw.split(/\r?\n/)

  const heading = lines.find((line) => line.startsWith('# ')) ?? ''
  const title = heading.replace(/^#\s*תת-נושא\s*/u, '').trim()
  const subtopicId = fileName.split('_')[0]

  const exercises = []
  const solutionsMap = {}

  let currentLevel = ''
  let inAnswers = false
  let currentAnswerNumber = null

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i].trim()

    if (line.startsWith('<summary>תשובות סופיות</summary>')) {
      inAnswers = true
      continue
    }

    if (line.startsWith('</details>')) {
      inAnswers = false
    }

    if (inAnswers) {
      const answerMatch = line.match(/^(\d+)\.\s*(.+)$/u)
      if (answerMatch) {
        currentAnswerNumber = Number(answerMatch[1])
        solutionsMap[currentAnswerNumber] = answerMatch[2].trim()
      } else if (currentAnswerNumber && line.length > 0) {
        const previous = solutionsMap[currentAnswerNumber] ?? ''
        solutionsMap[currentAnswerNumber] = `${previous}\n${line}`.trim()
      }
      continue
    }

    const sectionEntry = Object.keys(sectionMap).find((key) => line.startsWith(key))
    if (sectionEntry) {
      currentLevel = sectionMap[sectionEntry]
      continue
    }

    const exerciseMatch = line.match(/^(\d+)\.\s*(.+)$/u)
    if (!exerciseMatch) {
      continue
    }

    const number = Number(exerciseMatch[1])
    const promptLines = [exerciseMatch[2].trim()]

    let j = i + 1
    while (j < lines.length) {
      const next = lines[j].trim()

      if (
        /^(\d+)\.\s+/.test(next) ||
        next.startsWith('## רמה') ||
        next.startsWith('---') ||
        next.startsWith('<details>')
      ) {
        break
      }

      if (next.length > 0) {
        promptLines.push(next)
      }
      j += 1
    }

    i = j - 1

    exercises.push({
      id: number,
      level: currentLevel,
      prompt: promptLines.join('\n'),
      solution: '',
    })
  }

  for (const ex of exercises) {
    ex.solution = solutionsMap[ex.id] ?? 'לא הוגדר פתרון.'
  }

  return {
    id: subtopicId,
    title,
    sourceFile: fileName,
    exercises,
  }
}

const build = async () => {
  const files = await readdir(sourceDir)
  const markdownFiles = files.filter((name) => name.endsWith('.md')).sort((a, b) =>
    a.localeCompare(b, 'he', { numeric: true }),
  )

  const subtopics = await Promise.all(markdownFiles.map(parseFile))

  const output = {
    unitId: 1,
    unitTitle: 'טכניקה אלגברית',
    generatedAt: new Date().toISOString(),
    subtopics,
  }

  await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8')
}

await build()
