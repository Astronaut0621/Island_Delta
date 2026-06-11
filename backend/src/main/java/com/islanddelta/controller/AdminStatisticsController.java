package com.islanddelta.controller;

import com.islanddelta.common.ApiResponse;
import com.islanddelta.dto.StatisticsDTO;
import com.islanddelta.service.AdminStatisticsService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin/statistics")
public class AdminStatisticsController {

    private final AdminStatisticsService statisticsService;

    public AdminStatisticsController(AdminStatisticsService statisticsService) {
        this.statisticsService = statisticsService;
    }

    @GetMapping
    public ApiResponse<StatisticsDTO> getStatistics() {
        return ApiResponse.ok(statisticsService.getStatistics());
    }
}
