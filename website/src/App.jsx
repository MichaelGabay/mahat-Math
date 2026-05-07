import { useMemo, useState } from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import { chapters } from './data/chapters'
import unit1Exercises from './data/unit1-exercises.json'
import unit3Exercises from './data/unit3-exercises.json'
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

  return lines.map((line, index) => {
    const imageMatch = line.match(imageMarkerPattern)

    if (imageMatch) {
      const filename = imageMatch[1].trim()
      const alt = imageMatch[2].trim()
      return (
        <figure className="exercise-image" key={`${keyPrefix}-image-${index}`}>
          <img
            src={`${imageBaseUrl}${filename}`}
            alt={alt}
            loading="lazy"
          />
        </figure>
      )
    }

    const blockMatch = line.match(blockFormulaPattern)

    if (blockMatch) {
      return (
        <div className="math-line" key={`${keyPrefix}-block-${index}`}>
          <BlockMath math={blockMatch[1].trim()} />
        </div>
      )
    }

    return (
      <p className="text-line" key={`${keyPrefix}-line-${index}`}>
        {renderInlineMath(line, `${keyPrefix}-${index}`)}
      </p>
    )
  })
}

const buildSubtopicMapForSource = (source) => {
  const baseUrl = source.imageBaseUrl ?? ''
  const map = {}
  for (const subtopic of source.subtopics) {
    map[subtopic.id] = { subtopic, imageBaseUrl: baseUrl }
  }
  return map
}

const buildIdsByChapter = (unitExerciseJson, chapterId) => ({
  chapterId,
  ids: new Set(unitExerciseJson.subtopics.map((s) => s.id)),
})

const FIRST_CHAPTER_ID_WITHOUT_BOUND_EXERCISES = 4

function App() {
  const [openChapterId, setOpenChapterId] = useState(chapters[0]?.id ?? null)

  const subtopicEntryByChapter = useMemo(
    () => ({
      1: buildSubtopicMapForSource(unit1Exercises),
      3: buildSubtopicMapForSource(unit3Exercises),
    }),
    [],
  )

  const exerciseChaptersMeta = useMemo(
    () => [buildIdsByChapter(unit1Exercises, 1), buildIdsByChapter(unit3Exercises, 3)],
    [],
  )

  const exercisesBoundToChapter = (chapterId, subtopicToken) =>
    exerciseChaptersMeta.some(
      (meta) => meta.chapterId === chapterId && meta.ids.has(subtopicToken),
    )

  const [selection, setSelection] = useState(() => ({
    chapterId: chapters[0]?.id ?? null,
    subtopicToken: unit1Exercises.subtopics[0]?.id ?? null,
  }))
  const [openSolutions, setOpenSolutions] = useState({})

  const exercisesAvailableForChapter = (chapterId, subtopicToken) =>
    chapterId != null &&
    chapterId < FIRST_CHAPTER_ID_WITHOUT_BOUND_EXERCISES &&
    exercisesBoundToChapter(chapterId, subtopicToken)

  const selectedEntry =
    selection.chapterId != null &&
    selection.subtopicToken &&
    exercisesAvailableForChapter(selection.chapterId, selection.subtopicToken)
      ? subtopicEntryByChapter[selection.chapterId]?.[selection.subtopicToken] ?? null
      : null
  const selectedSubtopic = selectedEntry?.subtopic ?? null
  const selectedImageBaseUrl = selectedEntry?.imageBaseUrl ?? ''
  const hasSelectedSubtopicExercises = Boolean(selectedSubtopic)
  const awaitingContent =
    selection.chapterId != null &&
    selection.chapterId >= FIRST_CHAPTER_ID_WITHOUT_BOUND_EXERCISES &&
    Boolean(selection.subtopicToken)

  const awaitingEarlyChapterContent =
    selection.chapterId != null &&
    selection.subtopicToken &&
    selection.chapterId < FIRST_CHAPTER_ID_WITHOUT_BOUND_EXERCISES &&
    !hasSelectedSubtopicExercises &&
    !awaitingContent

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
                      const canShowExercises = exercisesAvailableForChapter(
                        chapter.id,
                        subtopicToken,
                      )
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
                            {!canShowExercises && <span className="soon-pill">בקרוב</span>}
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
          ) : awaitingContent ? (
            <div className="empty-state">
              <h2>תוכן בהכנה</h2>
              <p>
                מפרק 4 ואילך, החל בנושא משוואות ממעלה ראשונה, התרגילים עדיין לא מקושרים לתפריט.
                בינתיים לא מוצג כאן תוכן, כדי שלא יוצג חומר שאינו תואם לתת-הנושא שבחרתם.
              </p>
            </div>
          ) : awaitingEarlyChapterContent ? (
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
