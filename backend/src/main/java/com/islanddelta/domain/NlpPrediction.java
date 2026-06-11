package com.islanddelta.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "nlp_predictions")
public class NlpPrediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "target_type", length = 32)
    private String targetType;

    @Column(name = "target_id")
    private Long targetId;

    @Column(name = "model_version", nullable = false, length = 64)
    private String modelVersion;

    @Column(name = "input_text", nullable = false, columnDefinition = "TEXT")
    private String inputText;

    @Column(name = "sentiment_prediction", length = 32)
    private String sentimentPrediction;

    @Column(name = "emotion_prediction", length = 32)
    private String emotionPrediction;

    @Column(name = "temperature_prediction")
    private Integer temperaturePrediction;

    @Column(name = "safety_prediction", length = 32)
    private String safetyPrediction;

    private BigDecimal confidence;

    @Column(name = "user_corrected", nullable = false)
    private Boolean userCorrected = false;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTargetType() { return targetType; }
    public void setTargetType(String targetType) { this.targetType = targetType; }

    public Long getTargetId() { return targetId; }
    public void setTargetId(Long targetId) { this.targetId = targetId; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public String getInputText() { return inputText; }
    public void setInputText(String inputText) { this.inputText = inputText; }

    public String getSentimentPrediction() { return sentimentPrediction; }
    public void setSentimentPrediction(String sentimentPrediction) { this.sentimentPrediction = sentimentPrediction; }

    public String getEmotionPrediction() { return emotionPrediction; }
    public void setEmotionPrediction(String emotionPrediction) { this.emotionPrediction = emotionPrediction; }

    public Integer getTemperaturePrediction() { return temperaturePrediction; }
    public void setTemperaturePrediction(Integer temperaturePrediction) { this.temperaturePrediction = temperaturePrediction; }

    public String getSafetyPrediction() { return safetyPrediction; }
    public void setSafetyPrediction(String safetyPrediction) { this.safetyPrediction = safetyPrediction; }

    public BigDecimal getConfidence() { return confidence; }
    public void setConfidence(BigDecimal confidence) { this.confidence = confidence; }

    public Boolean getUserCorrected() { return userCorrected; }
    public void setUserCorrected(Boolean userCorrected) { this.userCorrected = userCorrected; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
