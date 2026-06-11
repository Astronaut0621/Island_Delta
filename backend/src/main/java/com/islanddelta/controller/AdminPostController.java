package com.islanddelta.controller;

import com.islanddelta.common.ApiResponse;
import com.islanddelta.dto.EmotionPostDTO;
import com.islanddelta.service.AdminPostService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/admin/posts")
public class AdminPostController {

    private final AdminPostService postService;

    public AdminPostController(AdminPostService postService) {
        this.postService = postService;
    }

    @GetMapping
    public ApiResponse<Page<EmotionPostDTO>> listPosts(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String emotionType,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<EmotionPostDTO> result = postService.listPosts(status, emotionType, startTime, endTime, pageable);
        return ApiResponse.ok(result);
    }

    @GetMapping("/{id}")
    public ApiResponse<EmotionPostDTO> getPost(@PathVariable Long id) {
        try {
            return ApiResponse.ok(postService.getPost(id));
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }

    @PutMapping("/{id}/hide")
    public ApiResponse<EmotionPostDTO> hidePost(@PathVariable Long id) {
        try {
            return ApiResponse.ok("内容已隐藏", postService.hidePost(id));
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }

    @PutMapping("/{id}/restore")
    public ApiResponse<EmotionPostDTO> restorePost(@PathVariable Long id) {
        try {
            return ApiResponse.ok("内容已恢复", postService.restorePost(id));
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> deletePost(@PathVariable Long id) {
        try {
            postService.deletePost(id);
            return ApiResponse.ok("内容已删除", null);
        } catch (RuntimeException e) {
            return ApiResponse.notFound(e.getMessage());
        }
    }
}
