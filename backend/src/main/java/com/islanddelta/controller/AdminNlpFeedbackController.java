package com.islanddelta.controller;

import com.islanddelta.common.ApiResponse;
import com.islanddelta.dto.NlpFeedbackDTO;
import com.islanddelta.service.AdminNlpFeedbackService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/nlp-feedback")
public class AdminNlpFeedbackController {

    private final AdminNlpFeedbackService nlpFeedbackService;

    public AdminNlpFeedbackController(AdminNlpFeedbackService nlpFeedbackService) {
        this.nlpFeedbackService = nlpFeedbackService;
    }

    @GetMapping
    public ApiResponse<Page<NlpFeedbackDTO>> listFeedback(
            @RequestParam(required = false) Boolean userCorrected,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<NlpFeedbackDTO> result = nlpFeedbackService.listFeedback(userCorrected, pageable);
        return ApiResponse.ok(result);
    }

    @GetMapping("/acceptance-rate")
    public ApiResponse<Map<String, Object>> getAcceptanceRate() {
        double rate = nlpFeedbackService.getAcceptanceRate();
        long total = nlpFeedbackService.getTotalPredictions();
        long corrected = nlpFeedbackService.getCorrectedCount();
        return ApiResponse.ok(Map.of(
                "acceptanceRate", rate,
                "totalPredictions", total,
                "correctedCount", corrected
        ));
    }
}
