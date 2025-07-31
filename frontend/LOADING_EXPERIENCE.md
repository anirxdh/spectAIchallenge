# Enhanced Loading Experience 🎮

This enhanced loading experience provides an engaging way to keep users entertained while PDFs are being processed.

## Features

### 🔄 Cycling Tips
- **7 different informative messages** that cycle every 3 seconds
- Educational content about the parsing process
- Smooth animations between transitions

### 🎮 Mini Jumping Game
- **Chrome dinosaur-style game** appears after 10 seconds
- Use **SPACEBAR** or **UP ARROW** to jump
- Avoid red obstacles and score points
- Simple but engaging gameplay

### 🌐 Portfolio Integration
- **Prominent portfolio link** with attractive styling
- Opens in new tab
- Animated hover effects
- Purple/pink gradient styling

### ✨ Visual Enhancements
- **Animated loading spinner** with sparkle effects
- **Smooth progress bar** with gradient colors
- **Loading dots animation** at the bottom
- **Responsive design** that works on all screen sizes

## Usage

```tsx
import EnhancedLoadingExperience from '@/components/EnhancedLoadingExperience';

// Basic usage
<EnhancedLoadingExperience />

// With custom portfolio URL
<EnhancedLoadingExperience portfolioUrl="https://your-actual-portfolio.com" />
```

## Customization

### Update Portfolio URL
Change the portfolio URL in `src/app/page.tsx`:

```tsx
<EnhancedLoadingExperience portfolioUrl="https://your-actual-portfolio.com" />
```

### Modify Loading Tips
Edit the `loadingTips` array in `EnhancedLoadingExperience.tsx`:

```tsx
const loadingTips = [
  "Your custom tip 1",
  "Your custom tip 2",
  // ... add more tips
];
```

### Adjust Timing
- **Tip cycling**: Change interval in `useEffect` (currently 3 seconds)
- **Game appearance**: Modify timeout (currently 10 seconds)

```tsx
// Tip cycling speed
setInterval(() => {
  setCurrentTipIndex((prev) => (prev + 1) % loadingTips.length);
}, 3000); // Change this value

// Game appearance delay
setTimeout(() => {
  setShowGame(true);
}, 10000); // Change this value
```

## Game Controls

- **SPACEBAR** or **UP ARROW**: Jump
- **Automatic scoring**: +1 point for each obstacle avoided
- **Auto-restart**: Game resets when you start a new parsing session

## Styling

The component uses Tailwind CSS classes and follows the existing design system:
- Primary colors for interactive elements
- Muted colors for secondary text
- Card styling for game container
- Responsive spacing and typography

## Performance

- Lightweight animations using Framer Motion
- Efficient game loop with requestAnimationFrame
- Automatic cleanup of event listeners and intervals
- No impact on PDF processing performance

---

**Pro Tip**: The longer the PDF processing takes, the more features become available to keep users engaged! 🚀