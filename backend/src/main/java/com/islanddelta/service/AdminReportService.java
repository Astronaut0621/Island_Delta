package com.islanddelta.service;

import com.islanddelta.domain.EmotionPost;
import com.islanddelta.domain.Report;
import com.islanddelta.dto.ReportDTO;
import com.islanddelta.repository.EmotionPostRepository;
import com.islanddelta.repository.ReportRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AdminReportService {

    private final ReportRepository reportRepository;
    private final EmotionPostRepository postRepository;

    public AdminReportService(ReportRepository reportRepository, EmotionPostRepository postRepository) {
        this.reportRepository = reportRepository;
        this.postRepository = postRepository;
    }

    public Page<ReportDTO> listReports(String status, Pageable pageable) {
        Specification<Report> spec = Specification.where(null);

        if (status != null && !status.isEmpty()) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("status"), status));
        }

        return reportRepository.findAll(spec, pageable)
                .map(this::toDTO);
    }

    @Transactional
    public ReportDTO handleReport(Long id) {
        Report report = reportRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("举报记录不存在"));
        report.setStatus("handled");
        reportRepository.save(report);

        // Also hide the associated post
        EmotionPost post = postRepository.findById(report.getPostId()).orElse(null);
        if (post != null) {
            post.setStatus("hidden");
            postRepository.save(post);
        }

        return toDTO(report);
    }

    @Transactional
    public ReportDTO ignoreReport(Long id) {
        Report report = reportRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("举报记录不存在"));
        report.setStatus("ignored");
        reportRepository.save(report);
        return toDTO(report);
    }

    private ReportDTO toDTO(Report report) {
        // Fetch associated post info
        String postContent = null;
        String postEmotionType = null;
        Integer postTemperature = null;
        String postLocationName = null;
        String postStatus = null;

        EmotionPost post = postRepository.findById(report.getPostId()).orElse(null);
        if (post != null) {
            postContent = post.getContent();
            postEmotionType = post.getEmotionType();
            postTemperature = post.getTemperature();
            postLocationName = post.getLocationName();
            postStatus = post.getStatus();
        }

        return new ReportDTO(
                report.getId(),
                report.getPostId(),
                report.getUserId(),
                report.getReason(),
                report.getDetail(),
                report.getCreatedAt(),
                report.getStatus(),
                postContent,
                postEmotionType,
                postTemperature,
                postLocationName,
                postStatus
        );
    }
}
