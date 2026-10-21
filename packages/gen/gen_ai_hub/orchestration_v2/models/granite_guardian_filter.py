"""
Granite Guardian 4.1 Content Filter Model
"""

from typing import Optional

from pydantic import model_validator

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

    harm: Optional[bool] = None
    social_bias: Optional[bool] = None
    jailbreak: Optional[bool] = None
    violence: Optional[bool] = None
    profanity: Optional[bool] = None
    sexual_content: Optional[bool] = None
    unethical_behavior: Optional[bool] = None

    @model_validator(mode="after")
    def enforce_min_categories(self):
        """
        Ensure at least one category is specified.
        """
        if all(getattr(self, name) is None for name in self.__class__.model_fields):
            raise ValueError("GraniteGuardian41Categories must specify at least one category.")
        return self


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
