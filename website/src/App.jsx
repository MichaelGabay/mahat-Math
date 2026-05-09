import { useCallback, useEffect, useLayoutEffect, useMemo, useState } from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import { chapters } from './data/chapters'
import exercisesByChapter from './data/exercises-by-chapter.json'
import 'katex/dist/katex.min.css'
import './App.css'

const LAST_PLACE_STORAGE_KEY = 'mahat-math:last-place'
const MOBILE_NAV_MEDIA = '(max-width: 1050px)'
const COLOR_MODE_STORAGE_KEY = 'mahat-math:color-mode'

const readStoredColorMode = () => {
  if (typeof window === 'undefined') {
    return 'light'
  }
  try {
    const raw = window.localStorage.getItem(COLOR_MODE_STORAGE_KEY)
    if (raw === 'dark' || raw === 'light') {
      return raw
    }
  } catch {
    /* ignore */
  }
  try {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
  } catch {
    /* ignore */
  }
  return 'light'
}

const useMatchMedia = (query) => {
  const getMatches = () =>
    typeof window !== 'undefined' ? window.matchMedia(query).matches : false

  const [matches, setMatches] = useState(getMatches)

  useEffect(() => {
    const mq = window.matchMedia(query)
    const onChange = () => setMatches(mq.matches)
    onChange()
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [query])

  return matches
}

const getDefaultSelection = () => ({
  chapterId: chapters[0]?.id ?? null,
  subtopicToken: chapters[0]?.subtopics?.[0]?.split(' ')[0] ?? null,
})

const readSavedSelection = () => {
  if (typeof window === 'undefined') {
    return null
  }
  try {
    const raw = window.localStorage.getItem(LAST_PLACE_STORAGE_KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw)
    const chapterId = Number(parsed.chapterId)
    const subtopicToken =
      typeof parsed.subtopicToken === 'string' ? parsed.subtopicToken : null
    if (!Number.isFinite(chapterId) || subtopicToken == null || subtopicToken === '') {
      return null
    }
    const chapter = chapters.find((c) => c.id === chapterId)
    if (!chapter) {
      return null
    }
    const tokenOk = chapter.subtopics.some((st) => st.split(' ')[0] === subtopicToken)
    if (!tokenOk) {
      return null
    }
    return { chapterId, subtopicToken }
  } catch {
    return null
  }
}

const getInitialNavigation = () => {
  const defaults = getDefaultSelection()
  const saved = readSavedSelection()
  const selection = saved ?? defaults
  const openChapterId = saved?.chapterId ?? defaults.chapterId
  return { selection, openChapterId }
}

const blockFormulaPattern = /^\$\$(.+)\$\$$/u
const inlineFormulaPattern = /(\$[^$\n]+\$)/u
const imageMarkerPattern = /^\[IMG:([^|\]]+)\|([^\]]*)\]$/u
/** שורה שמתחילה בסעיף ממוספר בעברית (א. ב. ג. …) — מפרידה בין הנתונים לסעיפים (גם בלי רווח אחרי הנקודה) */
const hebrewSubItemLinePattern = /^[\u05D0-\u05EA]\./u
/** טקסט מודגש בסגנון Markdown — האתר לא מריץ מפרש Markdown מלא */
const boldChunkPattern = /(\*\*[^*]+\*\*)/gu

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

const renderRichInline = (text, keyPrefix) => {
  const chunks = text.split(boldChunkPattern).filter(Boolean)
  return chunks.map((chunk, index) => {
    if (chunk.startsWith('**') && chunk.endsWith('**')) {
      const inner = chunk.slice(2, -2)
      return (
        <strong key={`${keyPrefix}-b-${index}`}>
          {renderInlineMath(inner, `${keyPrefix}-b-${index}`)}
        </strong>
      )
    }
    return <span key={`${keyPrefix}-t-${index}`}>{renderInlineMath(chunk, `${keyPrefix}-t-${index}`)}</span>
  })
}

const renderMathText = (content, keyPrefix, imageBaseUrl = '') => {
  const rawLines = content.split(/\r?\n/u)
  const nodes = []
  let textBuffer = []

  const flushTextBuffer = (index) => {
    if (textBuffer.length === 0) {
      return
    }
    nodes.push(
      <p className="text-line" key={`${keyPrefix}-line-${index}`}>
        {renderRichInline(textBuffer.join(' '), `${keyPrefix}-${index}`)}
      </p>,
    )
    textBuffer = []
  }

  rawLines.forEach((rawLine, index) => {
    const line = rawLine.trim()

    if (line.length === 0) {
      flushTextBuffer(index)
      return
    }

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
        </figure>,
      )
      return
    }

    const blockMatch = line.match(blockFormulaPattern)

    if (blockMatch) {
      flushTextBuffer(index)
      nodes.push(
        <div className="math-line" key={`${keyPrefix}-block-${index}`}>
          <BlockMath math={blockMatch[1].trim()} />
        </div>,
      )
      return
    }

    if (line === '***') {
      flushTextBuffer(index)
      return
    }

    if (hebrewSubItemLinePattern.test(line)) {
      flushTextBuffer(index)
    }

    textBuffer.push(line)
  })

  flushTextBuffer(rawLines.length)

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

