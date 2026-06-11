package com.islanddelta.dto;

import java.math.BigDecimal;

public record StatisticsDTO(
    long totalPosts,
    long todayPosts,
    BigDecimal avgTemperature,
    String coldestLocation,
    String warmestLocation,
    java.util.List<EmotionTagCount> topEmotionTags,
    java.util.List<DailyTrendItem> recentTrend
) {
    public record EmotionTagCount(String emotionType, long count) {}
    public record DailyTrendItem(String date, long count, BigDecimal avgTemperature) {}
}
