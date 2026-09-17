from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .sampling_heuristic_config_pool_size import SamplingHeuristicConfig_poolSize

@dataclass
class SamplingHeuristicConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # When true, heuristic sampling falls back to random on timeout instead of raising an error. Set by the orchestrator when strategy=AUTO.
    allow_timeout_fallback: Optional[bool] = False
    # Max CASE WHEN expressions per subquery chunk (avoids HANA parse-tree depth limit).
    chunk_size: Optional[int] = 100
    # Column count above which chunked SQL is used instead of a flat query.
    chunk_threshold: Optional[int] = 150
    # Day window for fuzzy date matching. A date column scores 1 if abs(DAYS_BETWEEN(row_date, query_date)) <= dateFuzzyDays. Set to 0 for exact date match.
    fuzzy_date_days: Optional[int] = 30
    # Numeric fuzzy threshold as a fraction of the absolute query value. E.g. 0.1 = +/-10%.
    fuzzy_num_pct: Optional[float] = 0.1
    # Fraction of numRows filled by scoring method (remainder is random fill). Must be between 0 and 1.
    method_ratio: Optional[float] = 0.67
    # If set, scoring runs against a random subsample of this many rows instead of the full table. None = full table scan.
    pool_size: Optional[SamplingHeuristicConfig_poolSize] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SamplingHeuristicConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SamplingHeuristicConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SamplingHeuristicConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .sampling_heuristic_config_pool_size import SamplingHeuristicConfig_poolSize

        from .sampling_heuristic_config_pool_size import SamplingHeuristicConfig_poolSize

        fields: dict[str, Callable[[Any], None]] = {
            "allowTimeoutFallback": lambda n : setattr(self, 'allow_timeout_fallback', n.get_bool_value()),
            "chunkSize": lambda n : setattr(self, 'chunk_size', n.get_int_value()),
            "chunkThreshold": lambda n : setattr(self, 'chunk_threshold', n.get_int_value()),
            "fuzzyDateDays": lambda n : setattr(self, 'fuzzy_date_days', n.get_int_value()),
            "fuzzyNumPct": lambda n : setattr(self, 'fuzzy_num_pct', n.get_float_value()),
            "methodRatio": lambda n : setattr(self, 'method_ratio', n.get_float_value()),
            "poolSize": lambda n : setattr(self, 'pool_size', n.get_object_value(SamplingHeuristicConfig_poolSize)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_bool_value("allowTimeoutFallback", self.allow_timeout_fallback)
        writer.write_int_value("chunkSize", self.chunk_size)
        writer.write_int_value("chunkThreshold", self.chunk_threshold)
        writer.write_int_value("fuzzyDateDays", self.fuzzy_date_days)
        writer.write_float_value("fuzzyNumPct", self.fuzzy_num_pct)
        writer.write_float_value("methodRatio", self.method_ratio)
        writer.write_object_value("poolSize", self.pool_size)
        writer.write_additional_data_value(self.additional_data)
    

