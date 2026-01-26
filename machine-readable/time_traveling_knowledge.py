"""
Time-Traveling Knowledge: Predicting Future Knowledge and Trends

This module implements a revolutionary system for temporal knowledge analysis:
- Analyze historical evolution of concepts and technologies
- Detect patterns and trends across time
- Extrapolate future states with confidence scores
- Causal modeling of knowledge evolution
- "Travel" through time to see how knowledge changes

The system acts as a "crystal ball" for knowledge, predicting not just what
will happen, but what we will KNOW in the future.

Level: 5 (ФУТУРИСТИЧЕСКОЕ)
Complexity: ⚫⚫ Extremely High
Timeline: 7-10 years
Reality: 20%
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import copy
import math
import statistics


class TrendType(Enum):
    """Types of trends in knowledge evolution"""
    EXPONENTIAL_GROWTH = "exponential_growth"  # Doubles every N years
    LINEAR_GROWTH = "linear_growth"  # Constant increment
    SIGMOID = "sigmoid"  # S-curve (slow → fast → plateau)
    CYCLICAL = "cyclical"  # Repeating patterns
    DISRUPTIVE = "disruptive"  # Sudden jumps
    CONVERGENCE = "convergence"  # Multiple concepts merging


class CausalFactorType(Enum):
    """Types of causal factors affecting knowledge evolution"""
    TECHNOLOGICAL = "technological"  # New tech enables new knowledge
    ECONOMIC = "economic"  # Funding, market forces
    SOCIAL = "social"  # Social acceptance, adoption
    REGULATORY = "regulatory"  # Laws, policies
    SCIENTIFIC = "scientific"  # Breakthrough discoveries
    ENVIRONMENTAL = "environmental"  # Physical constraints


@dataclass
class HistoricalDataPoint:
    """A single point in the historical trajectory of a concept"""
    year: int
    name: str
    metrics: Dict[str, Any]  # Quantitative metrics
    characteristics: List[str]  # Qualitative characteristics
    context: Dict[str, Any]  # Historical context


@dataclass
class DetectedTrend:
    """A trend detected in historical data"""
    trend_type: TrendType
    parameter: str  # Which parameter shows this trend
    growth_rate: float  # For exponential: multiplier, for linear: increment
    confidence: float  # 0.0 to 1.0
    description: str

    def apply(self, state: Dict[str, Any], years_forward: int) -> Dict[str, Any]:
        """Apply this trend to project forward"""
        new_state = copy.deepcopy(state)

        if self.parameter not in new_state:
            return new_state

        current_value = new_state[self.parameter]

        if self.trend_type == TrendType.EXPONENTIAL_GROWTH:
            # Exponential: value * (growth_rate ^ years)
            if isinstance(current_value, (int, float)):
                new_state[self.parameter] = current_value * (self.growth_rate ** years_forward)

        elif self.trend_type == TrendType.LINEAR_GROWTH:
            # Linear: value + (growth_rate * years)
            if isinstance(current_value, (int, float)):
                new_state[self.parameter] = current_value + (self.growth_rate * years_forward)

        elif self.trend_type == TrendType.SIGMOID:
            # S-curve: approaches asymptote
            if isinstance(current_value, (int, float)):
                # Sigmoid function with asymptote at 10x current value
                asymptote = current_value * 10
                x = years_forward / 10  # Normalize time
                sigmoid = asymptote / (1 + math.exp(-x))
                new_state[self.parameter] = sigmoid

        return new_state


@dataclass
class CausalFactor:
    """A causal factor that can affect knowledge evolution"""
    factor_type: CausalFactorType
    name: str
    trigger_year: Optional[int]  # When this factor becomes active
    impact: float  # -1.0 to 1.0 (negative = inhibits, positive = accelerates)
    affected_parameters: List[str]
    description: str

    def will_trigger(self, year: int) -> bool:
        """Check if this factor is active at given year"""
        if self.trigger_year is None:
            return True
        return year >= self.trigger_year

    def modify(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Modify state based on this causal factor"""
        new_state = copy.deepcopy(state)

        for param in self.affected_parameters:
            if param in new_state:
                value = new_state[param]
                if isinstance(value, (int, float)):
                    # Apply impact as percentage change
                    new_state[param] = value * (1 + self.impact)

        return new_state


