package com.islanddelta.repository;

import com.islanddelta.domain.NlpPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface NlpPredictionRepository extends JpaRepository<NlpPrediction, Long>,
        JpaSpecificationExecutor<NlpPrediction> {
}
