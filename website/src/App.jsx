import { useMemo, useState } from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import { chapters } from './data/chapters'
import exercisesByChapter from './data/exercises-by-chapter.json'
import 'katex/dist/katex.min.css'
import './App.css'

const blockFormulaPattern = /^\$\$(.+)\$\$$/u
const inlineFormulaPattern = /(\$[^$\n]+\$)/u
const imageMarkerPattern = /^\[IMG:([^|\]]+)\|([^\]]*)\]$/u

const renderInlineMath = (text, keyPrefix) => {
  const parts = text.split(inlineFormulaPattern).filter(Boolean)

  return parts.map((part, index) => {
    if (part.startsWith('$') && part.endsWith('$')) {
      const math = part.slice(1, -1).trim()
      return (
        <span className="inline-math" dir="ltr" key={`${keyPrefix}-math-${index}`}>
          <InlineMath math={math} />
        </span>
      )
    }

    return <span key={`${keyPrefix}-text-${index}`}>{part}</span>
  })
}

const renderMathText = (content, keyPrefix, imageBaseUrl = '') => {
  const lines = content.split('\n').map((line) => line.trim()).filter(Boolean)
  const nodes = []
  let textBuffer = []

  const flushTextBuffer = (index) => {
    if (textBuffer.length === 0) {
      return
    }
    nodes.push(
      <p className="text-line" key={`${keyPrefix}-line-${index}`}>
        {renderInlineMath(textBuffer.join(' '), `${keyPrefix}-${index}`)}
      </p>,
    )
    textBuffer = []
  }

  lines.forEach((line, index) => {
    const imageMatch = line.match(imageMarkerPattern)

    if (imageMatch) {
      flushTextBuffer(index)
      const filename = imageMatch[1].trim()
      const alt = imageMatch[2].trim()
      nodes.push(
        <figure className="exercise-image" key={`${keyPrefix}-image-${index}`}>
          <img
            src={`${imageBaseUrl}${filename}`}
            alt={alt}
            loading="lazy"
          />
        </figure>
      )
      return
    }

    const blockMatch = line.match(blockFormulaPattern)

    if (blockMatch) {
      flushTextBuffer(index)
      nodes.push(
        <div className="math-line" key={`${keyPrefix}-block-${index}`}>
          <BlockMath math={blockMatch[1].trim()} />
        </div>
      )
      return
    }

    textBuffer.push(line)
  })

  flushTextBuffer(lines.length)

  return nodes
}

const buildSubtopicMapForSource = (source) => {
  const baseUrl = source.imageBaseUrl ?? ''
  const map = {}
  for (const subtopic of source.subtopics) {
    map[subtopic.id] = { subtopic, imageBaseUrl: baseUrl }
  }
  return map
}

function App() {
  const [openChapterId, setOpenChapterId] = useState(chapters[0]?.id ?? null)

  const subtopicEntryByChapter = useMemo(() => {
    const map = {}
    for (const [chapterId, source] of Object.entries(exercisesByChapter)) {
      map[chapterId] = buildSubtopicMapForSource(source)
    }
    return map
  }, [])

  const [selection, setSelection] = useState(() => ({
    chapterId: chapters[0]?.id ?? null,
    subtopicToken:
      chapters[0]?.subtopics?.[0]?.split(' ')[0] ?? null,
  }))
  const [openSolutions, setOpenSolutions] = useState({})

  const selectedEntry = selection.chapterId != null && selection.subtopicToken
    ? subtopicEntryByChapter[selection.chapterId]?.[selection.subtopicToken] ?? null
    : null
  const selectedSubtopic = selectedEntry?.subtopic ?? null
  const selectedImageBaseUrl = selectedEntry?.imageBaseUrl ?? ''
  const hasSelectedSubtopicExercises = Boolean(selectedSubtopic)

  const toggleChapter = (chapterId) => {
    setOpenChapterId((currentOpenId) => (currentOpenId === chapterId ? null : chapterId))
  }

  const toggleSolution = (exerciseKey) => {
    setOpenSolutions((current) => ({
      ...current,
      [exerciseKey]: !current[exerciseKey],
    }))
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="ניווט נושאים">
        <div className="sidebar-header">
          <p className="kicker">MAHAT 99913</p>
          <h2>תרגול לפי נושאים</h2>
        </div>

        <nav className="chapters-nav">
          {chapters.map((chapter) => {
            const isOpen = openChapterId === chapter.id

            return (
              <section
                className={`chapter-item ${isOpen ? 'open' : ''}`}
                key={chapter.id}
              >
                <button
                  type="button"
                  className="chapter-toggle"
                  onClick={() => toggleChapter(chapter.id)}
                  aria-expanded={isOpen}
                  aria-controls={`chapter-panel-${chapter.id}`}
                >
                  <span className="chapter-label">
                    {chapter.id}. {chapter.title}
                  </span>
                  <span className="chapter-arrow" aria-hidden="true">
                    {isOpen ? '−' : '+'}
                  </span>
                </button>

                {isOpen && (
                  <ul id={`chapter-panel-${chapter.id}`} className="subtopic-list">
                    {chapter.subtopics.map((subtopic) => {
                      const subtopicToken = subtopic.split(' ')[0]
                      const isSelected =
                        selection.chapterId === chapter.id &&
                        selection.subtopicToken === subtopicToken

                      return (
                        <li key={subtopic}>
                          <button
                            type="button"
                            className={`subtopic-button ${isSelected ? 'active' : ''}`}
                            onClick={() => {
                              setSelection({
                                chapterId: chapter.id,
                                subtopicToken,
                              })
                            }}
                          >
                            {subtopic}
                          </button>
                        </li>
                      )
                    })}
                  </ul>
                )}
              </section>
            )
          })}
        </nav>
      </aside>

      <main className="content">
        <section className="exercise-view">
          {hasSelectedSubtopicExercises ? (
            <>
              <header className="exercise-header">
                <h1>{selectedSubtopic.title}</h1>
                <p>{selectedSubtopic.exercises.length} תרגילים</p>
              </header>

              <ol className="exercise-list">
                {selectedSubtopic.exercises.map((exercise) => {
                  const exerciseKey = `${selectedSubtopic.id}-${exercise.id}`
                  const isOpen = Boolean(openSolutions[exerciseKey])

                  return (
                    <li key={exerciseKey} className="exercise-card">
                      <p className="exercise-level">{exercise.level}</p>
                      <div className="exercise-prompt">
                        {renderMathText(exercise.prompt, exerciseKey, selectedImageBaseUrl)}
                      </div>
                      <button
                        type="button"
                        className="solution-toggle"
                        onClick={() => toggleSolution(exerciseKey)}
                      >
                        {isOpen ? 'הסתר פתרון' : 'הצג פתרון'}
                      </button>
                      {isOpen && (
                        <div className="exercise-solution">
                          {renderMathText(
                            exercise.solution,
                            `${exerciseKey}-solution`,
                            selectedImageBaseUrl,
                          )}
                        </div>
                      )}
                    </li>
                  )
                })}
              </ol>
            </>
          ) : selection.chapterId && selection.subtopicToken ? (
            <div className="empty-state">
              <h2>תוכן בהכנה</h2>
              <p>לתת-נושא זה עדיין אין באתר סט תרגילים. נשמח להוסיף אותו בהמשך.</p>
            </div>
          ) : (
            <div className="empty-state">
              <h2>בחרו תת-נושא</h2>
              <p>התרגילים יופיעו כאן לאחר בחירת תת-נושא מהתפריט.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