@dataclass
class FuturePrediction:
    """A prediction of future knowledge state"""
    year: int
    concept: str
    predicted_state: Dict[str, Any]
    confidence: float
    reasoning: List[str]  # Why we think this will happen
    uncertainties: List[str]  # What could go wrong


class TrendAnalyzer:
    """Analyzes historical data to detect trends"""

    def detect_trends(self, trajectory: List[HistoricalDataPoint]) -> List[DetectedTrend]:
        """Detect trends in historical trajectory"""
        trends = []

        if len(trajectory) < 2:
            return trends

        # Analyze each metric for trends
        metrics_over_time = self._extract_metrics_over_time(trajectory)

        for metric_name, values in metrics_over_time.items():
            if not values or len(values) < 2:
                continue

            # Try to detect exponential growth
            exp_trend = self._detect_exponential(metric_name, values)
            if exp_trend:
                trends.append(exp_trend)

            # Try to detect linear growth
            lin_trend = self._detect_linear(metric_name, values)
            if lin_trend:
                trends.append(lin_trend)

        return trends

    def _extract_metrics_over_time(
        self,
        trajectory: List[HistoricalDataPoint]
    ) -> Dict[str, List[Tuple[int, float]]]:
        """Extract numeric metrics over time"""
        metrics = {}

        for point in trajectory:
            for metric_name, value in point.metrics.items():
                if isinstance(value, (int, float)):
                    if metric_name not in metrics:
                        metrics[metric_name] = []
                    metrics[metric_name].append((point.year, value))

        return metrics

    def _detect_exponential(
        self,
        metric_name: str,
        values: List[Tuple[int, float]]
    ) -> Optional[DetectedTrend]:
        """Detect exponential growth pattern"""
        if len(values) < 3:
            return None

        # Calculate ratios between consecutive values
        ratios = []
        for i in range(1, len(values)):
            prev_val = values[i-1][1]
            curr_val = values[i][1]
            if prev_val > 0 and curr_val > 0:
                ratio = curr_val / prev_val
                ratios.append(ratio)

        if not ratios:
            return None

        # Check if ratios are relatively consistent (exponential growth)
        avg_ratio = statistics.mean(ratios)
        if len(ratios) > 1:
            std_ratio = statistics.stdev(ratios)
            consistency = 1.0 - min(1.0, std_ratio / avg_ratio)
        else:
            consistency = 1.0

        # If ratio > 1.5 and consistent, it's exponential growth
        if avg_ratio > 1.5 and consistency > 0.6:
            return DetectedTrend(
                trend_type=TrendType.EXPONENTIAL_GROWTH,
                parameter=metric_name,
                growth_rate=avg_ratio,
                confidence=consistency,
                description=f"{metric_name} grows exponentially at ~{avg_ratio:.2f}x per period"
            )

        return None

    def _detect_linear(
        self,
        metric_name: str,
        values: List[Tuple[int, float]]
    ) -> Optional[DetectedTrend]:
        """Detect linear growth pattern"""
        if len(values) < 3:
            return None

        # Calculate increments between consecutive values
        increments = []
        for i in range(1, len(values)):
            prev_val = values[i-1][1]
            curr_val = values[i][1]
            increment = curr_val - prev_val
            increments.append(increment)

        if not increments:
            return None

        # Check if increments are relatively consistent (linear growth)
        avg_increment = statistics.mean(increments)

        if abs(avg_increment) < 0.01:  # Too small to be significant
            return None

        if len(increments) > 1:
            std_increment = statistics.stdev(increments)
            consistency = 1.0 - min(1.0, std_increment / abs(avg_increment))
        else:
            consistency = 1.0

        # If consistent increments
        if consistency > 0.6:
            return DetectedTrend(
                trend_type=TrendType.LINEAR_GROWTH,
                parameter=metric_name,
                growth_rate=avg_increment,
                confidence=consistency,
                description=f"{metric_name} grows linearly by ~{avg_increment:.2f} per period"
            )

        return None


