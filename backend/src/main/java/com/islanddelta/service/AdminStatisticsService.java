package com.islanddelta.service;

import com.islanddelta.domain.EmotionPost;
import com.islanddelta.domain.Location;
import com.islanddelta.dto.StatisticsDTO;
import com.islanddelta.repository.EmotionPostRepository;
import com.islanddelta.repository.LocationRepository;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AdminStatisticsService {

    private final EmotionPostRepository postRepository;
    private final LocationRepository locationRepository;

    public AdminStatisticsService(EmotionPostRepository postRepository, LocationRepository locationRepository) {
        this.postRepository = postRepository;
        this.locationRepository = locationRepository;
    }

    public StatisticsDTO getStatistics() {
        long totalPosts = postRepository.count();

        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        Specification<EmotionPost> todaySpec = (root, query, cb) ->
                cb.greaterThanOrEqualTo(root.get("createdAt"), todayStart);
        long todayPosts = postRepository.count(todaySpec);

        // Average temperature of all normal posts
        BigDecimal avgTemperature = BigDecimal.ZERO;
        List<EmotionPost> normalPosts = postRepository.findByStatus("normal");
        if (!normalPosts.isEmpty()) {
            double avg = normalPosts.stream()
                    .mapToInt(EmotionPost::getTemperature)
                    .average()
                    .orElse(0.0);
            avgTemperature = BigDecimal.valueOf(avg).setScale(1, RoundingMode.HALF_UP);
        }

        // Coldest and warmest locations
        String coldestLocation = locationRepository.findAll().stream()
                .filter(l -> l.getAvgTemperature() != null)
                .min(Comparator.comparing(Location::getAvgTemperature))
                .map(l -> l.getName())
                .orElse("暂无数据");

        String warmestLocation = locationRepository.findAll().stream()
                .filter(l -> l.getAvgTemperature() != null)
                .max(Comparator.comparing(Location::getAvgTemperature))
                .map(l -> l.getName())
                .orElse("暂无数据");

        // Top emotion tags
        Map<String, Long> emotionCounts = normalPosts.stream()
                .collect(Collectors.groupingBy(EmotionPost::getEmotionType, Collectors.counting()));
        List<StatisticsDTO.EmotionTagCount> topTags = emotionCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(10)
                .map(e -> new StatisticsDTO.EmotionTagCount(e.getKey(), e.getValue()))
                .collect(Collectors.toList());

        // Recent trend (last 7 days)
        List<StatisticsDTO.DailyTrendItem> recentTrend = new ArrayList<>();
        for (int i = 6; i >= 0; i--) {
            LocalDate date = LocalDate.now().minusDays(i);
            LocalDateTime dayStart = date.atStartOfDay();
            LocalDateTime dayEnd = date.atTime(LocalTime.MAX);
            Specification<EmotionPost> daySpec = (root, query, cb) ->
                    cb.between(root.get("createdAt"), dayStart, dayEnd);
            long dayCount = postRepository.count(daySpec);

            List<EmotionPost> dayPosts = postRepository.findAll(daySpec);
            BigDecimal dayAvg = BigDecimal.ZERO;
            if (!dayPosts.isEmpty()) {
                dayAvg = BigDecimal.valueOf(
                        dayPosts.stream().mapToInt(EmotionPost::getTemperature).average().orElse(0.0)
                ).setScale(1, RoundingMode.HALF_UP);
            }
            recentTrend.add(new StatisticsDTO.DailyTrendItem(date.toString(), dayCount, dayAvg));
        }

        return new StatisticsDTO(totalPosts, todayPosts, avgTemperature,
                coldestLocation, warmestLocation, topTags, recentTrend);
    }
}
