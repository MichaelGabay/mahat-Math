import katex from 'katex'
import { useLayoutEffect, useRef } from 'react'

const renderOpts = (displayMode) => ({
  displayMode,
  throwOnError: false,
  strict: 'ignore',
  trust: false,
})

/**
 * KaTeX ישירות על DOM (בלי dangerouslySetInnerHTML דרך react-katex).
 * עוזר ב־RTL / WebKit / Netlify כשמזריקים HTML פנימה מתנהג אחרת.
 */
export function KatexBlock({ math }) {
  const ref = useRef(null)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) {
      return undefined
    }
    el.replaceChildren()
    const s = math == null ? '' : String(math).trim()
    if (s === '') {
      return undefined
    }
    try {
      katex.render(s, el, renderOpts(true))
    } catch {
      el.textContent = s
    }
    return () => {
      el.replaceChildren()
    }
  }, [math])

  return (
    <bdi className="katex-mount katex-mount--block" dir="ltr" lang="en">
      <div ref={ref} className="katex-mount-inner" />
    </bdi>
  )
}

export function KatexInline({ math }) {
  const ref = useRef(null)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) {
      return undefined
    }
    el.replaceChildren()
    const s = math == null ? '' : String(math).trim()
    if (s === '') {
      return undefined
    }
    try {
      katex.render(s, el, renderOpts(false))
    } catch {
      el.textContent = s
    }
    return () => {
      el.replaceChildren()
    }
  }, [math])

  return (
    <bdi className="katex-mount katex-mount--inline" dir="ltr" lang="en">
      <span ref={ref} className="katex-mount-inner" />
    </bdi>
  )
}
