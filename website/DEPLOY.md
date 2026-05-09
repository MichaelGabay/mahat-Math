# בנייה ופריסה (חינם)

האתר הוא **React + Vite** — אחרי `npm run build` נוצרת תיקייה סטטית `dist` (HTML, JS, CSS, תמונות). אין שרת יישומים, ולכן **עשרות משתמשים במקביל** לא מעמיסים על שום מכונה אחת: קבצים מוגשים מ־**CDN** של ספק האירוח.

## פריסה מומלצת (מהירה ובחינם)

1. **Cloudflare Pages** — טירת חינם חזקה, CDN גלובלי, התאמה מצוינת לקבצים סטטיים.  
   - חיבור ל־GitHub/GitLab  
   - **Root directory:** `website`  
   - **Build command:** `npm ci && npm run build`  
   - **Build output directory:** `dist`

2. **Vercel** — חיבור לריפו, אותן הגדרות (`website`, `npm run build`, פלט `dist`).

3. **Netlify** — ניתן לפרוס בלי הגדרות נוספות אם משתמשים ב־`netlify.toml` בתיקיית `website`.

לפני פריסה מקומית:

```bash
cd website
npm ci
npm run build
npx vite preview
```

## הערות למניעת "באגים" בפרודקשן

- אין כאן React Router — כל הנתיבים הם `/`, ולכן **אין צורך בכללי SPA redirect** אלא אם תוסיפו ניתוב לפי URL בעתיד.
- אם בעתיד תפרסו תחת **תת־נתיב** (למשל `example.com/math/`), יש להגדיר ב־`vite.config.js` את `base: '/math/'` ולבנות מחדש.
- **Node.js:** בגרסאות האחרונות של Vite נדרש **Node 20.19+ או 22.12+** לבנייה מקומית וב־CI. ב־Cloudflare/Vercel/Netlify הגדירו גרסת Node מעודכנת (למשל 22 LTS).
