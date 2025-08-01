# Privacy-Preserving Machine Learning for Heuristic Optimization

## Status

PROPOSED

## Context

The Sprint Radar system currently uses hardcoded heuristics for various predictions and thresholds (lookback periods, aging thresholds, team productivity curves, etc.). While these work reasonably well, they don't adapt to team-specific patterns or improve over time. We want to introduce ML-based optimization while ensuring:

1. **Data Isolation**: One project's data never influences another's predictions
2. **Privacy**: No data leakage between teams or projects
3. **Maintainability**: Clear, self-documenting models
4. **Explainability**: Users understand why predictions are made
5. **Graceful Degradation**: System works without ML models

## Decision

We will implement a privacy-preserving ML system using:

### 1. Isolated Model Architecture

Each project gets completely isolated models stored in their own namespace:

```
~/.sprint-radar/
├── projects/
│   ├── PROJ-123/
│   │   ├── models/
│   │   │   ├── lookback_optimizer.pkl
│   │   │   ├── productivity_curve.pkl
│   │   │   └── aging_predictor.pkl
│   │   ├── feature_cache/
│   │   └── model_metadata.json
│   └── TEAM-456/
│       └── ... (completely separate)
└── shared/
    └── base_heuristics.json  # Fallback rules only
```

### 2. Local-Only Learning

All ML happens locally on the user's machine:
- No data ever leaves the project's environment
- Models train on historical data from that project only
- No centralized model server or data collection

### 3. Explainable Model Choices
Use inherently interpretable models:
- **Decision Trees**: For threshold optimization (max depth 5)
- **Linear Models**: For trend prediction with feature weights
- **Rule-Based Systems**: For complex heuristics with clear rules

Example:
```python
class ExplainableLookbackOptimizer:
    def predict_with_explanation(self, features):
        prediction = self.model.predict(features)
        
        # Return both prediction and explanation
        return {
            'lookback_sprints': prediction,
            'reasoning': {
                'velocity_stability': 'High variance detected (CV=0.45)',
                'data_recency': 'Recent process change 8 sprints ago',
                'recommendation': 'Using 8 sprints to capture current process',
                'confidence': 0.82
            }
        }
```

### 4. Feature Engineering with Privacy
Features are computed locally and never stored raw:

```python
class PrivacyPreservingFeatures:
    """Compute features without storing sensitive data"""
    
    @staticmethod
    def compute_velocity_features(sprints):
        # Return only statistical aggregates, not raw data
        return {
            'cv': std_dev / mean,  # Coefficient of variation
            'trend_strength': abs(slope) / mean,
            'autocorrelation': lag_1_correlation,
            'sprint_count': len(sprints),
            # No sprint names, dates, or absolute values
        }
```

### 5. Model Lifecycle Management

```python
class ModelLifecycle:
    def __init__(self, project_key, model_type):
        self.project_path = f"~/.sprint-radar/projects/{project_key}"
        self.model_type = model_type
        self.version = "1.0.0"
        
    def should_retrain(self):
        """Retrain monthly or after significant data changes"""
        metadata = self.load_metadata()
        
        # Transparent retraining criteria
        days_since_training = (datetime.now() - metadata['trained_at']).days
        new_data_points = self.count_new_datapoints()
        
        return (days_since_training > 30 or 
                new_data_points > metadata['training_size'] * 0.5)
    
    def train(self, data):
        """Train with full audit trail"""
        features = self.extract_features(data)
        
        # Document what the model learned
        self.model.fit(features, labels)
        self.document_model_decisions()
        self.save_with_metadata()
```

### 6. Federated Insights (Optional Future Enhancement)

If projects opt-in, we could share only model parameters (not data):

```python
class FederatedInsights:
    """Share learning without sharing data"""
    
    def export_model_insights(self):
        # Export only aggregate patterns, no raw data
        return {
            'model_type': 'lookback_optimizer',
            'performance_metrics': {
                'accuracy_improvement': 0.15,
                'common_patterns': ['high_variance_needs_fewer_sprints']
            },
            'feature_importance': {
                'velocity_cv': 0.45,
                'team_size_changes': 0.30
            }
            # No project-specific information
        }
```

