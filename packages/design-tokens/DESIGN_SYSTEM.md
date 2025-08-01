# Sprint Radar Design System - Opreto Theme

## Overview

The Sprint Radar Design System is built on the Opreto brand guidelines, embodying the "Hero" archetype with professional, bold, and collaborative design principles. This system provides a comprehensive set of design tokens, components, and patterns for creating consistent, high-quality analytics reports.

## Brand Philosophy

### Hero Archetype
- **Bold Leadership**: Strong visual hierarchy with confident typography
- **Professional Excellence**: Clean, sophisticated design with attention to detail
- **Collaborative Spirit**: Approachable and inclusive visual language
- **Aspirational Vision**: Forward-thinking design that inspires confidence

## Color System

### Primary Colors

#### Teal (Primary Brand Color)
- **Primary-500**: `#03564c` - Main brand color
- **Primary-700**: `#023a33` - Dark variant for headers
- **Primary-800**: `#022d2c` - Extra dark for text
- **Primary-50**: `#e6f4f2` - Light background tint

#### Burgundy (Secondary)
- **Secondary-900**: `#6B1229` - Rich accent color
- **Secondary-700**: `#b83355` - Medium variant
- **Secondary-50**: `#fdf2f4` - Light background tint

#### Cerulean Blue (Accent)
- **Accent-500**: `#0E5473` - Professional blue accent
- **Accent-100**: `#cce7f1` - Light variant for backgrounds

### Semantic Colors

#### Success
- **Success-500**: `#00A86B` - Jade Green for positive metrics
- **Success-50**: `#e8f8f0` - Light success background

#### Warning
- **Warning-500**: `#FFA500` - Orange for caution states
- **Warning-50**: `#fff8e6` - Light warning background

#### Error
- **Error-700**: `#DC143C` - Crimson for critical states
- **Error-50**: `#fef2f2` - Light error background

### Chart Colors

Professional color palette optimized for data visualization:
1. **Primary**: `#03564c` - Teal
2. **Secondary**: `#0E5473` - Cerulean Blue
3. **Tertiary**: `#6B1229` - Burgundy
4. **Quaternary**: `#FF8C00` - Dark Orange
5. **Data Series**: Additional colors for extended data sets

## Typography

### Font Families

#### Display Font (Headings)
- **Font**: Sublima (fallback: Georgia, serif)
- **Weight**: 700 (Bold)
- **Letter Spacing**: -0.02em
- **Usage**: All major headings (H1-H3)

#### Body Font
- **Font**: Inter (fallback: system fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Line Height**: 1.7 for body text
- **Usage**: All body text, UI elements, data

### Type Scale

- **H1**: 4rem (desktop) / 3rem (mobile) - Display font
- **H2**: 3rem - Display font
- **H3**: 2rem - Display font
- **Body**: 1rem - Inter font
- **Caption**: 0.875rem - Inter font
- **Small**: 0.75rem - Inter font

## Spacing System

Consistent spacing scale based on 0.25rem (4px) base unit:
- **xs**: 0.25rem (4px)
- **sm**: 0.5rem (8px)
- **md**: 1rem (16px)
- **lg**: 2rem (32px)
- **xl**: 3rem (48px)
- **xxl**: 4rem (64px)

## Component Patterns

### Cards
- **Border**: 1px solid `gray-200`
- **Shadow**: Subtle shadow with hover state
- **Background**: White with optional gradient overlay
- **Padding**: 1.5rem (24px)
- **Border Radius**: 0.5rem (8px)

### Buttons
- **Primary**: Teal background with white text
- **Secondary**: White background with teal border
- **Padding**: 0.5rem 1rem
- **Border Radius**: 0.375rem (6px)
- **Hover**: Darker shade with shadow

### Tables
- **Header**: Gray-50 background
- **Borders**: 1px dividers between rows
- **Hover**: Teal-50 row highlight
- **Padding**: 1rem per cell

### Charts
- **Background**: Transparent
- **Grid**: Light gray with 0.5 opacity
- **Title**: Display font, 18px, Dark Teal
- **Axis Labels**: Inter font, 12px, Gray-600

## Design Elements

### Hero Pattern
- Hexagonal overlay pattern in headers
- 10% opacity white on dark backgrounds
- Represents strength and interconnectedness

### Gradients
- **Hero Gradient**: `from-teal-700 via-teal-800 to-teal-900`
- **Surface Gradient**: `from-transparent via-teal-50/20 to-transparent`
- **Overlay**: `from-white/5 to-transparent`

### Shadows
- **xs**: `0 1px 2px 0 rgba(2, 45, 44, 0.05)`
- **sm**: `0 1px 3px 0 rgba(2, 45, 44, 0.08)`
- **md**: `0 4px 8px -1px rgba(2, 45, 44, 0.12)`
- **lg**: `0 10px 15px -3px rgba(2, 45, 44, 0.15)`

## Interactive States

### Hover
- **Cards**: Increased shadow, slight elevation
- **Buttons**: Darker background, enhanced shadow
- **Links**: Underline animation
- **Tables**: Row highlight with teal tint

### Focus
- **Outline**: 2px solid teal-500
- **Offset**: 2px
- **Border Radius**: Matches element

### Active
- **Background**: Darker shade of primary color
- **Shadow**: Inner shadow for pressed effect

## Accessibility

### Color Contrast
- All text meets WCAG AA standards
- Primary text on white: 14.7:1 ratio
- White text on teal-700: 7.2:1 ratio

### Focus Indicators
- Visible focus rings on all interactive elements
- High contrast focus states
- Keyboard navigation support

### Typography
- Minimum 16px font size for body text
- Clear hierarchy with distinct heading sizes
- Adequate line height for readability

## Implementation

### CSS Variables
```css
:root {
  --color-primary: #03564c;
  --color-secondary: #0E5473;
  --color-accent: #6B1229;
  --color-success: #00A86B;
  --color-warning: #FFA500;
  --color-danger: #DC143C;
}
```

### Component Classes
- `.font-display` - Apply display font
- `.font-sans` - Apply body font
- `.card` - Card component styling
- `.btn-primary` - Primary button
- `.table` - Table component

## Usage Guidelines

### When to Use Display Font
- Page titles and major section headings
- Report titles
- Key metric labels

### When to Use Body Font
- All paragraph text
- Data values
- UI labels and controls
- Table content

### Color Application
- **Teal**: Primary actions, headers, key metrics
- **Burgundy**: Secondary accents, special highlights
- **Cerulean**: Supporting information, links
- **Semantic Colors**: Status indicators only

## Version History

### v1.0.0 (Current)
- Initial Opreto theme implementation
- Complete color system alignment
- Typography system with Sublima/Inter
- Professional component styling
- Hero archetype design elements