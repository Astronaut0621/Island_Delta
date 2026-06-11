package com.islanddelta.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record EmotionPostDTO(
    Long id,
    Long userId,
    String emotionType,
    String sentiment,
    Integer temperature,
    String temperatureBin,
    String content,
    BigDecimal latitude,
    BigDecimal longitude,
    String locationName,
    String visibility,
    Boolean allowReaction,
    String modelVersion,
    BigDecimal confidence,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    String status,
    Integer reportCount
) {}
