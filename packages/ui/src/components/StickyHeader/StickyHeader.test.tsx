import * as React from 'react'
import { render, screen } from '@testing-library/react'
import { StickyHeader } from './StickyHeader'

describe('StickyHeader', () => {
  it('renders children correctly', () => {
    render(
      <StickyHeader>
        <div>Test content</div>
      </StickyHeader>
    )
    
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <StickyHeader className="custom-class">
        <div>Test</div>
      </StickyHeader>
    )
    
    const stickyElement = container.firstChild
    expect(stickyElement).toHaveClass('custom-class')
    expect(stickyElement).toHaveClass('sticky')
  })

  it('applies stickyClassName when provided', () => {
    const { container } = render(
      <StickyHeader stickyClassName="when-sticky">
        <div>Test</div>
      </StickyHeader>
    )
    
    const stickyElement = container.firstChild
    expect(stickyElement).toHaveClass('when-sticky')
  })

  it('applies custom offsetTop', () => {
    const { container } = render(
      <StickyHeader offsetTop={50}>
        <div>Test</div>
      </StickyHeader>
    )
    
    const stickyElement = container.firstChild as HTMLElement
    expect(stickyElement.style.top).toBe('50px')
  })

  it('applies custom zIndex', () => {
    const { container } = render(
      <StickyHeader zIndex={200}>
        <div>Test</div>
      </StickyHeader>
    )
    
    const stickyElement = container.firstChild as HTMLElement
    expect(stickyElement.style.zIndex).toBe('200')
  })

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLDivElement>()
    
    render(
      <StickyHeader ref={ref}>
        <div>Test</div>
      </StickyHeader>
    )
    
    expect(ref.current).toBeInstanceOf(HTMLDivElement)
  })

  it('spreads additional props', () => {
    const { container } = render(
      <StickyHeader data-testid="sticky-header" aria-label="Navigation">
        <div>Test</div>
      </StickyHeader>
    )
    
    const stickyElement = container.firstChild
    expect(stickyElement).toHaveAttribute('data-testid', 'sticky-header')
    expect(stickyElement).toHaveAttribute('aria-label', 'Navigation')
  })

  // SSR-specific test
  it('uses forwardRef pattern for SSR compatibility', () => {
    // This test ensures the component is using React.forwardRef
    // which is required for proper SSR rendering with tsup
    expect(StickyHeader.$$typeof).toBe(Symbol.for('react.forward_ref'))
    expect(StickyHeader.displayName).toBe('StickyHeader')
  })
})