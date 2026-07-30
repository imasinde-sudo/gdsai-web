# Brand fonts

The `@iLabAfrica Centre Brand Identity Guidelines` specify four typeface roles:

| Role | Typeface | Licence | Status |
| :--- | :--- | :--- | :--- |
| Primary | Frutiger LT Std | Commercial (Linotype/Monotype) | **not bundled** — drop files here |
| Secondary | Gotham | Commercial (Hoefler&Co) | not bundled |
| Secondary | Montserrat | SIL Open Font Licence | loaded from Google Fonts |
| Document | Times New Roman | System font | available on all target platforms |
| Logo | Sansation Bold | Free for personal/commercial use | **not bundled** — drop files here |

Frutiger, Gotham and Sansation cannot be redistributed through a public CDN,
so the stylesheet resolves them through `local()` first and then a self-hosted
path in this directory. Until licensed files are added, the browser falls
through to Montserrat, which the handbook approves as a secondary face.

## Adding the licensed files

Convert the licensed desktop or web kits to WOFF2 and place them here using
exactly these filenames — `core/static/css/styles.css` already points at them,
so no code change is needed:

```
core/static/fonts/
  FrutigerLTStd-Light.woff2
  FrutigerLTStd-Roman.woff2
  FrutigerLTStd-Bold.woff2
  Sansation-Bold.woff2
  Sansation-BoldItalic.woff2
```

Then run `python manage.py collectstatic` so the files are served in production.

Sansation is used **only** for the logo lockup
(`events/partials/brand_logo.html`). It must never be applied to headings or
body copy.
