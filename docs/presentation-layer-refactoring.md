# Presentation Layer Refactoring Documentation

## Overview

This document describes the comprehensive refactoring of the Sprint Radar presentation layer to follow Clean Architecture principles and improve maintainability.

## Refactoring Goals

1. **Separation of Concerns**: Extract templates, styles, and JavaScript from Python code
2. **Clean Architecture**: Implement proper layer boundaries and dependency inversion
3. **Maintainability**: Break down monolithic code into focused, testable components
4. **Developer Experience**: Enable proper IDE support for HTML/CSS/JS editing
5. **Backward Compatibility**: Ensure existing functionality continues to work during migration

## Phase 1: Template Extraction ✅

### What Was Done

1. **Created new directory structure**:
```
src/presentation/
├── templates/
│   ├── base/
│   │   └── layout.html              # Base HTML template with Jinja2 blocks
│   └── reports/
│       ├── single_project.html      # Single project report (extends base)
│       ├── single_project_content.html  # Content-only version for backward compatibility
│       ├── multi_project.html       # Multi-project dashboard (extends base)
│       └── multi_project_content.html   # Content-only version
├── static/
│   ├── css/
│   │   └── base.css                 # Base styles with CSS variables
│   └── js/
│       ├── scenario-switcher.js     # Scenario switching functionality
│       └── charts.js                # Chart initialization and handling
└── services/
    └── template_service.py          # Template loading and rendering service
```

2. **Extracted embedded content**:
- Moved 1,000+ lines of HTML from `templates.py` to separate template files
- Extracted 400+ lines of JavaScript to dedicated JS files
- Created base CSS file with CSS custom properties for theming
- Maintained dynamic CSS generation from theme objects

3. **Created template service** (`template_service.py`):
- Jinja2-based template loading from filesystem
- Template caching for performance
- Support for template inheritance
- Backward-compatible interface

4. **Backward compatibility** (`templates_refactored.py`):
- Feature flag: `USE_FILE_BASED_TEMPLATES` environment variable
- Wrapper classes that maintain the existing API
- Gradual migration path without breaking changes

### Benefits Achieved

- **IDE Support**: Full syntax highlighting and validation for HTML/CSS/JS
- **Maintainability**: Templates can be edited without touching Python code
- **Performance**: Template caching reduces parsing overhead
- **Reusability**: Template inheritance reduces duplication

## Phase 2: CLI Decomposition ✅

### What Was Done

1. **Created command pattern architecture**:
```
src/presentation/cli_new/    # Renamed from 'cli' to avoid naming conflict with cli.py
├── commands/
│   ├── base.py              # Command interface and base classes
│   ├── import_data.py       # Import data from CSV/API sources
│   ├── forecast.py          # Run Monte Carlo simulations
│   └── report.py            # Generate HTML reports
├── orchestrators/
│   └── main_orchestrator.py # Workflow orchestration
├── container.py             # Dependency injection container
└── __init__.py
```

> **Note**: The directory was renamed from `cli/` to `cli_new/` to avoid Python module resolution conflicts with the existing `cli.py` file.

2. **Decomposed monolithic cli.py** (1,111 lines → modular components):

### Command Pattern Implementation

#### Base Command Interface (`commands/base.py`)
- `Command`: Abstract base class for all commands
- `CommandContext`: Contains args, config, and dependencies
- `CommandResult`: Standardized response object
- `CompositeCommand`: Compose multiple commands

#### ImportDataCommand (`commands/import_data.py`)
- Handles data import from CSV and API sources
- Auto-detection of data source type
- Field mapping configuration
- Multi-project support preparation

#### ForecastCommand (`commands/forecast.py`)
- Executes Monte Carlo simulations
- Velocity calculation and analysis
- Configurable confidence levels
- Scenario support preparation

#### ReportCommand (`commands/report.py`)
- Generates HTML reports
- Process health metrics analysis
- Chart data preparation
- Theme and styling support

### Dependency Injection Container (`container.py`)

Manages all dependencies:
- **Repositories**: Issue, Sprint, Config repositories
- **Factories**: DataSource, Model factories
- **Services**: Style service with theme support
- **Use Cases**: All application layer use cases
- **Generators**: Report generators

### Command Orchestrator (`orchestrators/main_orchestrator.py`)

Coordinates command execution:
- Full workflow orchestration (import → forecast → report)
- Individual command execution
- Multi-project workflow support
- Scenario comparison workflow

### Refactored CLI Entry Point (`cli_refactored.py`)

- Maintains same CLI interface
- Uses orchestrator for command execution
- Feature flag: `USE_REFACTORED_CLI` for gradual migration
- All existing command-line options preserved

## Architecture Improvements

### Before (Monolithic)
```
cli.py (1,111 lines)
├── Argument parsing
├── Data import logic
├── CSV analysis
├── Velocity calculation
├── Monte Carlo simulation
├── Report generation
├── Process health analysis
└── Multi-project handling
```

### After (Modular)
```
CLI Layer (Presentation)
├── Commands (focused responsibilities)
├── Orchestrator (workflow coordination)
└── Container (dependency management)
    ↓
Application Layer (Use Cases)
    ↓
Domain Layer (Entities, Value Objects)
    ↓
Infrastructure Layer (Repositories, External Services)
```

## Benefits Achieved

1. **Separation of Concerns**
   - Each command has a single, clear responsibility
   - Business logic separated from presentation logic
   - Clean layer boundaries

2. **Testability**
   - Commands can be tested in isolation
   - Mock dependencies through container
   - No need for complex integration tests

3. **Maintainability**
   - Easy to add new commands
   - Clear dependency management
   - Modular, focused components

4. **Extensibility**
   - New commands can be added without modifying existing code
   - Plugin architecture ready
   - Easy to add new workflows

