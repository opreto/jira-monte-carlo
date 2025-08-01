import * as React from 'react'
import { cn } from '../../lib/utils'

// Container component
export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ className, size = 'lg', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'mx-auto w-full px-4 sm:px-6 lg:px-8',
          {
            'max-w-3xl': size === 'sm',
            'max-w-5xl': size === 'md',
            'max-w-7xl': size === 'lg',
            'max-w-[90rem]': size === 'xl',
            'max-w-none': size === 'full',
          },
          className
        )}
        {...props}
      />
    )
  }
)
Container.displayName = 'Container'

// Header component
export interface HeaderProps extends React.HTMLAttributes<HTMLElement> {
  sticky?: boolean
}

const Header = React.forwardRef<HTMLElement, HeaderProps>(
  ({ className, sticky = false, children, ...props }, ref) => {
    return (
      <header
        ref={ref}
        className={cn(
          'w-full border-b border-gray-200 bg-white',
          {
            'sticky top-0 z-50': sticky,
          },
          className
        )}
        {...props}
      >
        <Container>
          <div className="flex h-16 items-center justify-between">{children}</div>
        </Container>
      </header>
    )
  }
)
Header.displayName = 'Header'

// HeaderLogo component
export interface HeaderLogoProps extends React.HTMLAttributes<HTMLDivElement> {
  href?: string
}

const HeaderLogo = React.forwardRef<HTMLDivElement, HeaderLogoProps>(
  ({ className, children, href, ...props }, ref) => {
    const content = (
      <div
        className={cn('flex items-center gap-2 font-semibold text-gray-900', className)}
        {...props}
      >
        {children}
      </div>
    )

    if (href) {
      return (
        <a href={href} className="no-underline" ref={ref as any}>
          {content}
        </a>
      )
    }

    return <div ref={ref}>{content}</div>
  }
)
HeaderLogo.displayName = 'HeaderLogo'

// HeaderNav component
export interface HeaderNavProps extends React.HTMLAttributes<HTMLElement> {}

const HeaderNav = React.forwardRef<HTMLElement, HeaderNavProps>(
  ({ className, ...props }, ref) => {
    return (
      <nav
        ref={ref}
        className={cn('flex items-center gap-6', className)}
        {...props}
      />
    )
  }
)
HeaderNav.displayName = 'HeaderNav'

// HeaderActions component
export interface HeaderActionsProps extends React.HTMLAttributes<HTMLDivElement> {}

const HeaderActions = React.forwardRef<HTMLDivElement, HeaderActionsProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center gap-4', className)}
        {...props}
      />
    )
  }
)
HeaderActions.displayName = 'HeaderActions'

// Footer component
export interface FooterProps extends React.HTMLAttributes<HTMLElement> {}

const Footer = React.forwardRef<HTMLElement, FooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <footer
        ref={ref}
        className={cn(
          'mt-auto w-full border-t border-gray-200 bg-white',
          className
        )}
        {...props}
      >
        <Container>
          <div className="py-8">{children}</div>
        </Container>
      </footer>
    )
  }
)
Footer.displayName = 'Footer'

// FooterSection component
export interface FooterSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
}

const FooterSection = React.forwardRef<HTMLDivElement, FooterSectionProps>(
  ({ className, title, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('space-y-3', className)} {...props}>
        {title && (
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        )}
        <div className="space-y-2 text-sm text-gray-600">{children}</div>
      </div>
    )
  }
)
FooterSection.displayName = 'FooterSection'

// Main layout component
export interface MainProps extends React.HTMLAttributes<HTMLElement> {}

const Main = React.forwardRef<HTMLElement, MainProps>(
  ({ className, ...props }, ref) => {
    return (
      <main
        ref={ref}
        className={cn('flex-1', className)}
        {...props}
      />
    )
  }
)
Main.displayName = 'Main'

// PageLayout component - combines header, main, footer
export interface PageLayoutProps extends React.HTMLAttributes<HTMLDivElement> {}

const PageLayout = React.forwardRef<HTMLDivElement, PageLayoutProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex min-h-screen flex-col', className)}
        {...props}
      />
    )
  }
)
PageLayout.displayName = 'PageLayout'

// Section component for page sections
export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  spacing?: 'sm' | 'md' | 'lg' | 'xl'
}

const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ className, spacing = 'lg', ...props }, ref) => {
    return (
      <section
        ref={ref}
        className={cn(
          {
            'py-4 sm:py-6': spacing === 'sm',
            'py-8 sm:py-12': spacing === 'md',
            'py-12 sm:py-16 lg:py-20': spacing === 'lg',
            'py-16 sm:py-20 lg:py-24': spacing === 'xl',
          },
          className
        )}
        {...props}
      />
    )
  }
)
Section.displayName = 'Section'

// Grid component for responsive layouts
export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 6 | 12
  gap?: 'sm' | 'md' | 'lg'
}

const Grid = React.forwardRef<HTMLDivElement, GridProps>(
  ({ className, cols = 1, gap = 'md', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'grid',
          {
            'grid-cols-1': cols === 1,
            'grid-cols-1 sm:grid-cols-2': cols === 2,
            'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': cols === 3,
            'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4': cols === 4,
            'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6': cols === 6,
            'grid-cols-3 sm:grid-cols-6 lg:grid-cols-12': cols === 12,
          },
          {
            'gap-2': gap === 'sm',
            'gap-4': gap === 'md',
            'gap-6 lg:gap-8': gap === 'lg',
          },
          className
        )}
        {...props}
      />
    )
  }
)
Grid.displayName = 'Grid'

export {
  Container,
  Header,
  HeaderLogo,
  HeaderNav,
  HeaderActions,
  Footer,
  FooterSection,
  Main,
  PageLayout,
  Section,
  Grid,
}