class CausalModel:
    """Models causal factors affecting knowledge evolution"""

    def __init__(self):
        self.factors = []

    def identify_factors(self, concept: str, trajectory: List[HistoricalDataPoint]) -> List[CausalFactor]:
        """Identify causal factors affecting this concept"""
        factors = []

        # Analyze trajectory for evidence of causal factors
        # In real system, this would use sophisticated causal inference

        # Example: If we see sudden jumps, there might be breakthrough factor
        for i in range(1, len(trajectory)):
            prev = trajectory[i-1]
            curr = trajectory[i]

            # Check for discontinuities (breakthroughs)
            for metric in curr.metrics:
                if metric in prev.metrics:
                    prev_val = prev.metrics[metric]
                    curr_val = curr.metrics[metric]

                    if isinstance(prev_val, (int, float)) and isinstance(curr_val, (int, float)):
                        if prev_val > 0:
                            jump = curr_val / prev_val
                            if jump > 3.0:  # 3x jump = breakthrough
                                factors.append(CausalFactor(
                                    factor_type=CausalFactorType.TECHNOLOGICAL,
                                    name=f"Breakthrough in {metric}",
                                    trigger_year=curr.year,
                                    impact=0.5,
                                    affected_parameters=[metric],
                                    description=f"Major advancement observed at {curr.year}"
                                ))

        # Add generic factors that often affect technology evolution
        factors.append(CausalFactor(
            factor_type=CausalFactorType.ECONOMIC,
            name="Market demand growth",
            trigger_year=None,
            impact=0.2,
            affected_parameters=["adoption_rate", "investment"],
            description="Increasing market demand accelerates development"
        ))

        factors.append(CausalFactor(
            factor_type=CausalFactorType.SCIENTIFIC,
            name="Fundamental research breakthroughs",
            trigger_year=None,
            impact=0.3,
            affected_parameters=["capabilities", "efficiency"],
            description="Basic science advances enable new capabilities"
        ))

        return factors

    def add_factor(self, factor: CausalFactor):
        """Add a causal factor to the model"""
        self.factors.append(factor)


