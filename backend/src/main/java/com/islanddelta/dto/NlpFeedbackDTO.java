package com.islanddelta.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record NlpFeedbackDTO(
    Long predictionId,
    String inputText,
    String modelVersion,
    String emotionPrediction,
    String sentimentPrediction,
    Integer temperaturePrediction,
    String safetyPrediction,
    BigDecimal confidence,
    Boolean userCorrected,
    String correctedEmotion,
    Integer correctedTemperature,
    Boolean accepted,
    LocalDateTime createdAt
) {}