const ThemeIconMoon = () => (
  <svg
    className="theme-toggle-icon"
    viewBox="0 0 24 24"
    width="22"
    height="22"
    aria-hidden="true"
    focusable="false"
  >
    <path
      d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

const ThemeIconSun = () => (
  <svg
    className="theme-toggle-icon"
    viewBox="0 0 24 24"
    width="22"
    height="22"
    aria-hidden="true"
    focusable="false"
  >
    <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" strokeWidth="2" />
    <path
      d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
)

function App() {
  const initialNav = getInitialNavigation()
  const [openChapterId, setOpenChapterId] = useState(initialNav.openChapterId)

  const subtopicEntryByChapter = useMemo(() => {
    const map = {}
    for (const [chapterId, source] of Object.entries(exercisesByChapter)) {
      map[chapterId] = buildSubtopicMapForSource(source)
    }
    return map
  }, [])

  const [selection, setSelection] = useState(initialNav.selection)
  const [openSolutions, setOpenSolutions] = useState({})
  const [expandAllSolutions, setExpandAllSolutions] = useState(false)
  const [colorMode, setColorMode] = useState(readStoredColorMode)
  const isNarrowViewport = useMatchMedia(MOBILE_NAV_MEDIA)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  useLayoutEffect(() => {
    const root = document.documentElement
    root.dataset.theme = colorMode
    root.style.colorScheme = colorMode === 'dark' ? 'dark' : 'light'
    try {
      window.localStorage.setItem(COLOR_MODE_STORAGE_KEY, colorMode)
    } catch {
      /* ignore */
    }
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) {
      meta.setAttribute('content', colorMode === 'dark' ? '#171b24' : '#2f67ff')
    }
  }, [colorMode])

  const toggleColorMode = useCallback(() => {
    setColorMode((current) => (current === 'dark' ? 'light' : 'dark'))
  }, [])

  const closeMobileNav = useCallback(() => {
    setMobileNavOpen(false)
  }, [])

  useEffect(() => {
    if (!isNarrowViewport) {
      setMobileNavOpen(false)
    }
  }, [isNarrowViewport])

  useEffect(() => {
    if (!mobileNavOpen) {
      return undefined
    }
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        setMobileNavOpen(false)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [mobileNavOpen])

  useEffect(() => {
    if (!mobileNavOpen || !isNarrowViewport) {
      return undefined
    }
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [mobileNavOpen, isNarrowViewport])

  useEffect(() => {
    try {
      window.localStorage.setItem(
        LAST_PLACE_STORAGE_KEY,
        JSON.stringify({
          chapterId: selection.chapterId,
          subtopicToken: selection.subtopicToken,
        }),
      )
    } catch {
      /* ignore quota / private mode */
    }
  }, [selection.chapterId, selection.subtopicToken])

  const goToSubtopic = (chapterId, subtopicToken) => {
    setExpandAllSolutions(false)
    setOpenSolutions({})
    setSelection({ chapterId, subtopicToken })
    setMobileNavOpen(false)
  }

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
    if (expandAllSolutions && selectedSubtopic) {
      setExpandAllSolutions(false)
      const keys = selectedSubtopic.exercises.map(
        (ex) => `${selectedSubtopic.id}-${ex.id}`,
      )
      setOpenSolutions(
        Object.fromEntries(keys.map((k) => [k, k !== exerciseKey])),
      )
      return
    }
    setOpenSolutions((current) => ({
      ...current,
      [exerciseKey]: !current[exerciseKey],
    }))
  }

  const toggleExpandAllSolutions = () => {
    setExpandAllSolutions((wasAllOpen) => {
      if (wasAllOpen) {
        setOpenSolutions({})
      }
      return !wasAllOpen
    })
  }

  const mobileBarTitle = selectedSubtopic?.title ?? 'תרגול לפי נושאים'

  return (
    <div className="app-shell">
      <header className="mobile-top-bar">
        <button
          type="button"
          className="mobile-nav-toggle"
          onClick={() => setMobileNavOpen((open) => !open)}
          aria-expanded={mobileNavOpen}
          aria-controls="sidebar-panel"
        >
          {mobileNavOpen ? 'סגור' : 'נושאים'}
        </button>
        <p className="mobile-top-title">{mobileBarTitle}</p>
      </header>

      <button
        type="button"
        className={`sidebar-backdrop${mobileNavOpen ? ' is-visible' : ''}`}
        tabIndex={-1}
        aria-hidden="true"
        onClick={closeMobileNav}
      />

      <main className="content main-column" id="main-content">
        <div className="content-toolbar">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleColorMode}
            aria-label={colorMode === 'dark' ? 'עבור למצב בהיר' : 'עבור למצב כהה'}
          >
            {colorMode === 'dark' ? <ThemeIconSun /> : <ThemeIconMoon />}
          </button>
          <button
            type="button"
            className="solutions-master-toggle"
            onClick={toggleExpandAllSolutions}
            disabled={!hasSelectedSubtopicExercises}
            aria-pressed={expandAllSolutions}
          >
            {expandAllSolutions ? 'הסתר פתרונות' : 'הצג פתרונות'}
          </button>
        </div>
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
                  const isOpen =
                    expandAllSolutions || Boolean(openSolutions[exerciseKey])

                  return (
                    <li key={exerciseKey} className="exercise-card">
                      <p className="exercise-id" aria-label={`תרגיל מספר ${exercise.id}`}>
                        תרגיל {exercise.id}
                      </p>
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

      <aside
        id="sidebar-panel"
        className={`sidebar${mobileNavOpen ? ' is-mobile-open' : ''}`}
        aria-label="ניווט נושאים"
        aria-hidden={isNarrowViewport ? !mobileNavOpen : undefined}
        inert={isNarrowViewport && !mobileNavOpen ? true : undefined}
      >
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
                              goToSubtopic(chapter.id, subtopicToken)
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
    </div>
  )
}

export default App
