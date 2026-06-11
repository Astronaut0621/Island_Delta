package com.islanddelta.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "emotion_posts")
public class EmotionPost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "emotion_type", nullable = false, length = 32)
    private String emotionType;

    @Column(length = 32)
    private String sentiment;

    @Column(nullable = false)
    private Integer temperature;

    @Column(name = "temperature_bin", length = 32)
    private String temperatureBin;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    private BigDecimal latitude;

    private BigDecimal longitude;

    @Column(name = "location_grid", length = 64)
    private String locationGrid;

    @Column(name = "location_name", length = 128)
    private String locationName;

    @Column(nullable = false, length = 32)
    private String visibility = "public";

    @Column(name = "allow_reaction", nullable = false)
    private Boolean allowReaction = true;

    @Column(name = "model_version", length = 64)
    private String modelVersion;

    private BigDecimal confidence;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(nullable = false, length = 32)
    private String status = "normal";

    @Column(name = "report_count", nullable = false)
    private Integer reportCount = 0;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getEmotionType() { return emotionType; }
    public void setEmotionType(String emotionType) { this.emotionType = emotionType; }

    public String getSentiment() { return sentiment; }
    public void setSentiment(String sentiment) { this.sentiment = sentiment; }

    public Integer getTemperature() { return temperature; }
    public void setTemperature(Integer temperature) { this.temperature = temperature; }

    public String getTemperatureBin() { return temperatureBin; }
    public void setTemperatureBin(String temperatureBin) { this.temperatureBin = temperatureBin; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public BigDecimal getLatitude() { return latitude; }
    public void setLatitude(BigDecimal latitude) { this.latitude = latitude; }

    public BigDecimal getLongitude() { return longitude; }
    public void setLongitude(BigDecimal longitude) { this.longitude = longitude; }

    public String getLocationGrid() { return locationGrid; }
    public void setLocationGrid(String locationGrid) { this.locationGrid = locationGrid; }

    public String getLocationName() { return locationName; }
    public void setLocationName(String locationName) { this.locationName = locationName; }

    public String getVisibility() { return visibility; }
    public void setVisibility(String visibility) { this.visibility = visibility; }

    public Boolean getAllowReaction() { return allowReaction; }
    public void setAllowReaction(Boolean allowReaction) { this.allowReaction = allowReaction; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public BigDecimal getConfidence() { return confidence; }
    public void setConfidence(BigDecimal confidence) { this.confidence = confidence; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Integer getReportCount() { return reportCount; }
    public void setReportCount(Integer reportCount) { this.reportCount = reportCount; }
}
