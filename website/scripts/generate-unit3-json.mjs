import { readdir, readFile, writeFile, mkdir, copyFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const sourceDir = path.resolve(
  __dirname,
  '../../3 - קריאת והבנת מידע מגרפים מסיפורי מעשה',
)
const outputPath = path.resolve(__dirname, '../src/data/unit3-exercises.json')
const imagesSourceDir = path.join(sourceDir, 'images')
const imagesOutputDir = path.resolve(__dirname, '../public/unit3-images')

const sectionMap = {
  '## רמה 1': 'רמה 1: בניית ביטחון',
  '## רמה 2': 'רמה 2: תרגול שוטף ומשולב',
  '## רמה 3': 'רמה 3: רמת בחינת מה"ט',
}

const imageLinePattern = /^!\[([^\]]*)\]\(([^)]+)\)$/u

const buildPrompt = (rawLines) => {
  const paragraphs = []
  let current = []

  for (const line of rawLines) {
    if (line.length === 0) {
      if (current.length > 0) {
        paragraphs.push(current)
        current = []
      }
    } else {
      current.push(line)
    }
  }
  if (current.length > 0) {
    paragraphs.push(current)
  }

  const outputLines = []

  for (const paragraph of paragraphs) {
    const segments = []

    for (const line of paragraph) {
      const imageMatch = line.match(imageLinePattern)
      if (imageMatch) {
        const alt = imageMatch[1]
        const src = imageMatch[2]
        const filename = src.replace(/^images\//u, '')
        segments.push({ type: 'image', text: `[IMG:${filename}|${alt}]` })
        continue
      }

      if (line.startsWith('$$') && line.endsWith('$$')) {
        segments.push({ type: 'block', text: line })
        continue
      }

      const last = segments[segments.length - 1]
      if (last && last.type === 'text') {
        last.text = `${last.text} ${line}`
      } else {
        segments.push({ type: 'text', text: line })
      }
    }

    for (const segment of segments) {
      outputLines.push(segment.text)
    }
  }

  return outputLines.join('\n')
}

const buildSolution = (rawLines) => {
  if (rawLines.length === 0) {
    return 'לא הוגדר פתרון.'
  }

  const segments = []

  for (const line of rawLines) {
    const trimmed = line.trim()
    if (trimmed.length === 0) {
      continue
    }

    if (trimmed.startsWith('$$') && trimmed.endsWith('$$')) {
      segments.push({ type: 'block', text: trimmed })
      continue
    }

    const last = segments[segments.length - 1]
    if (last && last.type === 'text') {
      last.text = `${last.text}\n${trimmed}`
    } else {
      segments.push({ type: 'text', text: trimmed })
    }
  }

  return segments.map((segment) => segment.text).join('\n')
}

const parseFile = async (fileName) => {
  const fullPath = path.join(sourceDir, fileName)
  const raw = await readFile(fullPath, 'utf8')
  const lines = raw.split(/\r?\n/u)

  const heading = lines.find((line) => line.startsWith('# ')) ?? ''
  const title = heading.replace(/^#\s*תת-נושא\s*/u, '').trim()
  const subtopicId = fileName.split('_')[0]

  const exercises = []
  const solutionsMap = {}

  let currentLevel = ''
  let inAnswers = false
  let currentAnswerNumber = null
  let currentAnswerLines = []

  const flushAnswer = () => {
    if (currentAnswerNumber === null) {
      return
    }
    solutionsMap[currentAnswerNumber] = buildSolution(currentAnswerLines)
    currentAnswerNumber = null
    currentAnswerLines = []
  }

  for (let i = 0; i < lines.length; i += 1) {
    const rawLine = lines[i]
    const line = rawLine.trim()

    if (line.startsWith('<summary>תשובות סופיות</summary>')) {
      inAnswers = true
      continue
    }

    if (line.startsWith('</details>')) {
      flushAnswer()
      inAnswers = false
      continue
    }

    if (inAnswers) {
      const answerMatch = line.match(/^(\d+)\.\s*(.*)$/u)
      if (answerMatch) {
        flushAnswer()
        currentAnswerNumber = Number(answerMatch[1])
        const rest = answerMatch[2].trim()
        currentAnswerLines = rest.length > 0 ? [rest] : []
      } else if (currentAnswerNumber !== null) {
        currentAnswerLines.push(line)
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
    const rawLines = [exerciseMatch[2].trim()]

    let j = i + 1
    while (j < lines.length) {
      const next = lines[j].trim()

      if (
        /^(\d+)\.\s+/u.test(next) ||
        next.startsWith('## רמה') ||
        next.startsWith('---') ||
        next.startsWith('<details>')
      ) {
        break
      }

      rawLines.push(next)
      j += 1
    }

    i = j - 1

    while (rawLines.length > 0 && rawLines[rawLines.length - 1] === '') {
      rawLines.pop()
    }

    exercises.push({
      id: number,
      level: currentLevel,
      prompt: buildPrompt(rawLines),
      solution: '',
    })
  }

  for (const exercise of exercises) {
    exercise.solution = solutionsMap[exercise.id] ?? 'לא הוגדר פתרון.'
  }

  return {
    id: subtopicId,
    title,
    sourceFile: fileName,
    exercises,
  }
}

const copyImages = async () => {
  await mkdir(imagesOutputDir, { recursive: true })
  const entries = await readdir(imagesSourceDir)
  await Promise.all(
    entries
      .filter((name) => name.toLowerCase().endsWith('.png'))
      .map((name) =>
        copyFile(path.join(imagesSourceDir, name), path.join(imagesOutputDir, name)),
      ),
  )
}

const build = async () => {
  const files = await readdir(sourceDir)
  const markdownFiles = files
    .filter((name) => name.endsWith('.md'))
    .sort((a, b) => a.localeCompare(b, 'he', { numeric: true }))

  const subtopics = await Promise.all(markdownFiles.map(parseFile))

  const output = {
    unitId: 3,
    unitTitle: 'קריאת והבנת מידע מגרפים מסיפורי מעשה',
    generatedAt: new Date().toISOString(),
    imageBaseUrl: '/unit3-images/',
    subtopics,
  }

  await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8')
  await copyImages()
}

await build()
