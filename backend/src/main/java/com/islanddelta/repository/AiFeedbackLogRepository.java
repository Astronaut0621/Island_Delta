package com.islanddelta.repository;

import com.islanddelta.domain.AiFeedbackLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface AiFeedbackLogRepository extends JpaRepository<AiFeedbackLog, Long>,
        JpaSpecificationExecutor<AiFeedbackLog> {
}
