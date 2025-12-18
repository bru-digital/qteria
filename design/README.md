# Design Assets

This directory contains design source files and brand assets for Qteria.

## Directory Structure

- `logos/` - Logo files and variations
  - `logo.xcf` - GIMP source file (editable)
  - Production logo: `apps/web/public/logo.png`

## Logo Usage

The production logo is located at `apps/web/public/logo.png` and is web-accessible via Next.js at `/logo.png`.

To use the logo in the app:

```tsx
import Image from 'next/image'
;<Image src="/logo.png" alt="Qteria" width={200} height={50} />
```

## Editing Logo

1. Open `logos/logo.xcf` in GIMP
2. Make your changes
3. Export as PNG to `apps/web/public/logo.png`
4. Optimize the PNG if needed:
   ```bash
   # Using ImageOptim, OptiPNG, or similar tools
   optipng apps/web/public/logo.png
   ```

## Brand Guidelines

For comprehensive brand guidelines including colors, typography, and usage rules, see `product-guidelines/05-brand-strategy.md` and `product-guidelines/06-design-system.md`.
