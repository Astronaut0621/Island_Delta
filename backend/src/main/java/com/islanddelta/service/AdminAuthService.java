package com.islanddelta.service;

import com.islanddelta.common.JwtUtil;
import com.islanddelta.common.PasswordUtil;
import com.islanddelta.dto.AdminLoginRequest;
import com.islanddelta.dto.AdminLoginResponse;
import com.islanddelta.domain.Admin;
import com.islanddelta.repository.AdminRepository;
import org.springframework.stereotype.Service;

@Service
public class AdminAuthService {

    private final AdminRepository adminRepository;
    private final JwtUtil jwtUtil;

    public AdminAuthService(AdminRepository adminRepository, JwtUtil jwtUtil) {
        this.adminRepository = adminRepository;
        this.jwtUtil = jwtUtil;
    }

    public AdminLoginResponse login(AdminLoginRequest request) {
        Admin admin = adminRepository.findByUsername(request.username())
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));

        if (!PasswordUtil.matches(request.password(), admin.getPasswordHash())) {
            throw new RuntimeException("用户名或密码错误");
        }

        if ("disabled".equals(admin.getStatus())) {
            throw new RuntimeException("账号已被禁用");
        }

        String token = jwtUtil.generateToken(admin.getId(), admin.getUsername(), admin.getRole());
        return new AdminLoginResponse(token, admin.getUsername(), admin.getRole());
    }
}
