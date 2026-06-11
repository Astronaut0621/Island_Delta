package com.islanddelta.controller;

import com.islanddelta.common.ApiResponse;
import com.islanddelta.dto.ReportDTO;
import com.islanddelta.service.AdminReportService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/reports")
public class AdminReportController {

    private final AdminReportService reportService;

    public AdminReportController(AdminReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping
    public ApiResponse<Page<ReportDTO>> listReports(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<ReportDTO> result = reportService.listReports(status, pageable);
        return ApiResponse.ok(result);
    }

    @PutMapping("/{id}/handle")
    public ApiResponse<ReportDTO> handleReport(@PathVariable Long id) {
        try {
            return ApiResponse.ok("举报已处理", reportService.handleReport(id));
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }

    @PutMapping("/{id}/ignore")
    public ApiResponse<ReportDTO> ignoreReport(@PathVariable Long id) {
        try {
            return ApiResponse.ok("举报已忽略", reportService.ignoreReport(id));
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }
}
