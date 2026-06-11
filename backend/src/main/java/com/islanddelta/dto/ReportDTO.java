package com.islanddelta.dto;

import java.time.LocalDateTime;

public record ReportDTO(
    Long id,
    Long postId,
    Long userId,
    String reason,
    String detail,
    LocalDateTime createdAt,
    String status,
    // Associated post info
    String postContent,
    String postEmotionType,
    Integer postTemperature,
    String postLocationName,
    String postStatus
) {}
