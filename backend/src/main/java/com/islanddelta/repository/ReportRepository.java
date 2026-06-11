package com.islanddelta.repository;

import com.islanddelta.domain.Report;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface ReportRepository extends JpaRepository<Report, Long>,
        JpaSpecificationExecutor<Report> {

    long countByStatus(String status);
}
