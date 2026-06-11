package com.islanddelta.config;

import com.islanddelta.common.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;

@Component
@Order(2)
public class AdminAuthFilter implements Filter {

    private static final String ADMIN_PREFIX = "/api/admin/";
    private static final String LOGIN_PATH = "/api/admin/login";

    private final JwtUtil jwtUtil;
    private final ObjectMapper objectMapper;

    public AdminAuthFilter(JwtUtil jwtUtil, ObjectMapper objectMapper) {
        this.jwtUtil = jwtUtil;
        this.objectMapper = objectMapper;
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        String path = httpRequest.getRequestURI();

        if ("OPTIONS".equalsIgnoreCase(httpRequest.getMethod())) {
            chain.doFilter(request, response);
            return;
        }

        // Only intercept admin API paths (excluding login)
        if (path.startsWith(ADMIN_PREFIX) && !path.equals(LOGIN_PATH)) {
            String authHeader = httpRequest.getHeader("Authorization");
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                writeUnauthorized(response, "未登录或Token已过期");
                return;
            }

            String token = authHeader.substring(7);
            if (!jwtUtil.validate(token)) {
                writeUnauthorized(response, "Token无效或已过期");
                return;
            }
        }

        chain.doFilter(request, response);
    }

    private void writeUnauthorized(ServletResponse response, String message) throws IOException {
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        httpResponse.setContentType("application/json;charset=UTF-8");
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("code", 401);
        body.put("message", message);
        body.put("data", null);
        httpResponse.getWriter().write(objectMapper.writeValueAsString(body));
    }
}
