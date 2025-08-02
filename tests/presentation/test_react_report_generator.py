"""Tests for React report generator, including chart data merging"""

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.presentation.react_report_generator import ReactReportGenerator
from src.domain.entities import SimulationConfig, SimulationResult
from src.domain.value_objects import VelocityMetrics, HistoricalData


class TestReactReportGenerator:
    """Test suite for React report generator"""

    @pytest.fixture
    def generator(self):
        """Create a React report generator instance"""
        with patch.object(ReactReportGenerator, '_find_report_builder') as mock_find:
            mock_find.return_value = Path('/fake/path')
            return ReactReportGenerator()

    @pytest.fixture
    def mock_data(self):
        """Create mock data for testing"""
        from datetime import datetime
        
        simulation_result = SimulationResult(
            percentiles={0.5: 5, 0.7: 6, 0.85: 7, 0.95: 8},
            mean_completion_date=datetime(2025, 10, 1),
            std_dev_days=14.0,
            probability_distribution=[0.1, 0.2, 0.4, 0.2, 0.1],
            completion_dates=[datetime(2025, 9, 15), datetime(2025, 10, 1), datetime(2025, 10, 15)],
            confidence_intervals={0.5: (4, 6), 0.85: (6, 8)},
            completion_sprints=[5, 6, 7, 8]
        )
        
        velocity_metrics = VelocityMetrics(
            average=30.0,
            median=28.0,
            std_dev=5.0,
            min_value=20.0,
            max_value=40.0,
            trend=0.5
        )
        
        historical_data = HistoricalData(
            velocities=[25, 30, 35],
            cycle_times=[5.0, 7.0, 6.0],
            throughput=[10, 12, 15],
            dates=[],
            sprint_names=['Sprint 1', 'Sprint 2', 'Sprint 3']
        )
        
        config = SimulationConfig(num_simulations=1000)
        
        return {
            'simulation_results': simulation_result,
            'velocity_metrics': velocity_metrics,
            'historical_data': historical_data,
            'config': config,
            'remaining_work': 100.0
        }

    def test_prepare_report_data_basic(self, generator, mock_data):
        """Test basic report data preparation"""
        report_data = generator._prepare_report_data(**mock_data)
        
        assert report_data['remainingWork'] == 100.0
        assert report_data['velocityMetrics']['average'] == 30.0
        assert len(report_data['sprints']) == 3
        assert report_data['simulationResults']['percentiles']['0.5'] == 5

    def test_charts_data_merging(self, generator, mock_data):
        """Test that health charts are properly merged with scenario charts"""
        # Add health charts data
        charts_data = {
            'velocity_trend': {'data': [], 'layout': {}},
            'aging_distribution': {'data': [], 'layout': {}},
            'aging_by_status': {'data': [], 'layout': {}},
            'wip_by_status': {'data': [], 'layout': {}},
            'sprint_completion_trend': {'data': [], 'layout': {}},
            'sprint_scope_changes': {'data': [], 'layout': {}}
        }
        
        # Add scenario-specific charts
        baseline_charts = {
            'probability_distribution': {'data': [], 'layout': {}},
            'forecast_timeline': {'data': [], 'layout': {}},
            'confidence_intervals': {'data': [], 'layout': {}}
        }
        
        adjusted_charts = {
            'probability_distribution': {'data': [], 'layout': {}},
            'forecast_timeline': {'data': [], 'layout': {}},
            'confidence_intervals': {'data': [], 'layout': {}}
        }
        
        # Prepare report data with all charts
        mock_data['charts_data'] = charts_data
        mock_data['baseline_charts_data'] = baseline_charts
        mock_data['adjusted_charts_data'] = adjusted_charts
        mock_data['combined_scenario_data'] = json.dumps({
            'baseline': {},
            'adjusted': {},
            'current_view': 'adjusted'
        })
        
        report_data = generator._prepare_report_data(**mock_data)
        
        # Verify initial charts include health charts
        assert 'velocity_trend' in report_data['charts']
        assert 'aging_distribution' in report_data['charts']
        assert 'probability_distribution' in report_data['charts']
        
        # Verify scenario charts include both health and scenario-specific charts
        assert 'scenarioCharts' in report_data
        assert 'velocity_trend' in report_data['scenarioCharts']['baseline']
        assert 'probability_distribution' in report_data['scenarioCharts']['baseline']
        assert 'velocity_trend' in report_data['scenarioCharts']['adjusted']
        assert 'probability_distribution' in report_data['scenarioCharts']['adjusted']

    def test_charts_data_without_scenarios(self, generator, mock_data):
        """Test chart handling without scenario data"""
        charts_data = {
            'velocity_trend': {'data': [], 'layout': {}},
            'health_score_gauge': {'data': [], 'layout': {}}
        }
        
        mock_data['charts_data'] = charts_data
        report_data = generator._prepare_report_data(**mock_data)
        
        # Should use charts_data directly when no scenarios
        assert report_data['charts'] == charts_data
        assert 'scenarioCharts' not in report_data

    def test_process_health_metrics_handling(self, generator, mock_data):
        """Test process health metrics are properly serialized"""
        process_health = Mock()
        process_health.health_score = 0.75
        process_health.wip_score = 0.8
        process_health.sprint_health_score = 0.9
        process_health.flow_efficiency_score = 0.7
        process_health.lead_time_score = 0.6
        process_health.defect_rate_score = 0.85
        process_health.blocked_items_score = 0.95
        
        # Add health breakdown
        breakdown_component = Mock()
        breakdown_component.name = "Test Component"
        breakdown_component.score = 0.8
        breakdown_component.description = "Test description"
        breakdown_component.insights = ["Insight 1", "Insight 2"]
        breakdown_component.recommendations = ["Rec 1", "Rec 2"]
        breakdown_component.detail_items = []
        
        process_health.health_score_breakdown = [breakdown_component]
        process_health.aging_analysis = None
        process_health.wip_analysis = None
        process_health.sprint_health = None
        process_health.blocked_items = None
        
        mock_data['process_health_metrics'] = process_health
        report_data = generator._prepare_report_data(**mock_data)
        
        assert report_data['processHealth']['score'] == 75.0  # Converted to percentage
        assert report_data['processHealth']['wipScore'] == 0.8
        assert len(report_data['processHealth']['health_score_breakdown']) == 1
        assert report_data['processHealth']['health_score_breakdown'][0]['name'] == "Test Component"

    @patch('subprocess.run')
    def test_generate_calls_node_builder(self, mock_run, generator, mock_data):
        """Test that generate method properly calls Node.js builder"""
        mock_run.return_value = Mock(returncode=0, stderr='')
        
        output_path = Path('/tmp/test-report.html')
        generator.generate(
            output_path=output_path,
            **mock_data
        )
        
        # Verify subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        
        # Verify command structure
        assert 'npx' in call_args
        assert 'tsx' in call_args
        assert str(output_path) in call_args

    def test_find_report_builder_error(self):
        """Test error when report builder is not found"""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(RuntimeError, match="Report builder not found"):
                ReactReportGenerator()

    def test_ml_decisions_serialization(self, generator, mock_data):
        """Test ML decisions are properly serialized"""
        ml_decision = Mock()
        ml_decision.decision_type = 'lookback_period'
        ml_decision.method = 'auto'
        ml_decision.value = 10
        ml_decision.model_name = 'OptimalLookback'
        ml_decision.reasoning = 'Test reasoning'
        ml_decision.confidence = 0.95
        ml_decision.details = {'key': 'value'}
        
        ml_decisions = Mock()
        ml_decisions.decisions = [ml_decision]
        
        mock_data['ml_decisions'] = ml_decisions
        report_data = generator._prepare_report_data(**mock_data)
        
        assert report_data['ml_decisions'] is not None
        assert len(report_data['ml_decisions']['decisions']) == 1
        assert report_data['ml_decisions']['decisions'][0]['decision_type'] == 'lookback_period'
        assert report_data['ml_decisions']['decisions'][0]['confidence'] == 0.95