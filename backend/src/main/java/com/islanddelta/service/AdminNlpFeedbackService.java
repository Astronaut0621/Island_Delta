package com.islanddelta.service;

import com.islanddelta.domain.AiFeedbackLog;
import com.islanddelta.domain.NlpPrediction;
import com.islanddelta.dto.NlpFeedbackDTO;
import com.islanddelta.repository.AiFeedbackLogRepository;
import com.islanddelta.repository.NlpPredictionRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

@Service
public class AdminNlpFeedbackService {

    private final NlpPredictionRepository predictionRepository;
    private final AiFeedbackLogRepository feedbackLogRepository;

    public AdminNlpFeedbackService(NlpPredictionRepository predictionRepository,
                                    AiFeedbackLogRepository feedbackLogRepository) {
        this.predictionRepository = predictionRepository;
        this.feedbackLogRepository = feedbackLogRepository;
    }

    public Page<NlpFeedbackDTO> listFeedback(Boolean userCorrected, Pageable pageable) {
        Specification<NlpPrediction> spec = Specification.where(null);

        if (userCorrected != null) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("userCorrected"), userCorrected));
        }

        return predictionRepository.findAll(spec, pageable)
                .map(this::toDTO);
    }

    public long getTotalPredictions() {
        return predictionRepository.count();
    }

    public long getCorrectedCount() {
        Specification<NlpPrediction> spec = (root, query, cb) ->
                cb.equal(root.get("userCorrected"), true);
        return predictionRepository.count(spec);
    }

    public double getAcceptanceRate() {
        long total = predictionRepository.count();
        if (total == 0) return 0.0;
        long corrected = getCorrectedCount();
        return (double) (total - corrected) / total * 100;
    }

    private NlpFeedbackDTO toDTO(NlpPrediction prediction) {
        // Find corresponding feedback log
        String correctedEmotion = null;
        Integer correctedTemperature = null;
        Boolean accepted = !prediction.getUserCorrected();

        if (prediction.getUserCorrected()) {
            Specification<AiFeedbackLog> spec = (root, query, cb) ->
                    cb.equal(root.get("predictionId"), prediction.getId());
            var feedbacks = feedbackLogRepository.findAll(spec);
            if (!feedbacks.isEmpty()) {
                AiFeedbackLog feedback = feedbacks.get(0);
                correctedEmotion = feedback.getCorrectedEmotion();
                correctedTemperature = feedback.getCorrectedTemperature();
                accepted = feedback.getAccepted();
            }
        }

        return new NlpFeedbackDTO(
                prediction.getId(),
                prediction.getInputText(),
                prediction.getModelVersion(),
                prediction.getEmotionPrediction(),
                prediction.getSentimentPrediction(),
                prediction.getTemperaturePrediction(),
                prediction.getSafetyPrediction(),
                prediction.getConfidence(),
                prediction.getUserCorrected(),
                correctedEmotion,
                correctedTemperature,
                accepted,
                prediction.getCreatedAt()
        );
    }
}
