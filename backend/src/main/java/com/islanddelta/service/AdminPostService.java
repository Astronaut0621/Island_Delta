package com.islanddelta.service;

import com.islanddelta.domain.EmotionPost;
import com.islanddelta.dto.EmotionPostDTO;
import com.islanddelta.repository.EmotionPostRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class AdminPostService {

    private final EmotionPostRepository postRepository;

    public AdminPostService(EmotionPostRepository postRepository) {
        this.postRepository = postRepository;
    }

    public Page<EmotionPostDTO> listPosts(String status, String emotionType,
                                           LocalDateTime startTime, LocalDateTime endTime,
                                           Pageable pageable) {
        Specification<EmotionPost> spec = Specification.where(null);

        if (status != null && !status.isEmpty()) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("status"), status));
        }
        if (emotionType != null && !emotionType.isEmpty()) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("emotionType"), emotionType));
        }
        if (startTime != null) {
            spec = spec.and((root, query, cb) -> cb.greaterThanOrEqualTo(root.get("createdAt"), startTime));
        }
        if (endTime != null) {
            spec = spec.and((root, query, cb) -> cb.lessThanOrEqualTo(root.get("createdAt"), endTime));
        }

        return postRepository.findAll(spec, pageable)
                .map(this::toDTO);
    }

    public EmotionPostDTO getPost(Long id) {
        EmotionPost post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("情绪记录不存在"));
        return toDTO(post);
    }

    @Transactional
    public EmotionPostDTO hidePost(Long id) {
        EmotionPost post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("情绪记录不存在"));
        post.setStatus("hidden");
        postRepository.save(post);
        return toDTO(post);
    }

    @Transactional
    public EmotionPostDTO restorePost(Long id) {
        EmotionPost post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("情绪记录不存在"));
        post.setStatus("normal");
        postRepository.save(post);
        return toDTO(post);
    }

    @Transactional
    public void deletePost(Long id) {
        EmotionPost post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("情绪记录不存在"));
        post.setStatus("deleted");
        postRepository.save(post);
    }

    private EmotionPostDTO toDTO(EmotionPost post) {
        return new EmotionPostDTO(
                post.getId(),
                post.getUserId(),
                post.getEmotionType(),
                post.getSentiment(),
                post.getTemperature(),
                post.getTemperatureBin(),
                post.getContent(),
                post.getLatitude(),
                post.getLongitude(),
                post.getLocationName(),
                post.getVisibility(),
                post.getAllowReaction(),
                post.getModelVersion(),
                post.getConfidence(),
                post.getCreatedAt(),
                post.getUpdatedAt(),
                post.getStatus(),
                post.getReportCount()
        );
    }
}
