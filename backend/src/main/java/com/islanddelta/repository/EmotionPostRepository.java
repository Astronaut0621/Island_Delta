package com.islanddelta.repository;

import com.islanddelta.domain.EmotionPost;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import java.util.List;

public interface EmotionPostRepository extends JpaRepository<EmotionPost, Long>,
        JpaSpecificationExecutor<EmotionPost> {

    List<EmotionPost> findByStatus(String status);
    long countByStatus(String status);
}
