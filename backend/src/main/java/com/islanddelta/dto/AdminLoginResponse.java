package com.islanddelta.dto;

public record AdminLoginResponse(
    String token,
    String username,
    String role
) {}