class TemporalKnowledgeAgent:
    """
    Agent that can "travel through time" to predict future knowledge

    This agent analyzes historical trajectories, detects patterns,
    and extrapolates to predict what we will know in the future.
    """

    def __init__(self):
        self.knowledge_history: Dict[str, List[HistoricalDataPoint]] = {}
        self.trend_analyzer = TrendAnalyzer()
        self.causal_model = CausalModel()
        self.current_year = 2026

    def add_historical_data(self, concept: str, datapoint: HistoricalDataPoint):
        """Add a historical data point for a concept"""
        if concept not in self.knowledge_history:
            self.knowledge_history[concept] = []
        self.knowledge_history[concept].append(datapoint)

        # Sort by year
        self.knowledge_history[concept].sort(key=lambda x: x.year)

    def analyze_trajectory(self, concept: str) -> List[HistoricalDataPoint]:
        """Analyze the historical trajectory of a concept"""
        if concept not in self.knowledge_history:
            return []

        trajectory = self.knowledge_history[concept]

        # Analyze patterns
        if len(trajectory) >= 2:
            years_between = []
            for i in range(1, len(trajectory)):
                years = trajectory[i].year - trajectory[i-1].year
                years_between.append(years)

            if years_between:
                avg_period = statistics.mean(years_between)
                print(f"Pattern: New generation every ~{avg_period:.1f} years")

        return trajectory

    def predict_future_knowledge(
        self,
        concept: str,
        years_ahead: int
    ) -> List[FuturePrediction]:
        """
        Predict how knowledge about this concept will evolve

        Args:
            concept: The concept to predict
            years_ahead: How many years into the future

        Returns:
            List of predictions for each future year
        """
        # Step 1: Get historical trajectory
        trajectory = self.analyze_trajectory(concept)

        if not trajectory:
            return []

        # Step 2: Detect trends
        trends = self.trend_analyzer.detect_trends(trajectory)

        # Step 3: Identify causal factors
        causal_factors = self.causal_model.identify_factors(concept, trajectory)

        # Step 4: Get current state (last known data point)
        current_state = trajectory[-1].metrics

        # Step 5: Extrapolate into future
        predictions = self.extrapolate(
            concept=concept,
            current_state=current_state,
            current_year=trajectory[-1].year,
            trends=trends,
            causal_factors=causal_factors,
            time_horizon=years_ahead
        )

        return predictions

    def extrapolate(
        self,
        concept: str,
        current_state: Dict[str, Any],
        current_year: int,
        trends: List[DetectedTrend],
        causal_factors: List[CausalFactor],
        time_horizon: int
    ) -> List[FuturePrediction]:
        """Extrapolate current state into the future"""

        predictions = []

        for year_offset in range(1, time_horizon + 1):
            # Start with current state
            predicted_state = copy.deepcopy(current_state)
            reasoning = []
            uncertainties = []

            # Apply trends
            for trend in trends:
                predicted_state = trend.apply(predicted_state, year_offset)
                reasoning.append(
                    f"Applied {trend.trend_type.value} trend to {trend.parameter} "
                    f"(confidence: {trend.confidence:.2f})"
                )

            # Apply causal factors
            future_year = current_year + year_offset
            for factor in causal_factors:
                if factor.will_trigger(future_year):
                    predicted_state = factor.modify(predicted_state)
                    reasoning.append(
                        f"Applied causal factor: {factor.name} "
                        f"(impact: {factor.impact:+.2f})"
                    )
                    if abs(factor.impact) > 0.3:
                        uncertainties.append(
                            f"High impact from {factor.name} - could vary significantly"
                        )

            # Calculate confidence (decreases with time)
            # Confidence = base_confidence * exp(-decay * years)
            base_confidence = statistics.mean([t.confidence for t in trends]) if trends else 0.5
            decay_rate = 0.1  # 10% confidence loss per year
            confidence = base_confidence * math.exp(-decay_rate * year_offset)

            # Add uncertainty for long-term predictions
            if year_offset > 5:
                uncertainties.append(
                    f"Long-term prediction ({year_offset} years) - high uncertainty"
                )
                confidence *= 0.8

            predictions.append(FuturePrediction(
                year=future_year,
                concept=concept,
                predicted_state=predicted_state,
                confidence=confidence,
                reasoning=reasoning,
                uncertainties=uncertainties
            ))

        return predictions

    def compare_predictions_with_reality(
        self,
        concept: str,
        predicted_year: int,
        actual_data: HistoricalDataPoint
    ) -> Dict[str, Any]:
        """
        Compare predictions with actual reality (for validation)

        This is how we learn if our predictions are accurate.
        """
        # Find prediction for that year
        trajectory = self.knowledge_history[concept]
        # Make prediction from earlier data
        earlier_trajectory = [p for p in trajectory if p.year < predicted_year]

        if not earlier_trajectory:
            return {"error": "No earlier data to make prediction from"}

        # Create a temporary agent with only earlier data
        temp_agent = TemporalKnowledgeAgent()
        for point in earlier_trajectory:
            temp_agent.add_historical_data(concept, point)

        years_ahead = predicted_year - earlier_trajectory[-1].year
        predictions = temp_agent.predict_future_knowledge(concept, years_ahead)

        if not predictions:
            return {"error": "Could not make prediction"}

        # Find prediction for the specific year
        target_prediction = None
        for pred in predictions:
            if pred.year == predicted_year:
                target_prediction = pred
                break

        if not target_prediction:
            return {"error": "No prediction for that year"}

        # Compare predicted vs actual
        comparison = {
            "predicted_year": predicted_year,
            "predicted_state": target_prediction.predicted_state,
            "actual_state": actual_data.metrics,
            "accuracy": {},
            "overall_accuracy": 0.0
        }

        # Calculate accuracy for each metric
        accuracies = []
        for metric in target_prediction.predicted_state:
            if metric in actual_data.metrics:
                pred_val = target_prediction.predicted_state[metric]
                actual_val = actual_data.metrics[metric]

                if isinstance(pred_val, (int, float)) and isinstance(actual_val, (int, float)):
                    if actual_val != 0:
                        error = abs(pred_val - actual_val) / actual_val
                        accuracy = max(0.0, 1.0 - error)
                        comparison["accuracy"][metric] = accuracy
                        accuracies.append(accuracy)

        if accuracies:
            comparison["overall_accuracy"] = statistics.mean(accuracies)

        return comparison

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "concepts_tracked": len(self.knowledge_history),
            "total_datapoints": sum(len(v) for v in self.knowledge_history.values()),
            "concepts": list(self.knowledge_history.keys())
        }


