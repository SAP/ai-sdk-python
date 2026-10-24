"""
Granite Guardian 4.1 Content Filter Model
"""

from typing import Optional

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel


class GraniteGuardian41Categories(BaseModel):
    """
    Content criteria to evaluate.

    Note: Granite Guardian requires separate calls for each configured content category.
    Recommendation: Use only the ``harm`` catch-all content category.

    Args:
        harm: Catch-all criterion for generally harmful content.

        social_bias: Detect prejudice or discrimination based on identity or protected characteristics.

        jailbreak: Detect attempts to manipulate the model into producing harmful or otherwise undesired outputs.

        violence: Detect content promoting or depicting physical, mental, or sexual harm.

        profanity: Detect offensive language or insults.

        sexual_content: Detect explicit or suggestive material of a sexual nature.

        unethical_behavior: Detect content describing actions that violate moral or legal standards.
    """

    harm: bool = False
    social_bias: bool = False
    jailbreak: bool = False
    violence: bool = False
    profanity: bool = False
    sexual_content: bool = False
    unethical_behavior: bool = False


class GraniteGuardian41Filter(BaseModel):
    """
    Configuration for the IBM Granite Guardian 4.1 filter provider.

    Args:
        enable_reasoning: Enable reasoning (think) mode for Granite Guardian. Applies to every configured
            category. Returns reasoning content when enabled, e.g.
            ``'harm': {'verdict': true, 'reasoning': '...'}``.

        categories: Content criteria to evaluate.
    """

    enable_reasoning: Optional[bool] = False
    categories: GraniteGuardian41Categories


__all__ = ["GraniteGuardian41Categories", "GraniteGuardian41Filter"]
