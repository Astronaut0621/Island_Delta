package com.islanddelta.controller;

import com.islanddelta.common.ApiResponse;
import com.islanddelta.dto.AdminLoginRequest;
import com.islanddelta.dto.AdminLoginResponse;
import com.islanddelta.service.AdminAuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
public class AdminAuthController {

    private final AdminAuthService authService;

    public AdminAuthController(AdminAuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AdminLoginResponse>> login(@Valid @RequestBody AdminLoginRequest request) {
        try {
            AdminLoginResponse response = authService.login(request);
            return ResponseEntity.ok(ApiResponse.ok("登录成功", response));
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.unauthorized(e.getMessage()));
        }
    }
}