# ============================================================================
# DEMO
# ============================================================================

def demo():
    """Demonstrate time-traveling knowledge prediction"""

    print("=" * 80)
    print("TIME-TRAVELING KNOWLEDGE DEMO")
    print("Predicting the Future of Technology")
    print("=" * 80)
    print()

    agent = TemporalKnowledgeAgent()

    # Example: Mobile Networks Evolution (1G → 2G → 3G → 4G → 5G → 6G?)
    print("Case Study: Mobile Network Evolution")
    print("-" * 80)
    print()

    # Add historical data
    mobile_networks = [
        HistoricalDataPoint(
            year=1980,
            name="1G",
            metrics={"speed_kbps": 2.4, "generation": 1},
            characteristics=["Analog", "Voice only"],
            context={"adoption": "Limited", "coverage": "Urban only"}
        ),
        HistoricalDataPoint(
            year=1990,
            name="2G",
            metrics={"speed_kbps": 64, "generation": 2},
            characteristics=["Digital", "SMS", "Voice"],
            context={"adoption": "Growing", "coverage": "Suburban"}
        ),
        HistoricalDataPoint(
            year=2000,
            name="3G",
            metrics={"speed_kbps": 2000, "generation": 3},
            characteristics=["Mobile internet", "Video calls"],
            context={"adoption": "Mass market", "coverage": "Wide"}
        ),
        HistoricalDataPoint(
            year=2010,
            name="4G",
            metrics={"speed_kbps": 100000, "generation": 4},
            characteristics=["HD video", "Apps", "Cloud"],
            context={"adoption": "Ubiquitous", "coverage": "Extensive"}
        ),
        HistoricalDataPoint(
            year=2020,
            name="5G",
            metrics={"speed_kbps": 1000000, "generation": 5},
            characteristics=["IoT", "AR/VR", "Ultra-low latency"],
            context={"adoption": "Growing", "coverage": "Urban"}
        ),
    ]

    print("Historical Trajectory:")
    for point in mobile_networks:
        agent.add_historical_data("mobile_networks", point)
        speed_mbps = point.metrics["speed_kbps"] / 1000
        print(f"  {point.year}: {point.name} - {speed_mbps:.1f} Mbps - {', '.join(point.characteristics)}")
    print()

    # Analyze trajectory
    print("Trajectory Analysis:")
    trajectory = agent.analyze_trajectory("mobile_networks")
    print()

    # Detect trends
    print("Detected Trends:")
    trends = agent.trend_analyzer.detect_trends(trajectory)
    for trend in trends:
        print(f"  • {trend.description}")
        print(f"    Type: {trend.trend_type.value}, Confidence: {trend.confidence:.2%}")
    print()

    # Predict future
    print("🔮 Predicting the Future:")
    print("-" * 80)
    years_to_predict = 15
    predictions = agent.predict_future_knowledge("mobile_networks", years_to_predict)

    # Show predictions for specific years
    interesting_years = [2030, 2035, 2040]
    for pred in predictions:
        if pred.year in interesting_years:
            print(f"\n📅 Year {pred.year} Prediction:")
            print(f"   Confidence: {pred.confidence:.2%}")
            print(f"\n   Predicted State:")

            if "speed_kbps" in pred.predicted_state:
                speed_kbps = pred.predicted_state["speed_kbps"]
                speed_gbps = speed_kbps / 1_000_000
                generation = pred.predicted_state.get("generation", "?")
                print(f"     Generation: {generation:.0f}G")
                print(f"     Speed: {speed_gbps:.1f} Gbps")

                # Estimate use cases based on speed
                if speed_gbps > 100:
                    use_cases = ["Holographic communication", "Full brain-computer interface",
                                 "Quantum internet", "Consciousness upload"]
                elif speed_gbps > 10:
                    use_cases = ["Holographic displays", "Real-time brain imaging",
                                 "Global tactile internet", "Digital twins"]
                elif speed_gbps > 1:
                    use_cases = ["8K streaming", "Advanced AR/VR", "Autonomous vehicles",
                                 "Smart cities"]
                else:
                    use_cases = ["4K video", "IoT", "AR/VR"]

                print(f"     Estimated Use Cases: {', '.join(use_cases[:3])}")

            print(f"\n   Reasoning:")
            for reason in pred.reasoning[:3]:  # Show first 3
                print(f"     • {reason}")

            if pred.uncertainties:
                print(f"\n   Uncertainties:")
                for uncertainty in pred.uncertainties[:2]:  # Show first 2
                    print(f"     ⚠️  {uncertainty}")

    print("\n" + "=" * 80)
    print("VALIDATION: Testing Prediction Accuracy")
    print("=" * 80)
    print()

    # Test prediction accuracy by predicting 5G from earlier data
    print("Test: Predict 5G (2020) using only data up to 4G (2010)")
    print("-" * 80)

    comparison = agent.compare_predictions_with_reality(
        "mobile_networks",
        predicted_year=2020,
        actual_data=mobile_networks[4]  # 5G actual data
    )

    if "error" not in comparison:
        print(f"Predicted speed: {comparison['predicted_state']['speed_kbps']/1000:.0f} Mbps")
        print(f"Actual speed: {comparison['actual_state']['speed_kbps']/1000:.0f} Mbps")
        print(f"\nAccuracy per metric:")
        for metric, acc in comparison["accuracy"].items():
            print(f"  {metric}: {acc:.2%}")
        print(f"\nOverall accuracy: {comparison['overall_accuracy']:.2%}")
    print()

    # Statistics
    print("=" * 80)
    print("AGENT STATISTICS")
    print("=" * 80)
    stats = agent.get_statistics()
    print(f"Concepts tracked: {stats['concepts_tracked']}")
    print(f"Total datapoints: {stats['total_datapoints']}")
    print(f"Concepts: {', '.join(stats['concepts'])}")
    print()

    print("=" * 80)
    print("REVOLUTIONARY IMPLICATIONS")
    print("=" * 80)
    print("""
This Time-Traveling Knowledge system enables:

1. **Technology Forecasting**: Predict future tech with confidence scores
   - When will 6G arrive? What will it enable?
   - What are the next breakthroughs in AI, quantum computing, biotech?

2. **Strategic Planning**: Make informed decisions about the future
   - Companies: Where to invest R&D?
   - Governments: What infrastructure to build?
   - Individuals: What skills to learn?

3. **Risk Assessment**: Identify what could go wrong
   - Uncertainties in predictions
   - Alternative scenarios
   - Black swan events

4. **Trend Analysis**: Understand long-term patterns
   - Moore's Law, AI scaling laws
   - Demographic trends, climate trends
   - Economic cycles

5. **Knowledge Gap Identification**: See what we DON'T know yet
   - What knowledge is missing now but will exist in 2030?
   - What questions can't we answer today but will answer tomorrow?

Limitations:
- Black swan events (unpredictable disruptions)
- Paradigm shifts (completely new frameworks)
- Confidence decreases exponentially with time
- Multiple possible futures (prediction = probability distribution)

This is not fortune-telling - it's extrapolation based on patterns.
But patterns can break. The future is not determined.
    """)


if __name__ == "__main__":
    demo()