## Migration Guide

### Using the Refactored Templates

1. Enable file-based templates:
```bash
export USE_FILE_BASED_TEMPLATES=true
```

2. Templates are now in `src/presentation/templates/`
3. Static files are in `src/presentation/static/`
4. Edit templates directly with full IDE support

### Using the Refactored CLI

1. Enable refactored CLI:
```bash
export USE_REFACTORED_CLI=true
```

2. All existing command-line options work the same
3. Same output and functionality
4. Better error handling and logging

### For Developers

1. **Adding a new command**:
   - Create new command class extending `Command`
   - Implement `execute()` method
   - Register in orchestrator
   - Add dependencies to container

2. **Adding a new template**:
   - Create template in appropriate directory
   - Use Jinja2 template inheritance
   - Access via `TemplateService`

3. **Modifying styles**:
   - Edit `static/css/base.css` for static styles
   - Use `StyleGenerator` for dynamic theme-based styles
   - CSS variables for theming

## Phase 3: Clean Architecture Adapters ✅

### What Was Done

1. **Created presentation layer models**:
```
src/presentation/models/
├── requests.py      # Request DTOs for presentation layer
├── responses.py     # Response DTOs with validation
└── view_models.py   # View models optimized for rendering
```

2. **Implemented controllers** for presentation logic:
```
src/presentation/controllers/
├── base.py              # Base controller with common functionality
├── import_controller.py # Handles data import operations
├── forecast_controller.py # Manages forecast generation
└── report_controller.py   # Controls report generation
```

3. **Created comprehensive mapper system**:
```
src/presentation/mappers/
├── view_model_mapper.py    # Maps domain entities to view models
├── chart_mapper.py         # Creates chart view models from data
├── request_response_mapper.py # Converts between DTOs
├── entity_mapper.py        # Maps domain entities to presentation formats
└── presentation_mapper.py  # Aggregated mapper coordinating all mappings
```

### Key Components

#### Request/Response Models
- `ImportDataRequest`: Encapsulates import parameters
- `ForecastRequest`: Forecast generation parameters
- `ReportRequest`: Report configuration and preferences
- Corresponding response models with validation

#### View Models
- `MetricCardViewModel`: Key metrics display
- `ChartViewModel`: Plotly chart configuration
- `TableRowViewModel`: Table data representation
- `HealthScoreViewModel`: Process health visualization
- `ReportViewModel`: Complete report structure
- `DashboardViewModel`: Multi-project dashboard

#### Controllers
- Implement Clean Architecture boundaries
- Convert between presentation and application layers
- Handle validation and error responses
- Maintain separation of concerns

## Phase 4: Component Architecture ✅

### What Was Done

1. **Created component system**:
```
src/presentation/components/
├── base.py          # Component base classes
├── header.py        # Header component with navigation
├── footer.py        # Footer with metadata
├── metric_card.py   # Metric card and grid components
├── chart.py         # Chart and chart grid components
└── table.py         # Table and summary table components
```

2. **Component Features**:
- Template-based rendering with Jinja2
- Component-specific styles
- Composable architecture
- View model integration
- Responsive design

### Component Architecture

#### Base Component System
- `Component`: Abstract base for all components
- `CompositeComponent`: For components containing other components
- Template rendering with context data
- Component-specific CSS and JavaScript

#### Implemented Components
1. **HeaderComponent**: Report header with metadata and navigation
2. **FooterComponent**: Footer with methodology and links
3. **MetricCardComponent**: Key metric display cards
4. **MetricCardGridComponent**: Responsive grid of metric cards
5. **ChartComponent**: Plotly chart wrapper with insights
6. **ChartGridComponent**: Multi-chart layout
7. **TableComponent**: Data table with styling options
8. **SummaryTableComponent**: Specialized forecast summary table

### Benefits Achieved
- **Reusability**: Components can be used across different reports
- **Maintainability**: Each component is self-contained
- **Testability**: Components can be tested in isolation
- **Consistency**: Unified styling and behavior
- **Performance**: Component-level optimization

## Future Improvements

### Phase 5: Integration and Migration (Planned)
- Create integration tests for refactored code
- Update existing code to use new architecture
- Remove deprecated code paths
- Complete migration documentation

## Testing

The refactoring maintains backward compatibility:
- Original `cli.py` continues to work
- Feature flags allow gradual migration
- All existing functionality preserved
- Comprehensive test coverage added

## Summary

The presentation layer refactoring successfully completed four major phases:

### Completed Achievements
- ✅ **Phase 1**: Extracted 1,000+ lines of embedded templates to separate files
- ✅ **Phase 2**: Broke down 1,111-line monolithic CLI into modular commands
- ✅ **Phase 3**: Implemented Clean Architecture with DTOs, controllers, and mappers
- ✅ **Phase 4**: Created reusable component architecture with 8 specialized components

### Technical Improvements
- ✅ Proper separation of concerns across all layers
- ✅ Dependency injection container for better testability
- ✅ Command pattern architecture for CLI operations
- ✅ View models optimized for rendering
- ✅ Comprehensive mapper system for data transformation
- ✅ Component-based UI architecture
- ✅ Full backward compatibility maintained
- ✅ Improved developer experience with IDE support

### Architecture Benefits
- **Clean Architecture**: Clear boundaries between presentation, application, and domain layers
- **Maintainability**: Modular components that can be modified independently
- **Testability**: Each component can be tested in isolation
- **Reusability**: Components and mappers can be reused across different contexts
- **Performance**: Template caching and optimized rendering
- **Flexibility**: Easy to add new commands, components, or view models

The refactoring provides a solid foundation for future enhancements while maintaining all existing functionality. The presentation layer is now well-structured, maintainable, and follows industry best practices.