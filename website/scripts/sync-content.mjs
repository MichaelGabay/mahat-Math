import { readdir, readFile, writeFile, mkdir, copyFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')
const websiteRoot = path.resolve(__dirname, '..')

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

const sectionMap = {
  '## רמה 1': 'רמה 1: בניית ביטחון',
  '## רמה 2': 'רמה 2: תרגול שוטף ומשולב',
  '## רמה 3': 'רמה 3: רמת בחינת מה"ט',
}

const imageLinePattern = /^!\[([^\]]*)\]\(([^)]+)\)$/u
const exercisePattern = /^(?:\*\*)?(\d+)\.(?:\*\*)?\s*(.*)$/u
/** כותרות תשובה בסגנון **תרגיל 12:** (פרק שאלות מילוליות ועוד) */
const answerHeadingPattern = /^\*\*תרגיל\s+(\d+):\*\*\s*(.*)$/u

const normalizeTitle = (fileName) =>
  fileName
    .replace(/\.md$/u, '')
    .split('_')
    .slice(1)
    .join(' ')
    .trim()

const buildPrompt = (rawLines) => {
  const output = []
  for (const line of rawLines) {
    if (!line) {
      continue
    }

    const imageMatch = line.match(imageLinePattern)
    if (imageMatch) {
      const alt = imageMatch[1]
      const src = imageMatch[2]
      const filename = src.replace(/^images\//u, '')
      output.push(`[IMG:${filename}|${alt}]`)
      continue
    }

    output.push(line)
  }
  return output.join('\n').trim()
}

const buildSolution = (rawLines) => {
  const lines = rawLines.filter((line) => line.trim().length > 0)
  if (lines.length === 0) {
    return 'לא הוגדר פתרון.'
  }
  return lines.join('\n').trim()
}

/** פיצול שורות תשובה שמוזגו בטעות (למשל $5.$ ואז 14.$ לפני \\dfrac) */
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
  /** לא לפצל $8.9$ או $33.75$ — רק נקודה שאינה חלק ממספר עשרוני */
  const tertiary = /(?<=\$)(\d{1,2})\.(?!\d)/u

  let chunks = splitOnce(trimmed, primary)
  chunks = chunks.flatMap((chunk) => splitOnce(chunk, secondary))
  chunks = chunks.flatMap((chunk) => splitOnce(chunk, tertiary))
  return chunks
}

const parseFile = async (filePath, fileName) => {
  const raw = await readFile(filePath, 'utf8')
  const lines = raw.split(/\r?\n/u)
  const subtopicId = fileName.split('_')[0]
  const title = normalizeTitle(fileName)

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
    const line = lines[i].trim()

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
      const headingMatch = line.match(answerHeadingPattern)
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
      continue
    }

    const sectionEntry = Object.keys(sectionMap).find((key) => line.startsWith(key))
    if (sectionEntry) {
      currentLevel = sectionMap[sectionEntry]
      continue
    }

    const exerciseMatch = line.match(exercisePattern)
    if (!exerciseMatch) {
      continue
    }

    const number = Number(exerciseMatch[1])
    const rawPromptLines = []
    const firstPrompt = exerciseMatch[2]?.trim() ?? ''
    if (firstPrompt) {
      rawPromptLines.push(firstPrompt)
    }

    let j = i + 1
    while (j < lines.length) {
      const next = lines[j].trim()
      if (
        exercisePattern.test(next) ||
        next.startsWith('## רמה') ||
        next.startsWith('---') ||
        next.startsWith('<details>')
      ) {
        break
      }
      rawPromptLines.push(next)
      j += 1
    }

    i = j - 1
    exercises.push({
      id: number,
      level: currentLevel,
      prompt: buildPrompt(rawPromptLines),
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

const syncChapterImages = async (chapterDir, chapterId) => {
  const sourceImagesDir = path.join(chapterDir, 'images')
  let entries = []
  try {
    entries = await readdir(sourceImagesDir)
  } catch {
    return ''
  }

  const pngFiles = entries.filter((name) => name.toLowerCase().endsWith('.png'))
  if (pngFiles.length === 0) {
    return ''
  }

  const outputDirName = `chapter${chapterId}-images`
  const outputDir = path.join(websiteRoot, 'public', outputDirName)
  await mkdir(outputDir, { recursive: true })

  await Promise.all(
    pngFiles.map((name) => copyFile(path.join(sourceImagesDir, name), path.join(outputDir, name))),
  )

  return `/${outputDirName}/`
}

const build = async () => {
  const chapters = []
  const chapterExercises = {}

  for (const chapterRoot of chaptersRoot) {
    const chapterDir = path.join(repoRoot, chapterRoot)
    const chapterId = Number(chapterRoot.split(' - ')[0])
    const chapterTitle = chapterRoot.split(' - ').slice(1).join(' - ')

    const files = await readdir(chapterDir)
    const markdownFiles = files
      .filter((name) => name.endsWith('.md'))
      .sort((a, b) => a.localeCompare(b, 'he', { numeric: true }))

    const subtopics = await Promise.all(
      markdownFiles.map((fileName) => parseFile(path.join(chapterDir, fileName), fileName)),
    )

    const imageBaseUrl = await syncChapterImages(chapterDir, chapterId)

    chapters.push({
      id: chapterId,
      title: chapterTitle,
      subtopics: subtopics.map((subtopic) => `${subtopic.id} ${subtopic.title}`),
    })

    chapterExercises[chapterId] = {
      chapterId,
      chapterTitle,
      generatedAt: new Date().toISOString(),
      imageBaseUrl,
      subtopics,
    }
  }

  const chaptersFile = `export const chapters = ${JSON.stringify(chapters, null, 2)};\n`
  await writeFile(path.join(websiteRoot, 'src/data/chapters.js'), chaptersFile, 'utf8')

  await writeFile(
    path.join(websiteRoot, 'src/data/exercises-by-chapter.json'),
    `${JSON.stringify(chapterExercises, null, 2)}\n`,
    'utf8',
  )
}

await build()
