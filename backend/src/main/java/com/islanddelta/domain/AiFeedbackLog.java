package com.islanddelta.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "ai_feedback_logs")
public class AiFeedbackLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "prediction_id", nullable = false)
    private Long predictionId;

    @Column(name = "original_emotion", length = 32)
    private String originalEmotion;

    @Column(name = "corrected_emotion", length = 32)
    private String correctedEmotion;

    @Column(name = "original_temperature")
    private Integer originalTemperature;

    @Column(name = "corrected_temperature")
    private Integer correctedTemperature;

    @Column(nullable = false)
    private Boolean accepted;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public Long getPredictionId() { return predictionId; }
    public void setPredictionId(Long predictionId) { this.predictionId = predictionId; }

    public String getOriginalEmotion() { return originalEmotion; }
    public void setOriginalEmotion(String originalEmotion) { this.originalEmotion = originalEmotion; }

    public String getCorrectedEmotion() { return correctedEmotion; }
    public void setCorrectedEmotion(String correctedEmotion) { this.correctedEmotion = correctedEmotion; }

    public Integer getOriginalTemperature() { return originalTemperature; }
    public void setOriginalTemperature(Integer originalTemperature) { this.originalTemperature = originalTemperature; }

    public Integer getCorrectedTemperature() { return correctedTemperature; }
    public void setCorrectedTemperature(Integer correctedTemperature) { this.correctedTemperature = correctedTemperature; }

    public Boolean getAccepted() { return accepted; }
    public void setAccepted(Boolean accepted) { this.accepted = accepted; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
