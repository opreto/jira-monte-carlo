# Sprint Radar Roadmap

This document outlines the development roadmap for Sprint Radar, organized by completion status, priority, and thematic areas.

## Recently Completed ✅

### Core Features
- Monte Carlo simulation engine
- Multi-source data import (Jira, Linear, Jira XML)
- Jira API direct integration with caching
- Sprint velocity analysis with outlier detection
- Beautiful HTML reports with interactive Plotly charts
- Multi-project dashboard with drill-down reports
- Sprint names on X-axis for velocity charts
- Story size breakdown chart for remaining work

### Process Health & Analytics
- Process health metrics (aging, WIP, sprint health, blocked items, lead time)
- Health score visualization with gauges
- Clickable issue links in health breakdown reports

### Architecture & Infrastructure
- Data source abstraction layer (LADR-0001)
- Forecasting model abstraction (LADR-0002)
- Clean architecture refactoring (LADR-0003)
- Velocity change prediction system (LADR-0004)
- Plugin architecture with registry
- Themeable reports (Opreto and generic themes)

### Machine Learning & Visualization
- ML-powered lookback optimization with confidence scores
- React-based report generation with smooth animations

## In Progress 🚧

- Additional analytics for scrum masters
- Mobile-responsive report design

## Planned Features 📋

### Phase 1: Architectural Cleanup (Priority 1)

#### Python-to-JavaScript Data Pipeline
- Replace brittle kwargs-based data passing between Python reporting layer and React/JS layer
- Design a type-safe, versioned data contract between backend and frontend
- Implement proper serialization/deserialization with validation
- Consider using Protocol Buffers or JSON Schema for data structure definition
- Ensure backward compatibility during migration

### Phase 2: Mobile Experience (Priority 2)

#### Responsive Design
- Implement responsive chart rendering
- Create mobile-optimized templates
- Add server-side rendering for complex visualizations
- Support touch gestures for chart interaction
- Optimize data transfer for mobile networks
- Progressive web app (PWA) capabilities

### Phase 3: Architecture Improvements (Priority 3)

#### Performance Optimizations
- Parallel CSV processing for multi-file imports
- Caching for large datasets beyond API responses
- Incremental report updates

#### Dependency Injection Refinement
- Complete DI container implementation
- Remove remaining static dependencies
- Improve testability with better mocking

#### Cross-Platform Issue Link Service
- Abstract issue URL construction into a dedicated service
- Support multiple project management platforms (Jira, Linear, GitHub Issues, etc.)
- Configurable URL patterns per platform
- Auto-detect platform from issue key format
- Enable deep linking to issues across different tools

### Phase 4: Work Classification System

#### Opreto Work Type Methodology
- Implement 7-type classification:
  - New Functionality (50-60% target)
  - Technical Debt (15-20% target)
  - Maintenance & Support (~10% target)
  - Research & Spikes (5-10% target)
  - Experience Work (5-10% target)
  - Platform/Infrastructure (5-10% target)
  - Process & Quality (flexible)
- Work type distribution reports
- Alerts for allocation imbalances
- Historical trend analysis by work type

## Feature Areas

### Analytics & Metrics

#### Sprint Health Metrics
- Sprint burndown charts
- Sprint completion rate tracking
- Sprint predictability metrics (variance/std dev)
- Commitment vs delivery analysis

#### Flow Metrics
- Cycle time distribution histogram
- Lead time analysis
- Work In Progress (WIP) visualization
- Throughput trends (items/week)
- Flow efficiency calculations

#### Team Health Metrics
- Team-level estimation accuracy
- Sprint commitment reliability (team aggregate)
- Quality metrics (bug vs feature ratio)
- Technical debt trends

#### Process Health Indicators
- Aging work items report (team level)
- Blocked items tracking with duration
- Unestimated items in backlog
- Sprint scope changes
- Dependency bottlenecks

#### Forecasting Enhancements
- Best/worst case scenario visualization
- Release burnup charts
- Feature/epic completion forecasts
- Scope change impact analysis
- What-if scenario modeling

#### Portfolio/Program Level
- Cross-team dependency visualization
- Program Increment (PI) progress (SAFe)
- Epic progress rollups
- Team capacity planning
- Portfolio health dashboard

### Integrations

#### Git Repository Integration
- Repository analyzer interface design
- Git client abstraction (GitHub, GitLab, Bitbucket)
- Commit frequency and size metrics
- Branch lifetime analysis
- Code ownership mapping
- PR review engagement
- Test coverage trends
- Integration with issue tracking

#### Data Source Expansion
- Azure DevOps integration
- GitHub Issues integration
- Trello integration
- Monday.com integration

### Opreto-Specific Features

#### Architect Dashboard
- Weekly architect overview
- Definition of Done compliance
- Team velocity by member
- Blockers requiring escalation
- Time tracking anomalies
- Executive sprint summaries
- Technical maturity scoring
- LADR compliance tracking

#### Team Intelligence
- Onboarding effectiveness metrics
- 30/60/90 day velocity curves
- Pairing frequency analysis
- Team composition optimization
- Skills gap identification

### Technical Improvements

#### Performance & Scalability
- Streaming processing for very large files
- Distributed simulation runs
- Real-time progress updates

#### Export Capabilities
- PDF report generation
- Excel export with raw data
- PowerPoint presentation mode
- Slack/Teams integration

#### Advanced Modeling
- PERT estimation model
- Bayesian forecasting
- Machine learning predictions
- Seasonal adjustment models

### User Experience

#### Interactive Dashboards
- Real-time filtering
- Drill-down capabilities
- Custom date ranges
- Saved view configurations

#### Customization
- Custom metrics definition
- Configurable workflows
- Theme builder
- Report templates

## Future Vision 🚀

### Long-term Strategic Goals
- SaaS offering with team collaboration
- Real-time Jira webhook integration
- AI-powered insights and recommendations
- Native mobile apps for iOS/Android
- ML-powered velocity predictions
- Technical debt accumulation forecasting
- Risk prediction based on patterns
- Client value demonstration tools

## Contributing

For new features or changes:
1. Check this roadmap for alignment with project direction
2. Create a feature branch in this repository
3. Write comprehensive tests for new functionality
4. Ensure all tests pass
5. Submit a pull request for review

For architectural changes, please document your decisions in a LADR (Lightweight Architecture Decision Record) in the `docs/architecture` directory.