## Implementation Plan

### Phase 1: Infrastructure (Week 1-2)

1. Create project-based storage system
2. Implement model versioning and metadata
3. Add feature computation pipeline
4. Create base `MLHeuristic` abstract class

### Phase 2: First Model - Lookback Optimizer (Week 3-4)
1. Implement decision tree for lookback period
2. Add explanation generation
3. Create A/B testing framework
4. Add performance monitoring

### Phase 3: Gradual Rollout (Week 5-6)
1. Start with opt-in flag: `--enable-ml-optimization`
2. Show both ML and heuristic predictions
3. Collect feedback (locally)
4. Iterate based on usage

### Phase 4: Additional Models (Week 7+)
1. Team productivity curves
2. Aging threshold optimization
3. Lead time prediction

## Example Implementation

```python
# src/domain/ml_heuristics.py
from abc import ABC, abstractmethod
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple

class MLHeuristic(ABC):
    """Base class for all ML-enhanced heuristics"""
    
    def __init__(self, project_key: str, fallback_heuristic):
        self.project_key = project_key
        self.fallback = fallback_heuristic
        self.model_path = self._get_model_path()
        self.model = self._load_or_initialize_model()
        
    def _get_model_path(self) -> Path:
        """Isolated path per project"""
        base = Path.home() / ".sprint-radar" / "projects" / self.project_key
        base.mkdir(parents=True, exist_ok=True)
        return base / "models" / f"{self.__class__.__name__}.pkl"
    
    @abstractmethod
    def extract_features(self, data: Any) -> Dict[str, float]:
        """Extract features while preserving privacy"""
        pass
    
    @abstractmethod
    def explain_prediction(self, features: Dict[str, float], 
                         prediction: Any) -> Dict[str, str]:
        """Generate human-readable explanation"""
        pass
    
    def predict(self, data: Any) -> Tuple[Any, Dict[str, str]]:
        """Make prediction with explanation"""
        try:
            if not self.has_sufficient_data(data):
                # Use fallback for cold start
                result = self.fallback(data)
                explanation = {"reason": "Insufficient data for ML model"}
                return result, explanation
                
            features = self.extract_features(data)
            prediction = self.model.predict([features])[0]
            explanation = self.explain_prediction(features, prediction)
            
            # Log for local improvement
            self._log_prediction(features, prediction)
            
            return prediction, explanation
            
        except Exception as e:
            # Graceful degradation
            logger.warning(f"ML prediction failed: {e}, using fallback")
            result = self.fallback(data)
            return result, {"reason": "ML model error, using heuristic"}
```

## Consequences

### Positive
- Each project's data remains completely isolated
- Models improve based on project-specific patterns
- Clear explanations for all predictions
- System works without ML (graceful degradation)
- No privacy or compliance concerns
- Models are auditable and versioned

### Negative
- No cross-project learning (by design)
- Requires more data per project to train effectively
- Additional complexity in the codebase
- Storage requirements for models (minimal ~10MB per project)

### Mitigations
- Start with simple models that need less data
- Provide clear documentation and examples
- Make ML opt-in initially
- Monitor model performance vs heuristics
- Regular model cleanup for inactive projects

## Security Considerations

1. **Model Poisoning**: Validate input data before training
2. **Model Extraction**: Models stored with appropriate permissions
3. **Information Leakage**: Features designed to prevent reverse engineering
4. **Access Control**: Models accessible only to authorized users

## References
- [Federated Learning: Privacy-Preserving ML](https://ai.google/research/pubs/pub45648)
- [Interpretable Machine Learning](https://christophm.github.io/interpretable-ml-book/)
- [Privacy Patterns for Analytics](https://privacypatterns.org/)